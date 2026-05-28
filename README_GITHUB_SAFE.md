# GitHub 安全版使用方式

## 1. 安裝套件

```powershell
pip install -r requirements.txt
```

## 2. 建立本機 `.env`

請複製 `.env.example`，重新命名成 `.env`，並填入自己的 Gemini API Key。

```env
GEMINI_API_KEY=你的 Gemini API Key
GEMINI_MODEL=gemini-flash-lite-latest
PORT=3000
```

`.env` 不要推上 GitHub。

## 3. 啟動網站

```powershell
python server.py
```

然後打開：

```text
http://127.0.0.1:3000
```

請不要直接雙擊 HTML，也不要用 Live Server 開啟，因為 Gemini API 現在是透過 `server.py` 後端呼叫。

## 4. 推上 GitHub 前

```powershell
git init
git add .
git commit -m "Prepare safe Gemini backend"
git branch -M main
git remote add origin 你的GitHubRepo網址
git push -u origin main
```

如果你是在原本的 Git repo 裡操作，而且 `project.html` / `project1.html` / `.env` 已經被追蹤過，請先執行：

```powershell
git rm --cached .env project.html project1.html
```

再重新 `git add .`。
