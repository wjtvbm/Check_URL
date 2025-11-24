import socket
import requests
import os
import sys
import time

# --- config ---
TARGET_HOST = "127.0.0.1"           # IP / Domain
TARGET_PORT = 80                    # Port
LINE_TOKEN = "8gXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXU="
USER_IDS = [
    "UdXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX8",  # User #1
    "UdYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY8"   # User #2 (只要發一個人的話就把其他 comment out )
]
STATUS_FILE = "/tmp/monitor_status_check.txt"       # 狀態暫存檔
REMINDER_INTERVAL = 3600            # 重發的時間(單位秒)

# 呼叫 Line Messaging API 送訊息
def send_line_multicast(message):
    url = "https://api.line.me/v2/bot/message/multicast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    data = {
        "to": USER_IDS,
        "messages": [{"type": "text", "text": message}]
    }
    try:
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Request Failed: {e}")

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

# 寫入狀態至暫存檔，格式：狀態|第一次斷線時間(用來算斷多久)|上次發通知時間(用來算下次何時發)
def save_status(status, first_down_time, last_reminder_time):
    with open(STATUS_FILE, "w") as f:
        f.write(f"{status}|{first_down_time}|{last_reminder_time}")

def main():
    current_time = int(time.time())
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))

    is_connected = check_port(TARGET_HOST, TARGET_PORT)

    # 狀態預設值
    last_status = "UP"
    first_down_time = current_time
    last_reminder_time = current_time

    # 讀取舊狀態
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                content = f.read().strip()
                parts = content.split("|")
                if len(parts) == 3:
                    last_status = parts[0]
                    first_down_time = int(parts[1])
                    last_reminder_time = int(parts[2])
                else:
                    last_status = "UP"
        except:
            pass

    # 四種狀態: 一直都正常、恢復正常、發現異常、發現異常超過 1 小時
    if is_connected and last_status == "DOWN":
        # 恢復正常
        duration = int((current_time - first_down_time) / 60)
        msg = f"[{time_str}]\n [恢復] {TARGET_HOST}:{TARGET_PORT} 連線已恢復正常 (中斷約 {duration} 分鐘)。"
        print(msg)
        send_line_multicast(msg)
        save_status("UP", current_time, current_time)

    elif not is_connected and last_status == "UP":
        # 發現異常
        msg = f"[{time_str}]\n [警告] {TARGET_HOST}:{TARGET_PORT} 無法連線！"
        print(msg)
        send_line_multicast(msg)
        save_status("DOWN", current_time, current_time)

    elif not is_connected and last_status == "DOWN":
        # 異常超過一小時 (REMINDER_INTERVAL)
        if (current_time - last_reminder_time) >= REMINDER_INTERVAL:
#            total_duration_hours = round((current_time - first_down_time) / 3600, 1)
            duration = int((current_time - first_down_time) / 60)
            msg = f"[{time_str}]\n [嚴重] {TARGET_HOST}:{TARGET_PORT} 仍無法連線！\n已持續中斷 {duration} 分鐘。"
            print(msg)
            send_line_multicast(msg)
            # 只更新上次通知時間，起始時間不變
            save_status("DOWN", first_down_time, current_time)
        else:
            # 還沒到下次通知時間，保持安靜
            pass

    else:
        # 狀態沒變且正常
        if not os.path.exists(STATUS_FILE):
            save_status("UP", current_time, current_time)
            
if __name__ == "__main__":
    main()