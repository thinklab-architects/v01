# 建築法規自動檢核系統 (Building Compliance Checker)

這是一個 Web 應用程式，旨在將《建築技術規則》數位化，提供即時的法規檢核服務。使用者可以輸入建築物的相關參數（如樓層數、樓板面積、使用類組等），系統會根據內建的規則引擎，即時指出不符合法規的項目並提供合規建議。

## 專案架構

-   **前端 (`/frontend`)**: 使用 React 開發的多步驟表單，用於收集建築參數。(待建立)
-   **後端 (`/backend`)**: 使用 Python (FastAPI) 開發的 API 服務，內含一個簡易的規則引擎，負責處理檢核邏輯。
-   **規則 (`/backend/rules.json`)**: 以 JSON 格式儲存的法規判斷式。

## 功能

-   **`/check-compliance`**: 根據輸入的建築參數進行法規檢核。
-   **`/admin/reload-rules`**: **[管理者]** 從 `rules.json` 檔案熱重載 (Hot-Reload) 規則，無需重啟服務。

## 如何啟動

### 1. 設定後端環境

首先，進入後端目錄並設定環境變數。

```bash
# 進入後端資料夾
cd backend

# 複製環境變數範例檔
cp .env.example .env
```

接著，編輯 `.env` 檔案，設定一個您自己的 `ADMIN_API_KEY`。這個金鑰將用於保護管理者 API。

### 2. 安裝依賴套件並啟動後端

```bash
# 建議先建立並啟用虛擬環境
# python -m venv venv
# source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝 Python 套件 (需要新增 python-dotenv)
pip install fastapi "uvicorn[standard]" python-dotenv

# 啟動後端服務
uvicorn main:app --reload
```

服務將會運行在 `http://127.0.0.1:8000`。您可以前往 `http://127.0.0.1:8000/docs` 查看自動生成的 API 文件。

## 如何使用熱重載 (Hot-Reload)

您可以使用 `curl` 或任何 API 工具來觸發規則的熱重載。請記得替換成您在 `.env` 檔案中設定的金鑰。

```bash
curl -X POST http://127.0.0.1:8000/admin/reload-rules \
-H "Content-Type: application/json" \
-H "X-API-KEY: your-secret-api-key-here"
```
