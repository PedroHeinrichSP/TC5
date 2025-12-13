"""
Tests for AI services - text extraction, topic segmentation, and difficulty classification.
"""
import pytest
from app.services.ai.text_extractor import TextExtractor
from app.services.ai.topic_segmenter import TopicSegmenter
from app.services.ai.difficulty_classifier import DifficultyClassifier


class TestTextExtractor:
    """Test text extraction functionality."""
    
    def test_extract_from_txt(self, sample_text_content):
        """Test extraction from plain text."""
        extractor = TextExtractor()
        result = extractor.extract_from_bytes(
            sample_text_content.encode('utf-8'),
            "test.txt"
        )
        
        assert result is not None
        assert len(result) > 0
        assert "Python" in result
    
    def test_clean_text(self):
        """Test text cleaning removes artifacts."""
        extractor = TextExtractor()
        dirty_text = "  Page 1  \n\nHello   World  \n\n\n Footer text "
        cleaned = extractor.clean_text(dirty_text)
        
        assert "  " not in cleaned or cleaned.count("  ") < dirty_text.count("  ")
        assert cleaned.strip() == cleaned
    
    def test_word_count(self, sample_text_content):
        """Test word counting accuracy."""
        extractor = TextExtractor()
        count = extractor.count_words(sample_text_content)
        
        assert count > 0
        assert count > 50  # Our sample has more than 50 words
    
    def test_validate_minimum_words(self):
        """Test minimum word validation."""
        extractor = TextExtractor()
        
        short_text = "Too short"
        long_text = "This is a longer text. " * 100  # ~500+ words
        
        assert not extractor.validate_minimum_words(short_text, 500)
        assert extractor.validate_minimum_words(long_text, 500)


class TestTopicSegmenter:
    """Test topic segmentation functionality."""
    
    def test_extract_topics(self, sample_text_content):
        """Test topic extraction from text."""
        segmenter = TopicSegmenter()
        topics = segmenter.extract_topics(sample_text_content, max_topics=5)
        
        assert topics is not None
        assert isinstance(topics, list)
        assert len(topics) <= 5
    
    def test_segment_by_topics(self, sample_text_content):
        """Test text segmentation by topics."""
        segmenter = TopicSegmenter()
        segments = segmenter.segment_text(sample_text_content)
        
        assert segments is not None
        assert isinstance(segments, list)
        assert len(segments) > 0
    
    def test_empty_text_handling(self):
        """Test handling of empty text."""
        segmenter = TopicSegmenter()
        topics = segmenter.extract_topics("", max_topics=3)
        
        assert topics is not None
        assert isinstance(topics, list)


class TestDifficultyClassifier:
    """Test difficulty classification functionality."""
    
    def test_classify_easy(self):
        """Test classification of easy content."""
        classifier = DifficultyClassifier()
        
        easy_question = "O que é Python?"
        difficulty = classifier.classify(easy_question)
        
        assert difficulty in ["easy", "medium", "hard"]
    
    def test_classify_hard(self):
        """Test classification of hard content."""
        classifier = DifficultyClassifier()
        
        hard_question = """
        Explique a diferença entre polimorfismo paramétrico e polimorfismo ad-hoc 
        em linguagens de programação com tipagem estática, fornecendo exemplos 
        de implementação em Haskell e comparando com o sistema de tipos do Scala.
        """
        difficulty = classifier.classify(hard_question)
        
        assert difficulty in ["easy", "medium", "hard"]
    
    def test_flesch_reading_score(self):
        """Test Flesch reading ease calculation."""
        classifier = DifficultyClassifier()
        
        simple_text = "The cat sat on the mat."
        complex_text = "The epistemological ramifications of quantum mechanics necessitate reconsideration."
        
        simple_score = classifier.calculate_flesch_score(simple_text)
        complex_score = classifier.calculate_flesch_score(complex_text)
        
        # Simpler text should have higher (easier) score
        assert simple_score > complex_score
    
    def test_vocabulary_level(self):
        """Test vocabulary complexity analysis."""
        classifier = DifficultyClassifier()
        
        simple_text = "I like cats and dogs."
        complex_text = "Implementing polymorphic abstractions requires understanding parametricity."
        
        simple_level = classifier.analyze_vocabulary(simple_text)
        complex_level = classifier.analyze_vocabulary(complex_text)
        
        assert simple_level <= complex_level
    
    def test_batch_classification(self):
        """Test classification of multiple questions."""
        classifier = DifficultyClassifier()
        
        questions = [
            "O que é uma variável?",
            "Explique a diferença entre compilação e interpretação.",
            "Descreva o algoritmo de Dijkstra para encontrar o caminho mais curto em um grafo ponderado."
        ]
        
        difficulties = classifier.classify_batch(questions)
        
        assert len(difficulties) == len(questions)
        assert all(d in ["easy", "medium", "hard"] for d in difficulties)


class TestQuestionValidation:
    """Test question validation utilities."""
    
    def test_validate_multiple_choice_options(self):
        """Test validation of multiple choice options."""
        from app.services.ai.question_service import QuestionService
        
        service = QuestionService()
        
        valid_options = ["A", "B", "C", "D"]
        invalid_options = ["A", "A", "B", "C"]  # Duplicate
        
        assert service.validate_options(valid_options)
        assert not service.validate_options(invalid_options)
    
    def test_validate_question_content(self):
        """Test validation of question content."""
        from app.services.ai.question_service import QuestionService
        
        service = QuestionService()
        
        valid_question = "O que é Python?"
        invalid_question = ""
        
        assert service.validate_content(valid_question)
        assert not service.validate_content(invalid_question)
