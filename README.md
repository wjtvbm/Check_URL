# Check_URL
Line bot 練習，檢查透過 curl 檢查特定網站並傳 Line 至使用者

事前準備
===

- Line bot: https://developers.line.biz/
- GAE: https://console.cloud.google.com/
- Secret Manager: https://console.cloud.google.com/security/secret-manager 需啟用 Secret Manager API (六個以內免費, 或是直接把 token 寫在程式裡面)

建立 Line Bot
==
1. 在電腦上登入 [Line Console](https://account.line.biz/console/ "Line Console")，可以用帳號密碼或是用 QRCode 登入。
[![登入 Line](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Line_login.png)]

2. 建立 Provider
[![建立 Provider](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Provider.png)]

Provider 會顯示在 Lint bot 下方
[![Provider 顯示](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Provider_show.png)]