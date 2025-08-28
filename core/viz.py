"""
可視化模組
支援財務指標的圖表展示
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional

class FinancialVisualizer:
    def __init__(self):
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        
        self.ratio_categories = {
            "profitability": {
                "name": "盈利能力",
                "metrics": ["gross_margin", "operating_margin", "net_margin", "roe", "roa"],
                "unit": "%"
            },
            "efficiency": {
                "name": "營運效率",
                "metrics": ["asset_turnover", "inventory_days", "receivable_days"],
                "unit": "mixed"
            },
            "leverage": {
                "name": "槓桿與償債",
                "metrics": ["debt_ratio"],
                "unit": "mixed"
            },
            "cash_quality": {
                "name": "現金流質量",
                "metrics": ["ocf_to_ni"],
                "unit": "mixed"
            }
        }
    
    def create_metrics_overview_cards(self, company_metrics_list) -> None:
        """
        創建指標概覽卡片
        """
        if not company_metrics_list:
            st.warning("沒有可顯示的指標數據")
            return
        
        # 顯示每家公司的關鍵指標卡片
        for i, cm in enumerate(company_metrics_list):
            st.subheader(f"{cm.company} ({cm.fiscal_year})")
            
            # 創建4列布局顯示關鍵指標
            col1, col2, col3, col4 = st.columns(4)
            
            # 淨利率
            if 'net_margin' in cm.metrics:
                with col1:
                    metric = cm.metrics['net_margin']
                    st.metric(
                        label="淨利率",
                        value=f"{metric.value}%",
                        help=metric.calculation_method
                    )
            
            # ROE
            if 'roe' in cm.metrics:
                with col2:
                    metric = cm.metrics['roe']
                    st.metric(
                        label="ROE",
                        value=f"{metric.value}%",
                        help=metric.calculation_method
                    )
            
            # 負債比率
            if 'debt_ratio' in cm.metrics:
                with col3:
                    metric = cm.metrics['debt_ratio']
                    st.metric(
                        label="負債比率",
                        value=f"{metric.value}%",
                        help=metric.calculation_method
                    )
            
            # 資產周轉率
            if 'asset_turnover' in cm.metrics:
                with col4:
                    metric = cm.metrics['asset_turnover']
                    st.metric(
                        label="資產周轉率",
                        value=f"{metric.value}倍",
                        help=metric.calculation_method
                    )
            
            st.divider()
    
    def create_comparison_charts(self, company_metrics_list, selected_categories: List[str]) -> None:
        """
        創建比較圖表
        """
        if not company_metrics_list or not selected_categories:
            return
        
        for category in selected_categories:
            if category not in self.ratio_categories:
                continue
            
            category_info = self.ratio_categories[category]
            st.subheader(f"📊 {category_info['name']}比較")
            
            # 收集該類別的數據
            chart_data = self._prepare_chart_data(company_metrics_list, category_info['metrics'])
            
            if chart_data.empty:
                st.info(f"暫無{category_info['name']}相關數據")
                continue
            
            # 創建柱狀圖
            fig = self._create_bar_chart(chart_data, category_info['name'])
            st.plotly_chart(fig, use_container_width=True)
    
    def _prepare_chart_data(self, company_metrics_list, metric_keys: List[str]) -> pd.DataFrame:
        """
        準備圖表數據
        """
        data = []
        
        for cm in company_metrics_list:
            for metric_key in metric_keys:
                if metric_key in cm.metrics:
                    metric = cm.metrics[metric_key]
                    data.append({
                        '公司': cm.company,
                        '年度': cm.fiscal_year,
                        '指標': metric.name,
                        '指標代碼': metric_key,
                        '數值': metric.value,
                        '單位': metric.unit
                    })
        
        return pd.DataFrame(data)
    
    def _create_bar_chart(self, df: pd.DataFrame, category_name: str) -> go.Figure:
        """
        創建柱狀圖
        """
        if df.empty:
            return go.Figure()
        
        # 使用 plotly express 創建分組柱狀圖
        fig = px.bar(
            df,
            x='指標',
            y='數值',
            color='公司',
            title=f"{category_name}指標比較",
            barmode='group',
            color_discrete_sequence=self.color_palette
        )
        
        # 美化圖表
        fig.update_layout(
            xaxis_title="指標",
            yaxis_title="數值",
            legend_title="公司",
            height=500,
            showlegend=True
        )
        
        # 添加數值標籤
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        
        return fig