"""
AnnualCompare Lite - Main Application
Simple multi-company financial report comparison tool
"""
import streamlit as st
import pandas as pd
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Optional

# Import core modules
from core.parse_pdf import PDFParser
from core.metrics import FinancialCalculator
from core.llm import GeminiLLMClient, MockLLMClient
from core.embed_retrieval import EmbeddingService

# Configure page
st.set_page_config(
    page_title="AnnualCompare Lite",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 AnnualCompare Lite v1.0")
    st.markdown("*本地執行、雲端 AI 輔助的多公司財報比較工具*")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Extract", "📋 Financial Data", "🎯 Strategic Analysis", "🔍 Q&A Compare"])
    
    with tab1:
        handle_upload_and_extract()
    
    with tab2:
        show_financial_data()
    
    with tab3:
        show_strategic_analysis()
    
    with tab4:
        handle_qa_and_compare()

def handle_upload_and_extract():
    """Simple upload and extraction"""
    st.header("📤 Upload PDFs & Extract Financial Data")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files", 
        type=['pdf'], 
        accept_multiple_files=True,
        help="Upload 2-5 company annual reports"
    )
    
    if uploaded_files:
        st.write(f"📄 {len(uploaded_files)} files uploaded")
        
        # Company name inputs
        company_names = []
        cols = st.columns(min(len(uploaded_files), 3))
        for i, file in enumerate(uploaded_files):
            with cols[i % 3]:
                name = st.text_input(f"Company name for {file.name}", 
                                   value=file.name.replace('.pdf', ''), 
                                   key=f"company_{i}")
                company_names.append(name)
        
        if st.button("🚀 Extract Financial Data", type="primary"):
            extract_financial_data(uploaded_files, company_names)

def extract_financial_data(uploaded_files, company_names):
    """Extract financial data from uploaded PDFs"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, (file, company_name) in enumerate(zip(uploaded_files, company_names)):
        progress_bar.progress((i + 0.5) / len(uploaded_files))
        status_text.text(f"Processing {company_name}...")
        
        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(file.read())
            temp_file_path = temp_file.name
        
        try:
            # Parse PDF
            parser = PDFParser()
            report = parser.parse_pdf(temp_file_path, company_name, 2024)
            
            # Calculate financial metrics
            calculator = FinancialCalculator()
            statements = parser.extract_financial_statements(report)
            figures = calculator.extract_key_figures(report, statements)
            metrics = calculator.calculate_ratios(figures)
            
            # Store in session state
            if 'company_metrics' not in st.session_state:
                st.session_state.company_metrics = []
            
            metrics.company = company_name
            st.session_state.company_metrics.append(metrics)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
            
        except Exception as e:
            st.error(f"Error processing {company_name}: {str(e)}")
        finally:
            os.unlink(temp_file_path)
    
    status_text.text("✅ Processing complete!")
    st.success(f"Successfully processed {len(company_names)} companies!")

def show_financial_data():
    """Show financial data and metrics"""
    st.header("📋 Financial Data & Metrics")
    
    if 'company_metrics' not in st.session_state or not st.session_state.company_metrics:
        st.info("Please upload and process PDFs first.")
        return
    
    # Display metrics overview
    from core.viz import FinancialVisualizer
    visualizer = FinancialVisualizer()
    visualizer.create_metrics_overview_cards(st.session_state.company_metrics)
    
    # Comparison charts
    st.subheader("📊 Metrics Comparison")
    selected_categories = st.multiselect(
        "Select ratio categories to compare:",
        ["profitability", "growth", "efficiency", "leverage", "cash_quality"],
        default=["profitability", "leverage"]
    )
    
    if selected_categories:
        visualizer.create_comparison_charts(st.session_state.company_metrics, selected_categories)

def show_strategic_analysis():
    """Show strategic analysis"""
    st.header("🎯 Strategic Analysis")
    st.info("Strategic analysis features will be available in the next update.")

def handle_qa_and_compare():
    """Handle Q&A and comparison"""
    st.header("🔍 Q&A Compare")
    st.info("Q&A and semantic search features will be available in the next update.")

if __name__ == "__main__":
    main()