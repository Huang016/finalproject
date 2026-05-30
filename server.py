import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)

SYSTEM_PROMPT = """
你現在是「湛藍守護：台灣水資源監測平台」的專屬 AI 客服導覽員。
請用友善、專業、簡短的語氣回答使用者的問題。
以下是關於本網站的資訊：
1. 網站目的：結合政府開放資料與民眾力量，即時監控全國河川與水庫水質。
2. 地圖顏色：綠色代表正常、黃色代表中度污染、紅色代表重度污染。
3. 積分系統：登入並通報污染可獲得 50 積分。
4. 通報功能：網頁下方有全民通報網，可上傳照片與地點。
5. 即時數據：點擊地圖或數據中心可查看水質資料，也可以匯出 CSV 報表。
請根據以上資訊，自然地回答使用者的問題。如果使用者閒聊，也請友善回應。
""".strip()


def call_gemini(user_message: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("找不到 GEMINI_API_KEY，請先在 .env 裡設定。")

    # 可在 .env 自訂：GEMINI_MODEL=gemini-flash-lite-latest
    model = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"{SYSTEM_PROMPT}\n\n使用者問：{user_message}"
                    }
                ],
            }
        ]
    }

    try:
        session = requests.Session()
        session.trust_env = False
        response = session.post(
            url,
            params={"key": api_key},
            json=payload,
            timeout=30,
        )
    except requests.RequestException:
        raise RuntimeError("無法連線到 Gemini API，請確認網路、Proxy 設定或稍後再試。")

    try:
        data = response.json() if response.content else {}
    except ValueError:
        data = {}
    if not response.ok:
        message = data.get("error", {}).get("message") or f"Gemini API 錯誤：HTTP {response.status_code}"
        raise RuntimeError(message)

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("Gemini 沒有回傳可用的文字內容。")


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "project2.html")


@app.route("/<path:filename>")
def files(filename):
    # 讓 api_data.json、圖片或其他靜態檔可以被讀到。
    # 不提供 .env，避免在瀏覽器曝光 API key。
    if filename == ".env" or filename.endswith(".env"):
        return "Not found", 404
    return send_from_directory(BASE_DIR, filename)

@app.route("/")
def home():
    return "Render is working. API endpoint is /api/chat"

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify({"error": "請輸入問題。"}), 400

    try:
        reply = call_gemini(message)
        return jsonify({"reply": reply})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    debug = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(host="0.0.0.0", port=port, debug=debug)
