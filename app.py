import streamlit as st
import os

# ページ設定
st.set_page_config(
    page_title="Task Agent AI",
    page_icon="🤖",
    layout="wide"
)

# サイドバー（ここに将来カレンダーが出る）
with st.sidebar:
    st.header("📅 今日の予定")
    st.write("（ここにカレンダー連携機能が入ります）")
    
    # デバッグ用：環境変数の確認
    if st.checkbox("Show Debug Info"):
        st.write(f"Project ID: {os.environ.get('GOOGLE_CLOUD_PROJECT', 'Local')}")

# メインエリア（チャット画面）
st.title("🤖 Task Agent AI")
st.write("過集中を防ぎ、あなたをマネジメントするAIパートナーです。")

# チャットUIのモックアップ
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "こんにちは！今日の予定を確認しましょうか？"}
    ]

# 履歴の表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 入力エリア（今はオウム返しのみ）
if prompt := st.chat_input("メッセージを入力..."):
    # ユーザーの入力を表示
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 仮の応答
    response = f"受け取りました: {prompt} (まだAIの脳は繋がっていません)"
    with st.chat_message("assistant"):
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    