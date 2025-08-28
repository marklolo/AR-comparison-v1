# AnnualCompare Lite

## 📋 項目簡介

AnnualCompare Lite 是一個本地執行、雲端 AI 輔助的多公司財報比較工具。支援 2-5 份 PDF 財報（約 300 頁/份）的自動解析、財務指標計算、可視化比較，以及基於 AI 的語義查詢功能。

### ✨ 核心特色

- 🔄 **零資料庫**: 所有運算在記憶體完成，僅輸出結果文件
- 📊 **預設比率包**: 自動計算盈利能力、成長性、營運效率、槓桿償債、現金流質量等五大類指標
- 🔍 **語義查詢**: 支援自然語言查詢（如「策略差異」「風險管理」），AI 自動檢索並比較
- 🌐 **中英雙語**: 界面和輸出支援繁體中文和英文
- ☁️ **雲端AI**: 使用 Gemini 2.5 Flash-Lite 進行文本分析和 Embeddings 向量檢索
- 📈 **豐富圖表**: 柱狀圖、雷達圖、趨勢圖等多種可視化方式
- 📤 **多格式匯出**: 支援 CSV、TXT、JSON 格式匯出

## 🚀 快速開始

### 環境需求

- Python 3.10+
- Windows 10/11, macOS, 或 Linux

### 安裝步驟

1. **下載專案**
   ```bash
   git clone https://github.com/marklolo/AR-comparison-v1.git
   cd AR-comparison-v1
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **設定 API 金鑰** (可選，用於語義查詢功能)
   ```bash
   # 複製配置文件
   copy config.example.env .env
   
   # 編輯 .env 文件，填入你的 Gemini API Key
   GEMINI_API_KEY=your_api_key_here
   ```

4. **啟動應用**
   ```bash
   streamlit run app_simple.py
   ```

5. **開啟瀏覽器**
   應用將在 `http://localhost:8501` 運行

## 📖 使用指南

### MVP-1: 基礎財報比較 (無需 API)

1. **上傳財報**: 上傳 2-5 份 PDF 格式的年度財報
2. **自動解析**: 系統自動抽取文字和表格內容
3. **指標計算**: 自動計算財務比率（毛利率、ROE、負債比等）
4. **可視化比較**: 查看圖表化的指標比較
5. **匯出結果**: 下載 CSV 格式的比較表

### MVP-2: 語義查詢分析 (需要 Gemini API)

1. **建立索引**: 系統自動將財報內容向量化
2. **語義查詢**: 輸入查詢問題，如「各公司的風險管理策略有什麼差異？」
3. **AI 分析**: 系統檢索相關內容並使用 AI 生成分析報告
4. **跨公司比較**: 自動生成各公司差異總結和洞察
5. **匯出分析**: 下載 JSON/TXT 格式的分析報告

### MVP-3: OCR 掃描文檔支援 (需要雲端 OCR API)

1. **檢測文檔類型**: 自動判斷是否需要 OCR 處理
2. **雲端 OCR**: 支援 Google Cloud Vision、Azure Document Intelligence、AWS Textract
3. **圖表理解**: 可選的圖片/圖表多模態分析功能

## 🔧 配置說明

### API 設定

在 `.env` 文件中配置以下 API：

```bash
# Gemini API (必需用於語義查詢)
GEMINI_API_KEY=your_gemini_api_key

# Google Cloud Vision (可選)
GOOGLE_CLOUD_PROJECT_ID=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Azure Document Intelligence (可選)
AZURE_DI_ENDPOINT=your_endpoint
AZURE_DI_KEY=your_key

# AWS Textract (可選)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

### 獲取 API 金鑰

#### Gemini API
1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 創建新的 API Key
3. 將 API Key 填入 `.env` 文件

#### Google Cloud Vision
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 啟用 Vision API
3. 創建服務帳戶並下載憑證文件
4. 設定環境變數指向憑證文件

## 📊 功能特色

### 預設財務比率包

#### 盈利能力
- 毛利率 (Gross Margin)
- 營業利潤率 (Operating Margin)  
- 淨利率 (Net Margin)
- 股東權益報酬率 (ROE)
- 資產報酬率 (ROA)
- EBITDA 利潤率

#### 成長性
- 營收年增率 (Revenue YoY)
- 淨利年增率 (Net Income YoY)
- 3年複合增長率 (3Y CAGR)

#### 營運效率
- 資產周轉率 (Asset Turnover)
- 存貨周轉天數 (DIO)
- 應收帳款天數 (DSO)

#### 槓桿與償債
- 負債比率 (Debt Ratio)
- 淨負債/EBITDA
- 利息保障倍數

#### 現金流質量
- 經營現金流/淨利
- 自由現金流利潤率

### 語義查詢範例

- "各公司的策略重點與未來規劃有什麼差異？"
- "風險管理政策和風險因子比較"
- "分部業務表現和市場策略"
- "資本支出計畫和投資重點"
- "ESG 和永續發展策略比較"

## 📁 項目結構

```
AR-comparison-v1/
├── app_simple.py          # 主應用程式
├── requirements.txt       # 依賴套件
├── config.example.env     # 配置文件範例
├── core/                  # 核心模組
│   ├── parse_pdf.py       # PDF 解析
│   ├── metrics.py         # 財務指標計算
│   ├── viz.py             # 可視化
│   ├── llm.py             # LLM 集成
│   ├── embed_retrieval.py # 向量檢索
│   └── ocr_cloud.py       # 雲端 OCR
├── outputs/               # 輸出文件目錄
└── README.md             # 說明文件
```

## 🔍 故障排除

### 常見問題

**Q: PDF 解析失敗或內容為空**
A: 可能是掃描版 PDF，請開啟「雲端 OCR」功能

**Q: 語義查詢功能不可用**
A: 請檢查是否正確設定 `GEMINI_API_KEY` 環境變數

**Q: 財務指標計算結果為空**
A: 請確認 PDF 包含標準的財務報表格式，系統會嘗試識別關鍵財務科目

**Q: 圖表無法顯示**
A: 請確認瀏覽器支援 JavaScript，並嘗試重新整理頁面

### 效能優化

- **大文件處理**: 建議單個 PDF 不超過 300 頁
- **記憶體使用**: 處理多個大文件時可能需要 8GB+ 記憶體
- **API 配額**: 注意 Gemini API 的免費配額限制

## 📈 輸出文件說明

### CSV 文件
- `metrics_aligned_all_[timestamp].csv`: 所有公司的對齊指標比較表

### JSON 文件  
- `insights_[timestamp].json`: 語義查詢的結構化分析結果

### TXT 文件
- `insights_[timestamp].txt`: 語義查詢的可讀性分析報告

## 🛣️ 開發路線圖

### 已完成 (MVP-1)
- ✅ PDF 文字/表格解析
- ✅ 財務指標自動計算
- ✅ 多公司比較可視化
- ✅ CSV/TXT/JSON 匯出

### 已完成 (MVP-2)  
- ✅ 向量檢索和語義搜索
- ✅ Gemini LLM 集成
- ✅ 跨公司比較分析

### 已完成 (MVP-3)
- ✅ 雲端 OCR 支援
- ✅ 圖片/圖表理解框架

### 未來計畫
- 🔄 歷史多年度趨勢分析
- 🔄 更多財務指標和行業基準
- 🔄 報告模板自定義
- 🔄 批量處理和自動化

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發環境設定
```bash
# 克隆專案
git clone https://github.com/marklolo/AR-comparison-v1.git
cd AR-comparison-v1

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝開發依賴
pip install -r requirements.txt
```

## 📄 授權

本專案採用 MIT 授權條款。

## 📞 支援

如有問題或建議，請：
1. 查看本 README 和故障排除章節
2. 提交 GitHub Issue
3. 聯絡開發團隊

---

**AnnualCompare Lite** - 讓財報比較變得簡單高效！ 🚀