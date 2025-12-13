"""
Classificador de dificuldade de questões
"""
import re
import math
from typing import Dict, List
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class DifficultyAnalysis:
    """Resultado da análise de dificuldade"""
    level: str  # facil, medio, dificil
    score: float  # 0.0 a 1.0
    lexical_score: float
    concept_score: float
    vocabulary_score: float
    explanation: str


class DifficultyClassifier:
    """
    Classificador de dificuldade usando análise híbrida:
    - Análise lexical (Flesch Reading Ease adaptado para português)
    - Complexidade conceitual
    - Nível vocabular
    """
    
    # Palavras técnicas/acadêmicas comuns (aumentam dificuldade)
    TECHNICAL_TERMS = {
        'algoritmo', 'paradigma', 'metodologia', 'epistemológico', 'heurística',
        'ontologia', 'axioma', 'teorema', 'hipótese', 'correlação', 'causalidade',
        'inferência', 'dedução', 'indução', 'abstração', 'concretização',
        'framework', 'arquitetura', 'implementação', 'instância', 'herança',
        'polimorfismo', 'encapsulamento', 'recursividade', 'complexidade'
    }
    
    # Conectivos que indicam raciocínio complexo
    COMPLEX_CONNECTORS = {
        'portanto', 'consequentemente', 'ademais', 'outrossim', 'destarte',
        'não obstante', 'todavia', 'entretanto', 'conquanto', 'porquanto',
        'mormente', 'precipuamente', 'sobretudo', 'malgrado', 'consoante'
    }
    
    def __init__(self):
        self.weights = {
            'lexical': 0.30,
            'concept': 0.50,
            'vocabulary': 0.20
        }
    
    def classify(self, question_text: str, context: str = "") -> DifficultyAnalysis:
        """
        Classifica a dificuldade de uma questão
        
        Args:
            question_text: Texto completo da questão
            context: Contexto original (opcional, para análise conceitual)
            
        Returns:
            DifficultyAnalysis com classificação e scores
        """
        # 1. Análise lexical (Flesch adaptado)
        lexical_score = self._calculate_lexical_score(question_text)
        
        # 2. Complexidade conceitual
        concept_score = self._calculate_concept_score(question_text, context)
        
        # 3. Nível vocabular
        vocabulary_score = self._calculate_vocabulary_score(question_text)
        
        # Score final ponderado
        final_score = (
            lexical_score * self.weights['lexical'] +
            concept_score * self.weights['concept'] +
            vocabulary_score * self.weights['vocabulary']
        )
        
        # Determina nível
        level = self._score_to_level(final_score)
        explanation = self._generate_explanation(level, lexical_score, concept_score, vocabulary_score)
        
        return DifficultyAnalysis(
            level=level,
            score=final_score,
            lexical_score=lexical_score,
            concept_score=concept_score,
            vocabulary_score=vocabulary_score,
            explanation=explanation
        )
    
    def _calculate_lexical_score(self, text: str) -> float:
        """
        Calcula score lexical baseado em Flesch Reading Ease adaptado para português
        
        Fórmula original Flesch: 206.835 - 1.015*(palavras/sentenças) - 84.6*(sílabas/palavras)
        Score alto = fácil de ler
        """
        sentences = self._count_sentences(text)
        words = self._get_words(text)
        word_count = len(words)
        
        if word_count == 0 or sentences == 0:
            return 0.5
        
        syllables = sum(self._count_syllables(word) for word in words)
        
        # Flesch Reading Ease adaptado
        avg_sentence_length = word_count / sentences
        avg_syllables_per_word = syllables / word_count
        
        flesch = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Normaliza para 0-1 (invertido: score alto = mais difícil)
        # Flesch vai de ~0 (muito difícil) a ~100 (muito fácil)
        normalized = 1 - (max(0, min(100, flesch)) / 100)
        
        return normalized
    
    def _calculate_concept_score(self, text: str, context: str = "") -> float:
        """
        Calcula complexidade conceitual baseada em:
        - Quantidade de conceitos técnicos
        - Conectivos de raciocínio complexo
        - Estrutura argumentativa
        """
        text_lower = text.lower()
        words = self._get_words(text)
        word_count = len(words)
        
        if word_count == 0:
            return 0.5
        
        # Conta termos técnicos
        technical_count = sum(1 for word in words if word.lower() in self.TECHNICAL_TERMS)
        technical_ratio = technical_count / word_count
        
        # Conta conectivos complexos
        connector_count = sum(1 for conn in self.COMPLEX_CONNECTORS if conn in text_lower)
        connector_score = min(1.0, connector_count / 3)  # Normaliza para máximo 3
        
        # Analisa estrutura (presença de múltiplas partes)
        has_enumerate = bool(re.search(r'(?:primeiro|segundo|terceiro|a\)|b\)|c\)|I\)|II\)|III\))', text, re.IGNORECASE))
        has_comparison = bool(re.search(r'(?:enquanto|diferente|semelhante|comparado|relação)', text_lower))
        
        structure_score = 0.0
        if has_enumerate:
            structure_score += 0.3
        if has_comparison:
            structure_score += 0.3
        if len(text) > 300:  # Questões longas tendem a ser mais complexas
            structure_score += 0.2
        
        # Combina scores
        concept_score = (technical_ratio * 2 + connector_score + structure_score) / 3
        
        return min(1.0, concept_score)
    
    def _calculate_vocabulary_score(self, text: str) -> float:
        """
        Analisa nível vocabular baseado em:
        - Comprimento médio das palavras
        - Diversidade lexical (type-token ratio)
        - Presença de palavras raras/acadêmicas
        """
        words = self._get_words(text)
        word_count = len(words)
        
        if word_count == 0:
            return 0.5
        
        # Comprimento médio das palavras
        avg_word_length = sum(len(word) for word in words) / word_count
        length_score = min(1.0, (avg_word_length - 4) / 6)  # 4-10 letras normalizado
        
        # Diversidade lexical (type-token ratio)
        unique_words = set(word.lower() for word in words)
        ttr = len(unique_words) / word_count
        diversity_score = ttr  # Já está entre 0-1
        
        # Palavras longas (mais de 10 caracteres)
        long_words = sum(1 for word in words if len(word) > 10)
        long_ratio = long_words / word_count
        
        vocabulary_score = (length_score + diversity_score + long_ratio * 2) / 3
        
        return min(1.0, max(0.0, vocabulary_score))
    
    def _score_to_level(self, score: float) -> str:
        """Converte score numérico para nível categórico"""
        if score < 0.35:
            return "facil"
        elif score < 0.65:
            return "medio"
        else:
            return "dificil"
    
    def _generate_explanation(
        self, 
        level: str, 
        lexical: float, 
        concept: float, 
        vocabulary: float
    ) -> str:
        """Gera explicação da classificação"""
        explanations = {
            "facil": "Questão com linguagem acessível e conceitos básicos.",
            "medio": "Questão com complexidade moderada, requerendo compreensão intermediária.",
            "dificil": "Questão com alta complexidade conceitual e vocabulário técnico avançado."
        }
        
        base = explanations[level]
        
        details = []
        if lexical > 0.6:
            details.append("estrutura textual elaborada")
        if concept > 0.6:
            details.append("múltiplos conceitos interrelacionados")
        if vocabulary > 0.6:
            details.append("vocabulário técnico especializado")
        
        if details:
            base += f" Fatores: {', '.join(details)}."
        
        return base
    
    def _count_sentences(self, text: str) -> int:
        """Conta sentenças no texto"""
        # Considera . ! ? como fim de sentença
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    def _get_words(self, text: str) -> List[str]:
        """Extrai palavras do texto"""
        return re.findall(r'\b[a-záàâãéèêíïóôõöúçñ]+\b', text.lower())
    
    def _count_syllables(self, word: str) -> int:
        """
        Conta sílabas em português (aproximação)
        Regra simplificada: conta vogais, subtrai ditongos
        """
        word = word.lower()
        vowels = 'aáàâãeéèêiíïoóôõuúü'
        
        count = 0
        prev_is_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel
        
        return max(1, count)
