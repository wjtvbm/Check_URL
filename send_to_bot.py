import sys
import requests
import json
import os

# 替換為你 GAE 服務的 URL，格式為 https://YOUR_PROJECT_ID.appspot.com/send_curl_result
BOT_RECEIVE_URL = 'https://XXXXXXXXXXXXXXXX.appspot.com/send_curl_result'

def send_message_to_bot(message_content):
    headers = {
        'Content-Type': 'application/json'
    }
    payload = json.dumps({"message": message_content})

    try:
        response = requests.post(BOT_RECEIVE_URL, headers=headers, data=payload)
        response.raise_for_status() # 如果傳回來不是 2xx，則會拋出異常 (傳給 Lint Bot)
        print(f"訊息成功發送。Bot 回覆: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"發送訊息到 Bot 時發生錯誤: {e}")
        print(f"Bot 原始回覆: {e.response.text if e.response else '無回覆'}")
        sys.exit(1) # 如果失敗則退出，讓 crontab 可以記錄錯誤

if __name__ == "__main__":
    incoming_message = sys.stdin.read().strip()
    if not incoming_message:
        print("未從標準輸入接收到任何訊息。")
        sys.exit(1)
    send_message_to_bot(incoming_message)