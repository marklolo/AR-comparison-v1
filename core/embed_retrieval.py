"""
向量檢索模組
支援文本嵌入和向量檢索功能
"""
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

try:
    import numpy as np
except ImportError:
    np = None

try:
    import faiss
except ImportError:
    faiss = None
    
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# 加載環境變數
load_dotenv()

class EmbeddingService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = 'models/text-embedding-004'
        
        if not self.api_key or genai is None:
            print("警告: 未設置 GEMINI_API_KEY 或未安裝 google-generativeai，向量檢索功能將使用模擬模式")
            self.client = None
        else:
            genai.configure(api_key=self.api_key)
            self.client = genai
    
    def is_available(self) -> bool:
        """檢查嵌入服務是否可用"""
        return self.client is not None
    
    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """
        生成文本嵌入向量
        """
        if not self.is_available():
            return self._generate_mock_embedding(text)
        
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document"
            )
            
            embedding = np.array(result['embedding'], dtype=np.float32)
            return embedding
            
        except Exception as e:
            print(f"嵌入生成失敗: {e}")
            return self._generate_mock_embedding(text)
    
    def embed_query(self, query: str) -> Optional[np.ndarray]:
        """
        生成查詢嵌入向量
        """
        if not self.is_available():
            return self._generate_mock_embedding(query)
        
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=query,
                task_type="retrieval_query"
            )
            
            embedding = np.array(result['embedding'], dtype=np.float32)
            return embedding
            
        except Exception as e:
            print(f"查詢嵌入生成失敗: {e}")
            return self._generate_mock_embedding(query)
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        批量生成嵌入向量
        """
        embeddings = []
        
        for text in texts:
            embedding = self.embed_text(text)
            if embedding is not None:
                embeddings.append(embedding)
            else:
                embeddings.append(np.zeros(768, dtype=np.float32))
        
        return embeddings
    
    def _generate_mock_embedding(self, text: str, dim: int = 768) -> np.ndarray:
        """
        生成模擬嵌入向量（基於文本哈希）
        """
        # 使用文本哈希生成確定性的模擬向量
        np.random.seed(hash(text) % (2**32))
        embedding = np.random.normal(0, 1, dim).astype(np.float32)
        # 正規化
        embedding = embedding / np.linalg.norm(embedding)
        return embedding

class VectorRetriever:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.index = None
        self.chunks = []
        self.dimension = 768
    
    def build_index(self, chunks: List[Dict]) -> bool:
        """
        建立向量索引
        """
        if not chunks:
            print("沒有內容用於建立索引")
            return False
        
        print(f"正在為 {len(chunks)} 個文檔片段建立向量索引...")
        
        # 提取文本
        texts = [chunk['text'] for chunk in chunks]
        
        # 生成嵌入向量
        embeddings = self.embedding_service.embed_batch(texts)
        
        if not embeddings:
            print("嵌入向量生成失敗")
            return False
        
        # 建立 FAISS 索引
        embeddings_matrix = np.array(embeddings).astype(np.float32)
        self.dimension = embeddings_matrix.shape[1]
        
        if faiss is not None:
            self.index = faiss.IndexFlatIP(self.dimension)
            faiss.normalize_L2(embeddings_matrix)
            self.index.add(embeddings_matrix)
        
        # 保存文檔片段
        self.chunks = chunks
        
        print(f"向量索引建立完成")
        return True
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        執行向量檢索
        """
        if self.index is None or not self.chunks:
            print("向量索引未建立")
            return []
        
        # 生成查詢向量
        query_embedding = self.embedding_service.embed_query(query)
        if query_embedding is None:
            print("查詢向量生成失敗")
            return []
        
        # 正規化查詢向量
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        if faiss is not None:
            faiss.normalize_L2(query_embedding)
        
        results = []
        
        if faiss is not None and self.index is not None:
            # 執行搜索
            scores, indices = self.index.search(query_embedding, min(top_k, len(self.chunks)))
            
            for score, idx in zip(scores[0], indices[0]):
                if idx >= len(self.chunks):
                    continue
                
                chunk = self.chunks[idx]
                result = {
                    'chunk_id': chunk['chunk_id'],
                    'text': chunk['text'],
                    'page_ref': chunk.get('page_ref', ''),
                    'doc_id': chunk.get('doc_id', ''),
                    'similarity_score': float(score),
                    'section_type': chunk.get('section_type', 'text')
                }
                results.append(result)
        
        return results

class SemanticSearchEngine:
    """
    語義搜索引擎主類
    """
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.retriever = VectorRetriever(self.embedding_service)
    
    def initialize_from_reports(self, reports: List[Dict]) -> bool:
        """
        從報告初始化搜索引擎
        """
        all_chunks = []
        
        # 收集所有文檔片段
        for report in reports:
            if hasattr(report, 'sections'):
                from core.parse_pdf import PDFParser
                parser = PDFParser()
                chunks = parser.slice_content_for_search(report)
                all_chunks.extend(chunks)
        
        # 建立索引
        return self.retriever.build_index(all_chunks)
    
    def search_semantic(self, query: str, top_k: int = 10) -> Dict[str, List[Dict]]:
        """
        執行語義搜索，返回按公司分組的結果
        """
        print(f"🔍 執行語義搜索: '{query}'")
        
        # 執行搜索
        results = self.retriever.search(query, top_k)
        
        if not results:
            return {}
        
        # 按公司分組結果
        grouped_results = {}
        for result in results:
            company = result.get('doc_id', '').split('_')[0] if result.get('doc_id') else 'unknown'
            if company not in grouped_results:
                grouped_results[company] = []
            grouped_results[company].append(result)
        
        return grouped_results
    
    def is_ready(self) -> bool:
        """
        檢查搜索引擎是否就緒
        """
        return (self.retriever.index is not None and 
                len(self.retriever.chunks) > 0)