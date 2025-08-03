import os
import json
import logging
from typing import Dict, List, Tuple, Optional
from groq import Groq
from django.conf import settings

logger = logging.getLogger(__name__)

class GroqAnalysisService:
    """Service for analyzing curriculum content using Groq API"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama3-8b-8192"  # Fast and capable model
    
    def extract_topics_from_text(self, text: str, subject: str = "general") -> List[Dict]:
        """Extract topics from curriculum text using Groq"""
        try:
            prompt = self._build_topic_extraction_prompt(text, subject)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational content analyzer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            return self._parse_topic_extraction_response(content)
            
        except Exception as e:
            logger.error(f"Error extracting topics with Groq: {str(e)}")
            return []
    
    def analyze_topic_difficulty(self, topic_text: str, context: str = "") -> Dict:
        """Analyze topic difficulty and complexity using Groq"""
        try:
            prompt = self._build_difficulty_analysis_prompt(topic_text, context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in educational difficulty assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            return self._parse_difficulty_response(content)
            
        except Exception as e:
            logger.error(f"Error analyzing difficulty with Groq: {str(e)}")
            return {"difficulty_level": 5, "confidence": 0.0}
    
    def estimate_learning_time(self, topic_text: str, difficulty_level: int, user_profile: Dict) -> Dict:
        """Estimate learning time based on topic and user profile"""
        try:
            prompt = self._build_time_estimation_prompt(topic_text, difficulty_level, user_profile)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in learning time estimation and educational planning."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            return self._parse_time_estimation_response(content)
            
        except Exception as e:
            logger.error(f"Error estimating time with Groq: {str(e)}")
            return {"total_hours": 2.0, "breakdown": {}, "confidence": 0.0}
    
    def identify_prerequisites(self, topic_text: str, all_topics: List[str]) -> List[Dict]:
        """Identify prerequisite relationships between topics"""
        try:
            prompt = self._build_prerequisites_prompt(topic_text, all_topics)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in educational sequencing and prerequisites."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1200
            )
            
            content = response.choices[0].message.content
            return self._parse_prerequisites_response(content)
            
        except Exception as e:
            logger.error(f"Error identifying prerequisites with Groq: {str(e)}")
            return []
    
    def generate_learning_objectives(self, topic_text: str, bloom_level: str = "understand") -> List[str]:
        """Generate learning objectives for a topic"""
        try:
            prompt = self._build_objectives_prompt(topic_text, bloom_level)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert instructional designer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            return self._parse_objectives_response(content)
            
        except Exception as e:
            logger.error(f"Error generating objectives with Groq: {str(e)}")
            return []
    
    def _build_topic_extraction_prompt(self, text: str, subject: str) -> str:
        """Build prompt for topic extraction"""
        return f"""
Analyze the following {subject} curriculum text and extract individual learning topics.

For each topic, provide:
1. Title (concise, clear)
2. Description (2-3 sentences)
3. Type (concept/skill/theory/application/assessment/project/reading)
4. Key concepts (3-5 main points)
5. Estimated difficulty (1-10 scale)
6. Chapter/section reference if mentioned

Format your response as JSON array with this structure:
[
  {{
    "title": "Topic Title",
    "description": "Clear description",
    "type": "concept",
    "key_concepts": ["concept1", "concept2"],
    "difficulty_estimate": 5,
    "chapter_section": "Chapter 1.2",
    "confidence": 0.85
  }}
]

Curriculum Text:
{text[:4000]}

Provide only the JSON array, no additional text.
"""
    
    def _build_difficulty_analysis_prompt(self, topic_text: str, context: str) -> str:
        """Build prompt for difficulty analysis"""
        return f"""
Analyze the difficulty of this learning topic and provide a detailed assessment.

Topic: {topic_text}
Context: {context}

Assess these factors:
1. Conceptual complexity (how abstract/concrete)
2. Prerequisite knowledge required
3. Cognitive load (working memory demand)
4. Typical learner challenges
5. Bloom's taxonomy level

Provide response in JSON format:
{{
  "difficulty_level": 6,
  "complexity_score": 0.7,
  "cognitive_load": 0.6,
  "bloom_taxonomy": "apply",
  "prerequisite_complexity": 0.5,
  "typical_challenges": ["challenge1", "challenge2"],
  "confidence": 0.8,
  "reasoning": "Brief explanation"
}}

Provide only the JSON object, no additional text.
"""
    
    def _build_time_estimation_prompt(self, topic_text: str, difficulty: int, user_profile: Dict) -> str:
        """Build prompt for time estimation"""
        return f"""
Estimate learning time for this topic based on the learner profile.

Topic: {topic_text}
Difficulty Level: {difficulty}/10

Learner Profile:
- Grade Level: {user_profile.get('grade_level', 'college')}
- Knowledge Level: {user_profile.get('knowledge_level', 'intermediate')}
- Learning Style: {user_profile.get('learning_style', 'mixed')}
- Daily Study Hours: {user_profile.get('daily_study_hours', 2.0)}

Estimate time breakdown in JSON format:
{{
  "reading_time_minutes": 45,
  "practice_time_minutes": 90,
  "mastery_time_minutes": 60,
  "review_time_minutes": 30,
  "total_hours": 3.75,
  "confidence": 0.8,
  "factors": ["factor1", "factor2"]
}}

Consider the learner's profile when estimating. Provide only JSON, no additional text.
"""
    
    def _build_prerequisites_prompt(self, topic_text: str, all_topics: List[str]) -> str:
        """Build prompt for prerequisites identification"""
        topics_list = "\n".join([f"- {topic}" for topic in all_topics[:20]])
        
        return f"""
Identify which topics from the list are prerequisites for learning this target topic.

Target Topic: {topic_text}

Available Topics:
{topics_list}

For each prerequisite, provide confidence level and reasoning.

Format as JSON array:
[
  {{
    "prerequisite_topic": "Topic name",
    "confidence": 0.9,
    "relationship_type": "direct|indirect|foundational",
    "reasoning": "Why this is a prerequisite"
  }}
]

Only include topics that are genuinely necessary before learning the target topic.
Provide only the JSON array, no additional text.
"""
    
    def _build_objectives_prompt(self, topic_text: str, bloom_level: str) -> str:
        """Build prompt for learning objectives generation"""
        return f"""
Generate specific, measurable learning objectives for this topic at the {bloom_level} level of Bloom's taxonomy.

Topic: {topic_text}
Target Bloom Level: {bloom_level}

Generate 3-5 objectives that:
1. Use appropriate action verbs for the Bloom level
2. Are specific and measurable
3. Are achievable for the target audience
4. Follow good instructional design principles

Format as JSON array:
[
  "Students will be able to...",
  "Learners can...",
  "By the end, students will..."
]

Provide only the JSON array of objectives, no additional text.
"""
    
    def _parse_topic_extraction_response(self, content: str) -> List[Dict]:
        """Parse Groq response for topic extraction"""
        try:
            # Clean content and extract JSON
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing topic extraction JSON: {str(e)}")
            return []
    
    def _parse_difficulty_response(self, content: str) -> Dict:
        """Parse Groq response for difficulty analysis"""
        try:
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing difficulty JSON: {str(e)}")
            return {"difficulty_level": 5, "confidence": 0.0}
    
    def _parse_time_estimation_response(self, content: str) -> Dict:
        """Parse Groq response for time estimation"""
        try:
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing time estimation JSON: {str(e)}")
            return {"total_hours": 2.0, "confidence": 0.0}
    
    def _parse_prerequisites_response(self, content: str) -> List[Dict]:
        """Parse Groq response for prerequisites"""
        try:
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing prerequisites JSON: {str(e)}")
            return []
    
    def _parse_objectives_response(self, content: str) -> List[str]:
        """Parse Groq response for learning objectives"""
        try:
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing objectives JSON: {str(e)}")
            return []
