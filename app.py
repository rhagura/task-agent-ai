import streamlit as st
import os
import requests
from dotenv import load_dotenv
from langchain_google_vertexai import ChatVertexAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 環境変数の読み込み
load_dotenv()

st.set_page_config(page_title="Task Agent AI", page_icon="🤖", layout="wide")

# --- 1. Notion書き込みツールの定義 ---
@tool
def create_notion_task(title: str, date: str):
    """Notionのデータベースに新しいタスクを記録します。
    Args:
        title: タスクの内容（例：日報作成、会議の振り返り）
        date: 予定日（YYYY-MM-DD形式）
    """
    NOTION_TOKEN = os.getenv("NOTION_API_SECRET")
    DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # ※Notionのデータベースの列名（名前、日付）が一致しているか確認してください
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "名前": {"title": [{"text": {"content": title}}]},
            "日付": {"date": {"start": date}}
        }
    }
    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    if response.status_code == 200:
        return f"✅ Notionに「{title}」を記録しました！"
    else:
        return f"❌ Notionエラー: {response.text}"

# --- 2. カレンダー・AIのセットアップ ---
def get_calendar_events():
    # (以前の get_calendar_events 関数と中身は同じです)
    if not os.path.exists('token.json'): return "カレンダー未認証です"
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar.readonly'])
    service = build('calendar', 'v3', credentials=creds)
    events_result = service.events().list(calendarId='primary', maxResults=5).execute()
    events = events_result.get('items', [])
    return "\n".join([f"{e.get('summary')} ({e.get('start').get('dateTime')})" for e in events])

# AIモデルの設定（安定した us-central1 / 2.5-flash）
llm = ChatVertexAI(
    model_name="gemini-2.5-flash", 
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location="us-central1"
)
# AIにツールをバインド
tools = [create_notion_task]
llm_with_tools = llm.bind_tools(tools)

# --- 3. UIとチャットロジック ---
st.title("🤖 Task Agent AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 2. チャットロジックの修正（複数呼び出し対応） ---
if prompt := st.chat_input("例：今日の予定を全部Notionに登録して"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("エージェントが実行中..."):
            calendar_info = get_calendar_events()
            
            # AIへのメッセージ履歴を構築
            history = [HumanMessage(content=f"カレンダー予定:\n{calendar_info}\n\n依頼: {prompt}")]
            ai_msg = llm_with_tools.invoke(history)
            history.append(ai_msg) # AIの回答（ツール呼び出し指令）を履歴に追加

            if ai_msg.tool_calls:
                # すべてのツール呼び出しに対してループで実行
                for tool_call in ai_msg.tool_calls:
                    result = create_notion_task.invoke(tool_call["args"])
                    st.success(result)
                    # 実行結果を ToolMessage として履歴に追加
                    history.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))
                
                # すべての結果を揃えてから AI に最終回答を求める [cite: 81]
                final_response = llm.invoke(history)
                st.write(final_response.content)
                st.session_state.messages.append({"role": "assistant", "content": final_response.content})
            else:
                st.write(ai_msg.content)
                st.session_state.messages.append({"role": "assistant", "content": ai_msg.content})