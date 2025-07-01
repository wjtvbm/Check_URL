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

	![登入 Line](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Line_login.png)

2. 建立 Provider  
	![建立 Provider](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Provider.png)

	Provider 會顯示在 Lint bot 下方  
	![Provider 顯示](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Provider_show.png)

3. 建立 Messaging API Channel。  
	![建立 Messaging API Channel](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Channel.png)
	
	建立 Messaging API Channel 前需要建立 Official Account，系統會幫你導向 Official Account 建立頁面。  
	![建立 Official Account](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Channel_official_account-1.png)
	
	填入必要的資訊以建立 Official Account。  
	![建立 Official Account 資訊](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Channel_official_account-2.png)
	
	你必須同意使用條款  
	![建立 Official Account 條款](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Channel_official_account-terms.png)
	
	Official Account 完成後你會看到像這樣的畫面 @XXXXXXXX 是 Line ID，也可以繳保護費取得易記的名字。  
	![建立 Official Account 完成](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Channel_official_account-done.png)

4. 設定 Messaging API
	進入 https://manager.line.biz/account/@XXXXXXXX/setting/messaging-api (請將 XXXXXXXX 換成你的 ID)，或是直接進入 https://manager.line.biz/ 找到剛剛建立的 Official Account 並在右邊點選設定。  
	![Official Account 設定](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Enable_Message_API-1.png)
	
	選擇啟用 API，選擇要跟哪一個 Provide 連結。(這邊我們選剛剛在第二步建立的 Provider，注意：選定之後不能更改)  
	![Select Provider](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Enable_Message_API-2.png)
	
	輸入你 bot 的隱私及使用條款。可以直接略過。  
	![隱私及使用條款](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Enable_Message_API-3.png)
	
	最後的確認。  
	![最後確認](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Enable_Message_API-4.png)
	
	取得 Channel ID、Channel Secret，Webhook 等 GAE 設定好再放。  
	![Channel_info](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Enable_Message_API-5.png)

	取得 Your user ID  
	到 https://developers.line.biz/console/ ，在左手邊選擇 Provider，選擇 Line Bot 所屬的 Channel，在 Basic settings 頁面裡面找到 Your user ID (其實 Channel ID、Channel Secret 在這邊也可以找到)  
	![User ID](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Line_bot_Your_User_ID.png)
	
GAE
==

確保你已登入並有可用的 Google Cloud 帳戶。

1. 建立新的 Project  
	新增 Project，Project Name 是給人看的，Project ID 最後會變成 Webhook 的網址。以這個例子來說會是 https://for-line-bot-464605.appspot.com/callback  
	![GAE New Project](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/GAE_New_Project.png)

2. 設定 GAE Secret Manager  
	啟用 Secret Manager API，建立完 Project 後會問你要不要啟用，如果沒有問的話就自己去旁邊按  
	![Enable_Secret_Manager_API-1](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Enable_Secret_Manager_API.png)  
	![Enable_Secret_Manager_API-2](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Enable_Secret_Manager_API-2.png)  
	
3. 建立 Secret  
	新增 Channel ID、Channel Secret 及 YOUR_LINE_USER_ID  
	![Secret_Manager-2](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Secret_Manager-2.png)

4. 設定 Secret Manager 權限給 Project  
	把每一個 Key 都點進去後選 GRANT ACCESS，rule 選 Secret Manager Secret Accessor，帳號則是 <Project ID>@appspot.gserviceaccount.com 在這邊的例子是 for-line-bot-464605@appspot.gserviceaccount.com  

5. 部屬到 GAE  
	安裝 [Google Cloud CLI](https://cloud.google.com/sdk/docs/downloads-interactive)  
	安裝完後後執行 ```gcloud init``` 初始化   
	準備好 app.py, app.yaml, Procfile 及 requirements.txt 放到任意資料夾(如 C:\Line-Bot )  
	![APP-1](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/app-1.png)  
	之後再執行 ```gcloud app deploy```  
	![deploy](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/deploy.png)  

6. 最後再到 https://developers.line.biz/console/ 在左手邊選擇 Provider，選擇 Line Bot 所屬的 Channel，在 Messaging API 裡面 Verify Webhook 可以正確使用。  
	![Webhook](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/Webhook_Setting.png)

執行
==
將 ```send_to_bot.py``` 傳到 Linux 上。可以用 ```/path/to/your/script.sh | python3 /path/to/your/send_to_bot.py``` 來測試。  
	![TEST](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/test-1.png)  
	![TEST](https://github.com/wjtvbm/Check_URL/blob/main/Pictures/test-2.png)  