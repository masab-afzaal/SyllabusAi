# analysis/services/huggingface_service.py
import logging
from typing import Dict, List, Tuple
import requests
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)

class HuggingFaceAnalysisService:
    """Service for content analysis using Hugging Face models"""
    
    def __init__(self):
        self.api_token = getattr(settings, 'HUGGINGFACE_API_KEY', None)
        self.api_url = "https://api-inference.huggingface.co/models/"
        
        # Initialize local models for basic tasks
        self._init_local_models()
    
    def _init_local_models(self):
        """Initialize local Hugging Face models"""
        try:
            # Text classification model for educational content
            self.classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                return_all_scores=True
            )
            
            # Sentiment analysis for difficulty assessment
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Named entity recognition for concept extraction
            self.ner = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
            
            logger.info("HuggingFace local models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing HuggingFace models: {str(e)}")
            self.classifier = None
            self.sentiment_analyzer = None
            self.ner = None
    
    def classify_educational_content(self, text: str) -> Dict:
        """Classify educational content type and domain"""
        try:
            # Use API for better classification if available
            if self.api_token:
                return self._api_classify_content(text)
            else:
                return self._local_classify_content(text)
                
        except Exception as e:
            logger.error(f"Error classifying content: {str(e)}")
            return {"classification": "unknown", "confidence": 0.0}
    
    def extract_key_concepts(self, text: str) -> List[Dict]:
        """Extract key concepts and entities from text"""
        try:
            concepts = []
            
            # Named Entity Recognition
            if self.ner:
                entities = self.ner(text)
                for entity in entities:
                    if entity['score'] > 0.7:  # High confidence entities
                        concepts.append({
                            'concept': entity['word'],
                            'type': entity['entity_group'],
                            'confidence': entity['score'],
                            'source': 'ner'
                        })
            
            # Keyword extraction using TF-IDF
            keywords = self._extract_keywords_tfidf(text)
            for keyword, score in keywords:
                concepts.append({
                    'concept': keyword,
                    'type': 'keyword',
                    'confidence': score,
                    'source': 'tfidf'
                })
            
            return concepts[:10]  # Top 10 concepts
            
        except Exception as e:
            logger.error(f"Error extracting concepts: {str(e)}")
            return []
    
    def assess_text_complexity(self, text: str) -> Dict:
        """Assess text complexity using multiple metrics"""
        try:
            complexity_metrics = {}
            
            # Lexical diversity
            words = text.lower().split()
            unique_words = len(set(words))
            total_words = len(words)
            lexical_diversity = unique_words / total_words if total_words > 0 else 0
            
            # Sentence complexity
            sentences = text.split('.')
            avg_sentence_length = total_words / len(sentences) if sentences else 0
            
            # Technical term density using NER
            technical_terms = 0
            if self.ner:
                entities = self.ner(text)
                technical_terms = len([e for e in entities if e['score'] > 0.8])
            
            technical_density = technical_terms / total_words if total_words > 0 else 0
            
            # Overall complexity score (0-1)
            complexity_score = min(
                (lexical_diversity * 0.3 + 
                 min(avg_sentence_length / 20, 1.0) * 0.4 + 
                 technical_density * 0.3), 
                1.0
            )
            
            return {
                'complexity_score': complexity_score,
                'lexical_diversity': lexical_diversity,
                'avg_sentence_length': avg_sentence_length,
                'technical_density': technical_density,
                'total_words': total_words,
                'confidence': 0.8
            }
            
        except Exception as e:
            logger.error(f"Error assessing complexity: {str(e)}")
            return {'complexity_score': 0.5, 'confidence': 0.0}
    
    def cluster_topics(self, topics_text: List[str], n_clusters: int = None) -> Dict:
        """Cluster topics into related groups"""
        try:
            if len(topics_text) < 2:
                return {'clusters': [0] * len(topics_text), 'cluster_labels': []}
            
            # TF-IDF vectorization
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            vectors = vectorizer.fit_transform(topics_text)
            
            # Determine optimal number of clusters
            if n_clusters is None:
                n_clusters = min(max(2, len(topics_text) // 3), 8)
            
            # K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(vectors)
            
            # Generate cluster descriptions
            feature_names = vectorizer.get_feature_names_out()
            cluster_descriptions = []
            
            for i in range(n_clusters):
                # Get top features for this cluster
                cluster_center = kmeans.cluster_centers_[i]
                top_indices = cluster_center.argsort()[-5:][::-1]
                top_features = [feature_names[idx] for idx in top_indices]
                cluster_descriptions.append(' '.join(top_features))
            
            return {
                'clusters': cluster_labels.tolist(),
                'cluster_descriptions': cluster_descriptions,
                'n_clusters': n_clusters,
                'confidence': 0.7
            }
            
        except Exception as e:
            logger.error(f"Error clustering topics: {str(e)}")
            return {'clusters': [0] * len(topics_text), 'cluster_labels': []}
    
    def analyze_learning_style_suitability(self, text: str) -> Dict:
        """Analyze how suitable content is for different learning styles"""
        try:
            # Analyze text characteristics
            visual_indicators = ['diagram', 'chart', 'graph', 'image', 'visual', 'picture', 'illustration']
            auditory_indicators = ['listen', 'discuss', 'explain', 'verbal', 'audio', 'presentation', 'lecture']
            kinesthetic_indicators = ['practice', 'hands-on', 'exercise', 'activity', 'build', 'create', 'experiment']
            reading_indicators = ['read', 'text', 'article', 'book', 'document', 'write', 'note']
            
            text_lower = text.lower()
            
            visual_score = sum(1 for indicator in visual_indicators if indicator in text_lower)
            auditory_score = sum(1 for indicator in auditory_indicators if indicator in text_lower)
            kinesthetic_score = sum(1 for indicator in kinesthetic_indicators if indicator in text_lower)
            reading_score = sum(1 for indicator in reading_indicators if indicator in text_lower)
            
            total_score = visual_score + auditory_score + kinesthetic_score + reading_score
            
            if total_score == 0:
                # Default equal distribution
                return {
                    'visual': 0.5,
                    'auditory': 0.5,
                    'kinesthetic': 0.5,
                    'reading': 0.5,
                    'confidence': 0.3
                }
            
            return {
                'visual': min(visual_score / total_score + 0.2, 1.0),
                'auditory': min(auditory_score / total_score + 0.2, 1.0),
                'kinesthetic': min(kinesthetic_score / total_score + 0.2, 1.0),
                'reading': min(reading_score / total_score + 0.2, 1.0),
                'confidence': 0.6
            }
            
        except Exception as e:
            logger.error(f"Error analyzing learning style suitability: {str(e)}")
            return {'visual': 0.5, 'auditory': 0.5, 'kinesthetic': 0.5, 'reading': 0.5, 'confidence': 0.0}
    
    def _api_classify_content(self, text: str) -> Dict:
        """Use HuggingFace API for content classification"""
        try:
            headers = {"Authorization": f"Bearer {self.api_token}"}
            
            # Use a pre-trained model for educational content classification
            model_url = self.api_url + "facebook/bart-large-mnli"
            
            candidate_labels = [
                "mathematics", "science", "engineering", "computer science",
                "literature", "history", "languages", "business", "arts"
            ]
            
            payload = {
                "inputs": text[:512],  # Limit text length
                "parameters": {"candidate_labels": candidate_labels}
            }
            
            response = requests.post(model_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "classification": result["labels"][0],
                    "confidence": result["scores"][0],
                    "all_scores": dict(zip(result["labels"], result["scores"]))
                }
            else:
                logger.error(f"HuggingFace API error: {response.status_code}")
                return {"classification": "unknown", "confidence": 0.0}
                
        except Exception as e:
            logger.error(f"Error with HuggingFace API classification: {str(e)}")
            return {"classification": "unknown", "confidence": 0.0}
    
    def _local_classify_content(self, text: str) -> Dict:
        """Use local models for content classification"""
        try:
            # Simple keyword-based classification as fallback
            subject_keywords = {
                "mathematics": ["math", "algebra", "calculus", "geometry", "statistics", "equation"],
                "science": ["physics", "chemistry", "biology", "experiment", "hypothesis", "theory"],
                "engineering": ["design", "system", "technical", "engineering", "implementation"],
                "computer_science": ["programming", "algorithm", "software", "code", "computer", "data"],
                "literature": ["literature", "poetry", "novel", "writing", "author", "analysis"],
                "history": ["history", "historical", "century", "period", "civilization", "event"],
                "languages": ["language", "grammar", "vocabulary", "pronunciation", "translation"],
                "business": ["business", "management", "marketing", "finance", "strategy", "economics"],
                "arts": ["art", "creative", "design", "aesthetic", "artistic", "visual"]
            }
            
            text_lower = text.lower()
            scores = {}
            
            for subject, keywords in subject_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                scores[subject] = score
            
            best_match = max(scores, key=scores.get) if scores else "unknown"
            max_score = scores.get(best_match, 0)
            total_matches = sum(scores.values())
            
            confidence = max_score / total_matches if total_matches > 0 else 0.0
            
            return {
                "classification": best_match,
                "confidence": confidence,
                "all_scores": scores
            }
            
        except Exception as e:
            logger.error(f"Error with local classification: {str(e)}")
            return {"classification": "unknown", "confidence": 0.0}
    
    def _extract_keywords_tfidf(self, text: str, max_keywords: int = 5) -> List[Tuple[str, float]]:
        """Extract keywords using TF-IDF"""
        try:
            # Create a simple corpus with the text
            corpus = [text]
            
            vectorizer = TfidfVectorizer(
                max_features=50,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1
            )
            
            tfidf_matrix = vectorizer.fit_transform(corpus)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get TF-IDF scores
            scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return keyword_scores[:max_keywords]
            
        except Exception as e:
            logger.error(f"Error extracting keywords with TF-IDF: {str(e)}")
            return []
