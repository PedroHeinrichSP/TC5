"""
Segmentador de tópicos usando TF-IDF e K-Means
"""
import re
from typing import List, Tuple, Dict
from dataclasses import dataclass
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import structlog

logger = structlog.get_logger()


@dataclass
class TopicSegment:
    """Representa um segmento de texto com tópico identificado"""
    topic: str
    content: str
    keywords: List[str]
    relevance_score: float


class TopicSegmenter:
    """
    Segmenta texto em tópicos usando TF-IDF e clustering K-Means
    """
    
    # Stopwords em português
    PORTUGUESE_STOPWORDS = {
        'a', 'à', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo',
        'as', 'até', 'com', 'como', 'da', 'das', 'de', 'dela', 'delas', 'dele',
        'deles', 'depois', 'do', 'dos', 'e', 'ela', 'elas', 'ele', 'eles', 'em',
        'entre', 'era', 'eram', 'essa', 'essas', 'esse', 'esses', 'esta', 'estas',
        'este', 'estes', 'eu', 'foi', 'foram', 'há', 'isso', 'isto', 'já', 'lhe',
        'lhes', 'lo', 'mas', 'me', 'mesmo', 'meu', 'minha', 'muito', 'na', 'não',
        'nas', 'nem', 'no', 'nos', 'nós', 'nossa', 'nossas', 'nosso', 'nossos',
        'num', 'numa', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo', 'pelos',
        'por', 'qual', 'quando', 'que', 'quem', 'são', 'se', 'sem', 'seu', 'seus',
        'só', 'sua', 'suas', 'também', 'te', 'tem', 'tinha', 'tinham', 'tu', 'tua',
        'tuas', 'tudo', 'um', 'uma', 'umas', 'uns', 'você', 'vocês', 'vos'
    }
    
    def __init__(self, n_topics: int = 5, min_segment_words: int = 100):
        self.n_topics = n_topics
        self.min_segment_words = min_segment_words
        
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            stop_words=list(self.PORTUGUESE_STOPWORDS),
            min_df=1,
            max_df=0.95
        )
        
        self.kmeans = None
    
    def segment(self, text: str) -> List[TopicSegment]:
        """
        Segmenta o texto em tópicos
        
        Args:
            text: Texto completo para segmentar
            
        Returns:
            Lista de TopicSegment com tópicos identificados
        """
        # Divide texto em parágrafos/chunks
        chunks = self._split_into_chunks(text)
        
        if len(chunks) < 2:
            # Texto muito curto, retorna como único segmento
            return [TopicSegment(
                topic="Conteúdo Principal",
                content=text,
                keywords=self._extract_keywords_simple(text),
                relevance_score=1.0
            )]
        
        # Ajusta número de clusters baseado na quantidade de chunks
        n_clusters = min(self.n_topics, len(chunks))
        
        logger.info(
            "topic_segmentation_started",
            chunks=len(chunks),
            target_topics=n_clusters
        )
        
        # Vetorização TF-IDF
        try:
            tfidf_matrix = self.vectorizer.fit_transform(chunks)
        except ValueError as e:
            logger.warning("tfidf_failed", error=str(e))
            return [TopicSegment(
                topic="Conteúdo Principal",
                content=text,
                keywords=self._extract_keywords_simple(text),
                relevance_score=1.0
            )]
        
        # Clustering K-Means
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = self.kmeans.fit_predict(tfidf_matrix)
        
        # Agrupa chunks por cluster
        segments = self._build_segments(chunks, cluster_labels, tfidf_matrix)
        
        logger.info(
            "topic_segmentation_completed",
            segments=len(segments)
        )
        
        return segments
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """Divide texto em chunks significativos"""
        # Divide por parágrafos duplos primeiro
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_words = len(para.split())
            
            if current_word_count + para_words < self.min_segment_words:
                current_chunk.append(para)
                current_word_count += para_words
            else:
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                current_chunk = [para]
                current_word_count = para_words
        
        # Adiciona último chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def _build_segments(
        self, 
        chunks: List[str], 
        labels: np.ndarray,
        tfidf_matrix
    ) -> List[TopicSegment]:
        """Constrói segmentos a partir dos clusters"""
        segments = []
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Agrupa chunks por cluster
        cluster_chunks: Dict[int, List[str]] = {}
        for chunk, label in zip(chunks, labels):
            if label not in cluster_chunks:
                cluster_chunks[label] = []
            cluster_chunks[label].append(chunk)
        
        # Cria segmentos
        for cluster_id, cluster_texts in sorted(cluster_chunks.items()):
            combined_text = '\n\n'.join(cluster_texts)
            
            # Extrai keywords do centróide do cluster
            centroid = self.kmeans.cluster_centers_[cluster_id]
            top_indices = centroid.argsort()[-10:][::-1]
            keywords = [feature_names[i] for i in top_indices if centroid[i] > 0]
            
            # Gera nome do tópico baseado nas keywords
            topic_name = self._generate_topic_name(keywords)
            
            # Calcula score de relevância (distância média ao centróide)
            cluster_mask = labels == cluster_id
            cluster_vectors = tfidf_matrix[cluster_mask]
            if cluster_vectors.shape[0] > 0:
                distances = np.linalg.norm(
                    cluster_vectors.toarray() - centroid, axis=1
                )
                relevance_score = 1 / (1 + np.mean(distances))
            else:
                relevance_score = 0.5
            
            segments.append(TopicSegment(
                topic=topic_name,
                content=combined_text,
                keywords=keywords[:5],
                relevance_score=float(relevance_score)
            ))
        
        # Ordena por relevância
        segments.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return segments
    
    def _generate_topic_name(self, keywords: List[str]) -> str:
        """Gera nome do tópico baseado nas keywords"""
        if not keywords:
            return "Tópico Geral"
        
        # Usa as 2-3 keywords mais relevantes
        main_keywords = keywords[:3]
        
        # Capitaliza e junta
        topic_parts = [kw.title() for kw in main_keywords if len(kw) > 2]
        
        if not topic_parts:
            return "Tópico Geral"
        
        return " - ".join(topic_parts[:2])
    
    def _extract_keywords_simple(self, text: str) -> List[str]:
        """Extração simples de keywords para textos curtos"""
        words = re.findall(r'\b[a-záàâãéèêíïóôõöúçñ]{4,}\b', text.lower())
        
        # Remove stopwords
        words = [w for w in words if w not in self.PORTUGUESE_STOPWORDS]
        
        # Conta frequência
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Retorna top 5
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:5]]
