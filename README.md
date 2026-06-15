# YouTube 轉 MP3 工具

iPad、手機、電腦都能用的網頁版轉換工具。

---

## 部署步驟（一次設定，永久使用）

### 第一步：把程式碼放到 GitHub

1. 前往 [github.com](https://github.com) 並登入（沒有帳號請先免費註冊）
2. 點右上角「**+**」→「**New repository**」
3. Repository name 填入：`yt2mp3`
4. 選「**Private**」（私人）
5. 按「**Create repository**」
6. 把這個資料夾裡的所有檔案上傳上去（點「uploading an existing file」）

---

### 第二步：在 Render 部署

1. 前往 [render.com](https://render.com) 並免費註冊
2. 點「**New +**」→「**Web Service**」
3. 選「**Connect a Git repository**」→ 連結你的 GitHub 帳號
4. 選剛才建立的 `yt2mp3` repo
5. 設定如下：
   - **Name**：yt2mp3（隨意）
   - **Runtime**：選「**Docker**」
   - **Instance Type**：選「**Free**」
6. 按「**Create Web Service**」
7. 等待約 3～5 分鐘部署完成
8. 部署完成後會看到一個網址，例如：`https://yt2mp3.onrender.com`

---

### 第三步：在 iPad 使用

1. 用 Safari 打開 Render 給你的網址
2. 貼上 YouTube 網址
3. 按「開始轉換」
4. 完成後按「下載 MP3」

> **提示**：可以把網址加入書籤，方便下次快速開啟。

---

## 注意事項

- 免費方案若超過 15 分鐘無人使用，伺服器會「睡眠」，下次開啟需等約 30 秒喚醒
- 檔案下載後會自動從伺服器刪除，不會儲存
- 僅供下載個人創作或公共版權音樂使用

---

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `app.py` | 後端主程式（Flask） |
| `templates/index.html` | 網頁介面 |
| `requirements.txt` | Python 套件清單 |
| `Dockerfile` | 含 ffmpeg 的容器設定 |
| `render.yaml` | Render 部署設定 |
