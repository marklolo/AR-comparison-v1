# Outputs Directory

此目錄用於存放 AnnualCompare Lite 生成的輸出文件。

## 文件類型

### CSV 文件
- `metrics_aligned_all_[timestamp].csv` - 所有公司的對齊指標比較表
- `tables_[company]_[year]_[type].csv` - 各公司的個別財務報表

### JSON 文件
- `insights_[timestamp].json` - 語義查詢的結構化分析結果

### TXT 文件  
- `insights_[timestamp].txt` - 語義查詢的可讀性分析報告

## 注意事項

- 輸出文件會自動根據時間戳命名
- 所有文件都是臨時生成，不會持久化到資料庫
- 建議定期清理舊的輸出文件以節省磁盤空間