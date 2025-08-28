"""
LLM 模組
支援 Gemini 2.5 Flash-Lite 的調用與回應生成
"""
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# 加載環境變數
load_dotenv()

@dataclass
class QueryResponse:
    company: str
    query: str
    answer: str
    sources: List[str]
    confidence: float

@dataclass
class ComparisonSummary:
    query: str
    individual_responses: List[QueryResponse]
    cross_company_summary: str
    key_differences: List[str]
    insights: List[str]

class GeminiLLMClient:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key or genai is None:
            print("警告: 未設置 GEMINI_API_KEY 或未安裝 google-generativeai，語義查詢功能將不可用")
            self.client = None
        else:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel('gemini-1.5-flash')
    
    def is_available(self) -> bool:
        """檢查 LLM 是否可用"""
        return self.client is not None
    
    def generate_response(self, prompt: str) -> str:
        """生成簡單回應（相容性方法）"""
        if not self.is_available():
            return "LLM 服務不可用，請檢查 API 設定"
        
        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"生成回應時發生錯誤: {str(e)}"
    
    def generate_company_answer(self, company: str, query: str, context_chunks: List[Dict], language: str = 'zh') -> QueryResponse:
        """
        為單一公司生成基於檢索內容的回答
        """
        if not self.is_available():
            return QueryResponse(
                company=company,
                query=query,
                answer="LLM 服務不可用，請檢查 API 設定",
                sources=[],
                confidence=0.0
            )
        
        # 構建上下文
        context_text = "\n\n".join([chunk['text'][:500] for chunk in context_chunks[:3]])
        
        # 構建 prompt
        prompt = f"""你是一位專業的財務分析師。請根據提供的財報內容回答關於 {company} 的問題。

查詢問題: {query}

財報內容:
{context_text}

請提供簡潔而專業的回答，如果資訊不足，請明確說明。"""
        
        try:
            response = self.client.generate_content(prompt)
            sources = [chunk.get('page_ref', '') for chunk in context_chunks]
            
            return QueryResponse(
                company=company,
                query=query,
                answer=response.text,
                sources=list(set(sources)),
                confidence=0.8
            )
            
        except Exception as e:
            return QueryResponse(
                company=company,
                query=query,
                answer=f"生成回答時發生錯誤: {str(e)}",
                sources=[],
                confidence=0.0
            )

# 測試用的簡化版本（當 API 不可用時）
class MockLLMClient:
    """模擬 LLM 客戶端，用於測試"""
    
    def is_available(self) -> bool:
        return True
    
    def generate_response(self, prompt: str) -> str:
        """生成模擬回應"""
        return "這是模擬回應，實際使用時需要配置 Gemini API"
    
    def generate_company_answer(self, company: str, query: str, context_chunks: List[Dict], language: str = 'zh') -> QueryResponse:
        # 簡化的模擬回答
        mock_answer = f"基於提供的財報內容，{company} 在「{query}」方面的表現如下：[這是模擬回答，實際使用時需要配置 Gemini API]"
        
        sources = [chunk.get('page_ref', '') for chunk in context_chunks[:3]]
        
        return QueryResponse(
            company=company,
            query=query,
            answer=mock_answer,
            sources=sources,
            confidence=0.6
        )