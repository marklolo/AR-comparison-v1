"""
財務指標計算和比率包模組
支援預設比率包的計算與對齊
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Metric:
    name: str
    value: float
    unit: str
    period: str
    page_ref: str
    calculation_method: str = ""

@dataclass
class CompanyMetrics:
    company: str
    fiscal_year: int
    period: str
    currency: str
    metrics: Dict[str, Metric]

class FinancialCalculator:
    def __init__(self):
        self.ratio_definitions = {
            "profitability": {
                "gross_margin": "毛利率",
                "operating_margin": "營業利潤率", 
                "net_margin": "淨利率",
                "roe": "股東權益報酬率(ROE)",
                "roa": "資產報酬率(ROA)",
                "ebitda_margin": "EBITDA利潤率"
            },
            "growth": {
                "revenue_yoy": "營收年增率",
                "net_income_yoy": "淨利年增率",
                "revenue_cagr_3y": "營收3年複合增長率"
            },
            "efficiency": {
                "asset_turnover": "資產周轉率",
                "inventory_days": "存貨周轉天數(DIO)",
                "receivable_days": "應收帳款天數(DSO)"
            },
            "leverage": {
                "debt_ratio": "負債比率",
                "debt_to_ebitda": "淨負債/EBITDA",
                "interest_coverage": "利息保障倍數"
            },
            "cash_quality": {
                "ocf_to_ni": "經營現金流/淨利",
                "fcf_margin": "自由現金流利潤率"
            }
        }
        
        # 財務科目關鍵字映射
        self.account_keywords = {
            'zh': {
                'revenue': ['營業收入', '營收', '銷售收入', '總收入', '收入'],
                'gross_profit': ['毛利', '銷售毛利'],
                'operating_income': ['營業利益', '營業利潤', '經營利潤'],
                'net_income': ['本期淨利', '淨利潤', '淨收益', '稅後淨利', '稅後盈餘'],
                'total_assets': ['總資產', '資產總額'],
                'total_liabilities': ['總負債', '負債總額'],
                'shareholders_equity': ['股東權益', '所有者權益', '淨資產'],
                'operating_cash_flow': ['營業活動現金流量', '經營活動現金流量']
            }
        }
    
    def extract_key_figures(self, report, statements: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """
        從財務報表中抽取關鍵數字
        """
        figures = {}
        
        # 從損益表抽取
        if not statements['income'].empty:
            figures.update(self._extract_from_income_statement(statements['income']))
        
        # 從資產負債表抽取
        if not statements['balance'].empty:
            figures.update(self._extract_from_balance_sheet(statements['balance']))
        
        # 從現金流量表抽取
        if not statements['cashflow'].empty:
            figures.update(self._extract_from_cashflow_statement(statements['cashflow']))
        
        return figures
    
    def _extract_from_income_statement(self, df: pd.DataFrame) -> Dict[str, float]:
        """從損益表抽取數據"""
        figures = {}
        text_data = df.to_string()
        
        # 抽取營業收入
        revenue = self._find_amount_by_keywords(text_data, self.account_keywords['zh']['revenue'])
        if revenue:
            figures['revenue'] = revenue
        
        # 抽取淨利
        net_income = self._find_amount_by_keywords(text_data, self.account_keywords['zh']['net_income'])
        if net_income:
            figures['net_income'] = net_income
        
        return figures
    
    def _extract_from_balance_sheet(self, df: pd.DataFrame) -> Dict[str, float]:
        """從資產負債表抽取數據"""
        figures = {}
        text_data = df.to_string()
        
        # 抽取總資產
        total_assets = self._find_amount_by_keywords(text_data, self.account_keywords['zh']['total_assets'])
        if total_assets:
            figures['total_assets'] = total_assets
        
        # 抽取股東權益
        shareholders_equity = self._find_amount_by_keywords(text_data, self.account_keywords['zh']['shareholders_equity'])
        if shareholders_equity:
            figures['shareholders_equity'] = shareholders_equity
        
        return figures
    
    def _extract_from_cashflow_statement(self, df: pd.DataFrame) -> Dict[str, float]:
        """從現金流量表抽取數據"""
        figures = {}
        text_data = df.to_string()
        
        # 抽取營業活動現金流量
        operating_cash_flow = self._find_amount_by_keywords(text_data, self.account_keywords['zh']['operating_cash_flow'])
        if operating_cash_flow:
            figures['operating_cash_flow'] = operating_cash_flow
        
        return figures
    
    def _find_amount_by_keywords(self, text: str, keywords: List[str]) -> Optional[float]:
        """
        根據關鍵字在文字中查找金額
        """
        for keyword in keywords:
            # 查找包含關鍵字的行
            lines = text.split('\n')
            for line in lines:
                if keyword in line:
                    # 提取數字
                    numbers = re.findall(r'[\d,]+\.?\d*', line)
                    if numbers:
                        try:
                            # 取最大的數字（通常是主要金額）
                            amounts = [float(num.replace(',', '')) for num in numbers if float(num.replace(',', '')) > 1000]
                            if amounts:
                                return max(amounts)
                        except ValueError:
                            continue
        return None
    
    def calculate_ratios(self, figures: Dict[str, float]) -> CompanyMetrics:
        """
        計算所有預設比率包
        """
        metrics = {}
        
        # 盈利能力指標
        metrics.update(self._calculate_profitability_ratios(figures))
        
        # 效率指標
        metrics.update(self._calculate_efficiency_ratios(figures))
        
        # 槓桿與償債指標
        metrics.update(self._calculate_leverage_ratios(figures))
        
        # 現金流質量指標
        metrics.update(self._calculate_cash_quality_ratios(figures))
        
        return CompanyMetrics(
            company="",  # 將在後續填入
            fiscal_year=2023,  # 將在後續填入
            period="FY",
            currency="",  # 將在後續填入
            metrics=metrics
        )
    
    def _calculate_profitability_ratios(self, figures: Dict[str, float]) -> Dict[str, Metric]:
        """計算盈利能力指標"""
        metrics = {}
        
        revenue = figures.get('revenue', 0)
        net_income = figures.get('net_income', 0)
        total_assets = figures.get('total_assets', 0)
        shareholders_equity = figures.get('shareholders_equity', 0)
        
        # 淨利率
        if revenue > 0 and net_income > 0:
            net_margin = (net_income / revenue) * 100
            metrics['net_margin'] = Metric(
                name="淨利率",
                value=round(net_margin, 2),
                unit="%",
                period="FY",
                page_ref="計算得出",
                calculation_method="淨利 / 營業收入"
            )
        
        # ROE
        if shareholders_equity > 0 and net_income != 0:
            roe = (net_income / shareholders_equity) * 100
            metrics['roe'] = Metric(
                name="股東權益報酬率(ROE)",
                value=round(roe, 2),
                unit="%",
                period="FY",
                page_ref="計算得出",
                calculation_method="淨利 / 股東權益"
            )
        
        # ROA
        if total_assets > 0 and net_income != 0:
            roa = (net_income / total_assets) * 100
            metrics['roa'] = Metric(
                name="資產報酬率(ROA)",
                value=round(roa, 2),
                unit="%",
                period="FY",
                page_ref="計算得出",
                calculation_method="淨利 / 總資產"
            )
        
        return metrics
    
    def _calculate_efficiency_ratios(self, figures: Dict[str, float]) -> Dict[str, Metric]:
        """計算效率指標"""
        metrics = {}
        
        revenue = figures.get('revenue', 0)
        total_assets = figures.get('total_assets', 0)
        
        # 資產周轉率
        if total_assets > 0 and revenue > 0:
            metrics['asset_turnover'] = Metric(
                name="資產周轉率",
                value=round(revenue / total_assets, 2),
                unit="倍",
                period="FY",
                page_ref="計算得出",
                calculation_method="營業收入 / 總資產"
            )
        
        return metrics
    
    def _calculate_leverage_ratios(self, figures: Dict[str, float]) -> Dict[str, Metric]:
        """計算槓桿與償債指標"""
        metrics = {}
        
        total_assets = figures.get('total_assets', 0)
        total_liabilities = figures.get('total_liabilities', 0)
        
        # 負債比率
        if total_assets > 0 and total_liabilities > 0:
            metrics['debt_ratio'] = Metric(
                name="負債比率",
                value=round((total_liabilities / total_assets) * 100, 2),
                unit="%",
                period="FY",
                page_ref="計算得出",
                calculation_method="總負債 / 總資產"
            )
        
        return metrics
    
    def _calculate_cash_quality_ratios(self, figures: Dict[str, float]) -> Dict[str, Metric]:
        """計算現金流質量指標"""
        metrics = {}
        
        operating_cash_flow = figures.get('operating_cash_flow', 0)
        net_income = figures.get('net_income', 0)
        
        # 經營現金流/淨利
        if net_income > 0 and operating_cash_flow > 0:
            metrics['ocf_to_ni'] = Metric(
                name="經營現金流/淨利",
                value=round(operating_cash_flow / net_income, 2),
                unit="倍",
                period="FY",
                page_ref="計算得出",
                calculation_method="營業活動現金流量 / 淨利"
            )
        
        return metrics