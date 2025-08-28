"""
雲端 OCR 模組
支援 Google Cloud Vision、Azure Document Intelligence、AWS Textract
"""
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

class OCRProvider(Enum):
    GOOGLE_CLOUD_VISION = "google_cloud_vision"
    AZURE_DOCUMENT_INTELLIGENCE = "azure_document_intelligence" 
    AWS_TEXTRACT = "aws_textract"

@dataclass
class OCRResult:
    text: str
    confidence: float
    bounding_boxes: List[Dict]
    page_number: int
    provider: str

class CloudOCRService:
    """
    雲端 OCR 服務管理器
    """
    
    def __init__(self):
        self.available_providers = self._check_available_providers()
        
    def _check_available_providers(self) -> List[OCRProvider]:
        """檢查可用的 OCR 提供商"""
        available = []
        
        # 檢查 Google Cloud Vision
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or os.getenv('GOOGLE_CLOUD_PROJECT_ID'):
            available.append(OCRProvider.GOOGLE_CLOUD_VISION)
        
        # 檢查 Azure Document Intelligence
        if os.getenv('AZURE_DI_ENDPOINT') and os.getenv('AZURE_DI_KEY'):
            available.append(OCRProvider.AZURE_DOCUMENT_INTELLIGENCE)
        
        # 檢查 AWS Textract
        if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
            available.append(OCRProvider.AWS_TEXTRACT)
        
        return available
    
    def is_available(self) -> bool:
        """檢查是否有可用的 OCR 服務"""
        return len(self.available_providers) > 0
    
    def get_available_providers(self) -> List[str]:
        """獲取可用提供商列表"""
        return [provider.value for provider in self.available_providers]
    
    def extract_text_from_pdf_page(self, pdf_path: str, page_number: int, 
                                   provider: Optional[OCRProvider] = None) -> OCRResult:
        """
        從 PDF 頁面提取文字
        """
        if not self.available_providers:
            return OCRResult(
                text="沒有可用的 OCR 服務，請檢查 API 配置",
                confidence=0.0,
                bounding_boxes=[],
                page_number=page_number,
                provider="none"
            )
        
        # 如果沒有指定提供商，使用第一個可用的
        if provider is None:
            provider = self.available_providers[0]
        
        # 這裡應該實現具體的 OCR 功能
        # 目前返回模擬結果
        return OCRResult(
            text=f"[模擬 OCR 文字 - 第{page_number + 1}頁]\n這是模擬的 OCR 結果。實際使用時需要配置雲端 OCR 服務。",
            confidence=0.7,
            bounding_boxes=[],
            page_number=page_number,
            provider=provider.value
        )

# 模擬 OCR 服務（用於測試）
class MockOCRService:
    """模擬 OCR 服務，用於測試"""
    
    def is_available(self) -> bool:
        return True
    
    def get_available_providers(self) -> List[str]:
        return ["mock_ocr"]
    
    def extract_text_from_pdf_page(self, pdf_path: str, page_number: int, 
                                   provider: Optional[OCRProvider] = None) -> OCRResult:
        return OCRResult(
            text=f"[模擬 OCR 文字 - 第{page_number + 1}頁]\n這是模擬的 OCR 結果。實際使用時需要配置雲端 OCR 服務。",
            confidence=0.7,
            bounding_boxes=[],
            page_number=page_number,
            provider="mock_ocr"
        )