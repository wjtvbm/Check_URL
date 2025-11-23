import socket
import requests
import os
import sys
import time

# --- config ---
TARGET_HOST = "127.0.0.1"           # IP / Domain
TARGET_PORT = 80                    # Port
LINE_TOKEN = "8gXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXU="
USER_ID = "UdXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX8"       # U開頭的那串亂碼
STATUS_FILE = "/tmp/monitor_status_check.txt"       # 狀態暫存檔
REMINDER_SECONDS = 3600             # 重發的時間(單位秒)

# 呼叫 Line Messaging API 送訊息
def send_line_push(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    data = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    try:
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Line API Error: {e}")

# 檢查 port 狀態
def check_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

# 寫入狀態至暫存檔，格式：狀態|時間戳記|是否已提醒
def save_status(status, timestamp, reminder_sent):
    with open(STATUS_FILE, "w") as f:
        f.write(f"{status}|{timestamp}|{reminder_sent}")

def main():
    current_time = int(time.time())
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))

    is_connected = check_port(TARGET_HOST, TARGET_PORT)

    # 狀態預設值 (如果狀態檔不存在)
    last_status = "UP"
    last_time = current_time
    reminder_sent = "0"

    # 讀取舊狀態
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                content = f.read().strip()
                parts = content.split("|")
                if len(parts) == 3:
                    last_status = parts[0]
                    last_time = int(parts[1])
                    reminder_sent = parts[2]
                else:
                    last_status = "UP"
        except:
            pass

    if is_connected and last_status == "DOWN":
        # 恢復正常
        duration = int((current_time - last_time) / 60)
        msg = f"[{time_str}]\n [恢復] {TARGET_HOST}:{TARGET_PORT} 連線已恢復正常 (中斷約 {duration} 分鐘)。"
        print(msg)
        send_line_push(msg)
        save_status("UP", current_time, "0")

    elif not is_connected and last_status == "UP":
        # 發現異常
        msg = f"[{time_str}]\n [警告] {TARGET_HOST}:{TARGET_PORT} 無法連線！"
        print(msg)
        send_line_push(msg)
        save_status("DOWN", current_time, "0")

    elif not is_connected and last_status == "DOWN":
        # 異常超過一小時 (REMINDER_SECONDS)
        duration_seconds = current_time - last_time
        if duration_seconds >= REMINDER_SECONDS and reminder_sent == "0":
            msg = f"[{time_str}]\n [嚴重] {TARGET_HOST}:{TARGET_PORT} 已斷線超過一小時！"
            print(msg)
            send_line_push(msg)
            save_status("DOWN", last_time, "1")
        else:
            pass

    else:
        # 狀態沒變，若檔案不存在補建
        if not os.path.exists(STATUS_FILE):
            save_status("UP", current_time, "0")

if __name__ == "__main__":
    main()
