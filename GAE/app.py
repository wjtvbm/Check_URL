import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from datetime import datetime
import pytz

# Google Cloud Secret Manager client
from google.cloud import secretmanager

app = Flask(__name__)

# 從 Secret Manager 讀 key
def get_secret_value(secret_name):
    # 取得 Project
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', os.environ.get('GAE_APPLICATION'))
    if not project_id:
        print("Warning: GOOGLE_CLOUD_PROJECT environment variable not set. Attempting to get project from gcloud config.")
        try:
            import subprocess
            project_id = subprocess.check_output(['gcloud', 'config', 'get-value', 'project']).decode('utf-8').strip()
        except Exception as e:
            print(f"Error getting project ID from gcloud config: {e}")
            return None

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error accessing secret '{secret_name}': {e}")
        # 如果無法獨到 Key 就退出
        return None

# 從 Secret Manager 讀 Key 並檢查是否讀到全部的 Key 
LINE_CHANNEL_ACCESS_TOKEN = get_secret_value('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = get_secret_value('LINE_CHANNEL_SECRET')
YOUR_LINE_USER_ID = get_secret_value('YOUR_LINE_USER_ID')

if not all([LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, YOUR_LINE_USER_ID]):
    print("FATAL ERROR: One or more Line Bot secrets could not be loaded. Check Secret Manager and IAM permissions.")
    import sys
    sys.exit(1)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Webhook (給 Line bot 用的)
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# 回訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    utc_now = datetime.utcnow()
    taiwan_tz = pytz.timezone('Asia/Taipei')
    taiwan_time = utc_now.astimezone(taiwan_tz)
    time_str = taiwan_time.strftime("%Y-%m-%d %H:%M:%S")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"現在時間：{time_str}\n你說了：{event.message.text}\n我現在在 GAE 上！")
    )

# 接 curl 結果
@app.route("/send_curl_result", methods=['POST'])
def send_curl_result():
    if request.method == 'POST':
        try:
            data = request.get_json()
            message_content = data.get('message', '未收到有效的訊息內容。')

            if len(message_content) > 5000:
                message_content = message_content[:4900] + "\n...(訊息過長，已截斷)"

            if YOUR_LINE_USER_ID:
                line_bot_api.push_message(YOUR_LINE_USER_ID, TextSendMessage(text=message_content))
                print(f"訊息已成功發送給用戶: {YOUR_LINE_USER_ID}")
                return '訊息已發送', 200
            else:
                print("YOUR_LINE_USER_ID is not set via Secret Manager. Cannot push message.")
                return 'Internal Server Error: User ID not set', 500
        except Exception as e:
            print(f"處理 /send_curl_result 請求時發生錯誤: {e}")
            return f'Internal Server Error: {e}', 500
    return 'Method Not Allowed', 405

# if __name__ == "__main__":
#     port = int(os.environ.get('PORT', 8080))
#     app.run(host='0.0.0.0', port=port)