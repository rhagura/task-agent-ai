import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests

# .envファイルを読み込む
load_dotenv()

# --- 1. Google Calendar API テスト ---
def test_google_calendar():
    print("\n--- Google Calendar API テスト開始 ---")
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    # credentials.jsonを使用して認証
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    service = build('calendar', 'v3', credentials=creds)
    print("直近の予定を5件取得します...")
    events_result = service.events().list(calendarId='primary', maxResults=5).execute()
    events = events_result.get('items', [])
    
    if not events:
        print('予定は見つかりませんでした。')
    for event in events:
        print(f"予定: {event.get('summary')} ({event.get('start').get('dateTime')})")

# --- 2. Notion API テスト ---
def test_notion():
    print("\n--- Notion API テスト開始 ---")
    NOTION_TOKEN = os.getenv("NOTION_API_SECRET")
    DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # データベースの情報を取得してみる
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # タイトルが空の場合でもエラーにならないように取得
        titles = data.get('title', [])
        db_name = titles[0].get('plain_text') if titles else "（名前なし）"
        print(f"Notion接続成功！ データベース名: {db_name}")
    else:
        print(f"Notionエラー: {response.status_code}, {response.text}")

if __name__ == "__main__":
    try:
        test_google_calendar()
        test_notion()
    except Exception as e:
        print(f"エラー発生: {e}")