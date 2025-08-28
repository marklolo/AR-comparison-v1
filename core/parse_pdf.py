"""
PDF 解析模組
支援文字層 PDF 的解析，抽取文字和表格數據
"""
import pdfplumber
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class SectionType(Enum):
    TEXT = "text"
    TABLE = "table"
    FIGURE = "figure"

@dataclass
class Section:
    type: SectionType
    page_from: int
    page_to: int
    content: str
    page_ref: str
    raw_data: Optional[any] = None

@dataclass
class Report:
    report_id: str
    company: str
    fiscal_year: int
    period: str  # FY, Q1, Q2, Q3, Q4, TTM
    currency: str
    sections: List[Section]
    
class PDFParser:
    def __init__(self):
        self.financial_keywords = {
            'zh': [
                '損益表', '綜合損益表', '利潤表', '收益表',
                '資產負債表', '財務狀況表', '資產負債及股東權益表',
                '現金流量表', '現金流表',
                '營業收入', '營收', '銷售收入', '總收入',
                '營業成本', '銷售成本', '營業費用',
                '營業利益', '營業利潤', '經營利潤',
                '稅前利益', '稅前利潤', '稅前盈餘',
                '本期淨利', '淨利潤', '淨收益', '稅後淨利',
                '總資產', '資產總額', '總負債', '負債總額',
                '股東權益', '所有者權益', '淨資產',
                '營業活動現金流量', '經營活動現金流量',
                '投資活動現金流量', '融資活動現金流量'
            ],
            'en': [
                'income statement', 'statement of income', 'profit and loss',
                'balance sheet', 'statement of financial position',
                'cash flow statement', 'statement of cash flows',
                'revenue', 'sales', 'net sales', 'total revenue',
                'cost of sales', 'cost of goods sold', 'operating expenses',
                'operating income', 'operating profit',
                'income before tax', 'pretax income',
                'net income', 'net profit', 'net earnings',
                'total assets', 'total liabilities',
                'shareholders equity', 'stockholders equity',
                'operating cash flow', 'cash from operations',
                'investing cash flow', 'financing cash flow'
            ]
        }
    
    def detect_pdf_type(self, pdf_path: str) -> bool:
        """
        檢測 PDF 是否有文字層
        返回 True 表示有文字層，False 表示需要 OCR
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # 檢查前幾頁是否有文字
                for i, page in enumerate(pdf.pages[:3]):  # 檢查前3頁
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:  # 如果有足夠的文字
                        return True
                return False
        except Exception as e:
            print(f"檢測 PDF 類型時發生錯誤: {e}")
            return False
    
    def parse_pdf(self, pdf_path: str, company: str = "", fiscal_year: int = 2023) -> Report:
        """
        解析 PDF 文件，抽取文字和表格
        """
        sections = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    page_ref = f"第{page_num + 1}頁"
                    
                    # 抽取文字
                    text = page.extract_text()
                    if text and len(text.strip()) > 20:
                        sections.append(Section(
                            type=SectionType.TEXT,
                            page_from=page_num + 1,
                            page_to=page_num + 1,
                            content=text.strip(),
                            page_ref=page_ref
                        ))
                    
                    # 抽取表格
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if table and len(table) > 1:  # 至少有標題行和數據行
                            # 將表格轉換為 DataFrame
                            df = pd.DataFrame(table[1:], columns=table[0])
                            
                            sections.append(Section(
                                type=SectionType.TABLE,
                                page_from=page_num + 1,
                                page_to=page_num + 1,
                                content=f"表格 {table_idx + 1}: {df.to_string()}",
                                page_ref=f"{page_ref}_表格{table_idx + 1}",
                                raw_data=df
                            ))
        
        except Exception as e:
            print(f"解析 PDF 時發生錯誤: {e}")
        
        # 嘗試提取公司資訊
        if not company:
            company = self._extract_company_name(sections)
        
        report_id = f"{company}_{fiscal_year}"
        
        return Report(
            report_id=report_id,
            company=company,
            fiscal_year=fiscal_year,
            period="FY",  # 默認為年度報告
            currency="",  # 後續從內容中提取
            sections=sections
        )
    
    def _extract_company_name(self, sections: List[Section]) -> str:
        """
        從文檔內容中提取公司名稱
        """
        for section in sections[:5]:  # 檢查前5個段落
            if section.type == SectionType.TEXT:
                text = section.content
                # 簡單的公司名稱提取邏輯
                lines = text.split('\n')
                for line in lines[:10]:  # 檢查前10行
                    if any(keyword in line for keyword in ['股份有限公司', 'Corporation', 'Inc.', 'Ltd', '公司']):
                        return line.strip()
        return "未知公司"
    
    def extract_financial_statements(self, report: Report) -> Dict[str, pd.DataFrame]:
        """
        從報告中提取三大財務報表
        """
        statements = {
            'income': pd.DataFrame(),
            'balance': pd.DataFrame(),
            'cashflow': pd.DataFrame()
        }
        
        for section in report.sections:
            if section.type == SectionType.TABLE and section.raw_data is not None:
                df = section.raw_data
                
                # 檢查是否為財務報表
                table_content = section.content.lower()
                
                if self._is_income_statement(table_content):
                    statements['income'] = df
                elif self._is_balance_sheet(table_content):
                    statements['balance'] = df
                elif self._is_cashflow_statement(table_content):
                    statements['cashflow'] = df
        
        return statements
    
    def _is_income_statement(self, text: str) -> bool:
        """判斷是否為損益表"""
        keywords = ['損益', '利潤', '收益', 'income', 'profit']
        return any(keyword in text for keyword in keywords)
    
    def _is_balance_sheet(self, text: str) -> bool:
        """判斷是否為資產負債表"""
        keywords = ['資產負債', '財務狀況', 'balance', 'position']
        return any(keyword in text for keyword in keywords)
    
    def _is_cashflow_statement(self, text: str) -> bool:
        """判斷是否為現金流量表"""
        keywords = ['現金流', 'cash flow', 'cash flows']
        return any(keyword in text for keyword in keywords)
    
    def slice_content_for_search(self, report: Report, chunk_size: int = 500) -> List[Dict]:
        """
        將內容切片用於向量檢索
        """
        chunks = []
        chunk_id = 0
        
        for section in report.sections:
            if section.type == SectionType.TEXT:
                # 將長文本切分為小塊
                text = section.content
                words = text.split()
                
                for i in range(0, len(words), chunk_size):
                    chunk_text = ' '.join(words[i:i + chunk_size])
                    if len(chunk_text.strip()) > 50:  # 過濾太短的片段
                        chunks.append({
                            'doc_id': report.report_id,
                            'chunk_id': f"{report.report_id}_chunk_{chunk_id}",
                            'text': chunk_text,
                            'page_ref': section.page_ref,
                            'section_type': section.type.value
                        })
                        chunk_id += 1
            
            elif section.type == SectionType.TABLE:
                # 表格內容也加入檢索
                chunks.append({
                    'doc_id': report.report_id,
                    'chunk_id': f"{report.report_id}_table_{chunk_id}",
                    'text': section.content,
                    'page_ref': section.page_ref,
                    'section_type': section.type.value
                })
                chunk_id += 1
        
        return chunks