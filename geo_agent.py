"""
required_open_webui_version: 0.6.0
description: Generative Engine Optimization Agent
requirements: aiohttp
"""

"""
GEO Agent - Generative Engine Optimization Agent
Optimize content visibility and ranking in AI search and generative engines
"""

import re
import json
from typing import Dict, Any, List, Optional
from collections import Counter
import aiohttp


class Tools:
    """GEO Agent Tools - Generative Engine Optimization Toolset"""

    async def analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """
        Analyze content quality and evaluate its performance in generative engines
        
        :param content: Content text to analyze
        :return: Dictionary containing quality analysis results
        """
        try:
            word_count = len(content.split())
            char_count = len(content)
            sentence_count = len(re.split(r'[.!?]+', content))
            
            # Calculate readability metrics
            avg_words_per_sentence = word_count / max(sentence_count, 1)
            avg_chars_per_word = char_count / max(word_count, 1)
            
            # Detect keyword density
            words = re.findall(r'\b\w+\b', content.lower())
            word_freq = Counter(words)
            top_keywords = word_freq.most_common(10)
            
            # Evaluate structure
            has_headings = bool(re.search(r'^#+\s', content, re.MULTILINE))
            has_lists = bool(re.search(r'^[\*\-\+]\s|^\d+\.\s', content, re.MULTILINE))
            has_links = bool(re.search(r'\[.*?\]\(.*?\)', content))
            
            # Quality scoring
            quality_score = 0
            if word_count >= 300:
                quality_score += 20
            if 15 <= avg_words_per_sentence <= 25:
                quality_score += 20
            if has_headings:
                quality_score += 15
            if has_lists:
                quality_score += 15
            if has_links:
                quality_score += 10
            if word_count >= 1000:
                quality_score += 20
            
            return {
                "success": True,
                "content_length": {
                    "words": word_count,
                    "characters": char_count,
                    "sentences": sentence_count
                },
                "readability": {
                    "avg_words_per_sentence": round(avg_words_per_sentence, 2),
                    "avg_chars_per_word": round(avg_chars_per_word, 2)
                },
                "top_keywords": [{"word": word, "count": count} for word, count in top_keywords],
                "structure": {
                    "has_headings": has_headings,
                    "has_lists": has_lists,
                    "has_links": has_links
                },
                "quality_score": min(quality_score, 100),
                "recommendations": self._generate_quality_recommendations(word_count, avg_words_per_sentence, has_headings, has_lists)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Content analysis error: {str(e)}"
            }

    def _generate_quality_recommendations(self, word_count: int, avg_words: float, has_headings: bool, has_lists: bool) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        if word_count < 300:
            recommendations.append("Content is too short, recommend increasing to at least 300 words for better depth")
        elif word_count < 1000:
            recommendations.append("Content can be further expanded to provide more comprehensive information")
        
        if avg_words < 15:
            recommendations.append("Sentences may be too short, recommend increasing sentence complexity")
        elif avg_words > 25:
            recommendations.append("Sentences may be too long, recommend breaking them down for better readability")
        
        if not has_headings:
            recommendations.append("Recommend adding headings and subheadings to improve structure")
        
        if not has_lists:
            recommendations.append("Recommend using lists to organize information and improve readability")
        
        return recommendations

    async def optimize_for_generative_engines(
        self,
        content: str,
        target_keywords: Optional[List[str]] = None,
        target_questions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Optimize content for generative engines
        
        :param content: Original content text
        :param target_keywords: Target keywords
        :param target_questions: Target questions
        :return: Optimization suggestions
        """
        try:
            analysis = await self.analyze_content_quality(content)
            if not analysis["success"]:
                return analysis
            
            suggestions = []
            optimized_sections = []
            
            # Keyword optimization
            if target_keywords:
                content_lower = content.lower()
                missing_keywords = [kw for kw in target_keywords if kw.lower() not in content_lower]
                if missing_keywords:
                    suggestions.append(f"Recommend including the following keywords in content: {', '.join(missing_keywords)}")
            
            # Question-oriented optimization
            if target_questions:
                content_lower = content.lower()
                qa_sections = []
                for question in target_questions:
                    if question.lower() not in content_lower:
                        qa_sections.append(f"## {question}\n\n[Add detailed answer to this question here]")
                
                if qa_sections:
                    suggestions.append("Recommend adding FAQ section to improve visibility in Q&A scenarios")
                    optimized_sections.append({
                        "type": "faq",
                        "content": "\n\n".join(qa_sections)
                    })
            
            # Structure suggestions
            if not analysis["structure"]["has_headings"]:
                suggestions.append("Add clear heading structure (H1, H2, H3) to help AI understand content hierarchy")
                optimized_sections.append({
                    "type": "structure",
                    "suggestion": "Use Markdown format headings to organize content"
                })
            
            # Metadata suggestions
            meta_suggestions = {
                "title": self._extract_suggested_title(content),
                "description": self._extract_suggested_description(content),
                "tags": analysis["top_keywords"][:5]
            }
            
            return {
                "success": True,
                "original_analysis": analysis,
                "optimization_suggestions": suggestions,
                "optimized_sections": optimized_sections,
                "metadata_suggestions": meta_suggestions,
                "seo_score": self._calculate_seo_score(content, target_keywords, analysis)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Optimization analysis error: {str(e)}"
            }

    def _extract_suggested_title(self, content: str, max_length: int = 60) -> str:
        """Extract suggested title from content"""
        # Try to find the first heading
        heading_match = re.search(r'^#+\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1).strip()
            if len(title) <= max_length:
                return title
        
        # Use the first sentence
        first_sentence = re.split(r'[.!?]+', content)[0].strip()
        if len(first_sentence) <= max_length:
            return first_sentence
        
        # Truncate
        return first_sentence[:max_length-3] + "..."

    def _extract_suggested_description(self, content: str, max_length: int = 160) -> str:
        """Extract suggested description from content"""
        # Remove Markdown formatting
        clean_content = re.sub(r'[#*_\[\]()]', '', content)
        # Take first 160 characters
        description = clean_content.strip()[:max_length]
        if len(clean_content) > max_length:
            description = description.rsplit(' ', 1)[0] + "..."
        return description

    def _calculate_seo_score(self, content: str, keywords: Optional[List[str]], analysis: Dict) -> int:
        """Calculate SEO/GEO score"""
        score = analysis.get("quality_score", 0)
        
        if keywords:
            content_lower = content.lower()
            keyword_matches = sum(1 for kw in keywords if kw.lower() in content_lower)
            score += min(keyword_matches * 10, 30)
        
        return min(score, 100)

    async def generate_structured_content(
        self,
        topic: str,
        outline: Optional[List[str]] = None,
        target_length: int = 1000
    ) -> Dict[str, Any]:
        """
        Generate structured content optimized for generative engines
        
        :param topic: Content topic
        :param outline: Content outline
        :param target_length: Target word count
        :return: Structured content
        """
        try:
            # Generate basic structure
            structure = {
                "title": f"Complete Guide to {topic}",
                "meta_description": f"Deep dive into {topic}, including definitions, applications, best practices and comprehensive information.",
                "sections": []
            }
            
            if outline:
                for section in outline:
                    structure["sections"].append({
                        "heading": section,
                        "content_placeholder": f"[Add detailed content about {section} here, recommend 200-300 words]",
                        "keywords": [],
                        "questions": []
                    })
            else:
                # Default structure
                default_sections = [
                    f"What is {topic}",
                    f"Key Features of {topic}",
                    f"Applications of {topic}",
                    f"How to Get Started with {topic}",
                    "Best Practices and Considerations"
                ]
                
                for section in default_sections:
                    structure["sections"].append({
                        "heading": section,
                        "content_placeholder": f"[Add detailed content about {section} here]",
                        "keywords": [],
                        "questions": []
                    })
            
            # Generate FAQ section
            faq_section = {
                "heading": "Frequently Asked Questions",
                "questions": [
                    f"What is {topic}?",
                    f"What are the advantages of {topic}?",
                    f"How to use {topic}?",
                    f"What scenarios is {topic} suitable for?"
                ]
            }
            
            return {
                "success": True,
                "topic": topic,
                "target_length": target_length,
                "structure": structure,
                "faq_section": faq_section,
                "optimization_tips": [
                    "Use clear subheadings to organize content",
                    "Include relevant keywords but keep it natural",
                    "Answer questions users might ask",
                    "Provide specific examples and data",
                    "Use lists and tables to improve readability"
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating structured content: {str(e)}"
            }

    async def analyze_competitor_content(
        self,
        url: Optional[str] = None,
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze competitor content and extract optimization strategies
        
        :param url: Content URL
        :param content: Content text
        :return: Competitor analysis results
        """
        try:
            if url and not content:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            content = await response.text()
                        else:
                            return {
                                "success": False,
                                "error": f"Unable to fetch URL content: {response.status}"
                            }
            
            if not content:
                return {
                    "success": False,
                    "error": "URL or content must be provided"
                }
            
            # Analyze content
            analysis = await self.analyze_content_quality(content)
            
            # Extract key information
            headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
            links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
            
            # Extract keywords
            words = re.findall(r'\b\w{4,}\b', content.lower())
            keyword_freq = Counter(words)
            top_keywords = keyword_freq.most_common(20)
            
            return {
                "success": True,
                "content_analysis": analysis,
                "structure_analysis": {
                    "headings_count": len(headings),
                    "headings": headings[:10],
                    "links_count": len(links),
                    "links": links[:10]
                },
                "keyword_analysis": {
                    "top_keywords": [{"word": word, "frequency": freq} for word, freq in top_keywords],
                    "keyword_density": {word: round(freq/len(words)*100, 2) for word, freq in top_keywords[:10]}
                },
                "optimization_insights": [
                    "Focus on how high-frequency keywords are used",
                    "Learn their content structure organization methods",
                    "Reference their linking strategy",
                    "Analyze their use of headings and subheadings"
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error analyzing competitor content: {str(e)}"
            }

    async def generate_meta_tags(
        self,
        title: str,
        description: str,
        keywords: List[str],
        content_type: str = "article"
    ) -> Dict[str, Any]:
        """
        Generate meta tags optimized for generative engines
        
        :param title: Page title
        :param description: Page description
        :param keywords: Keywords list
        :param content_type: Content type
        :return: Meta tags
        """
        try:
            meta_tags = {
                "html_meta": {
                    "title": title,
                    "description": description,
                    "keywords": ", ".join(keywords),
                    "og:title": title,
                    "og:description": description,
                    "og:type": content_type,
                    "twitter:card": "summary_large_image",
                    "twitter:title": title,
                    "twitter:description": description
                },
                "structured_data": {
                    "@context": "https://schema.org",
                    "@type": "Article" if content_type == "article" else "WebPage",
                    "headline": title,
                    "description": description,
                    "keywords": keywords
                },
                "recommendations": [
                    "Ensure title contains main keywords",
                    "Description should be between 150-160 characters",
                    "Use relevant structured data",
                    "Optimize social media sharing tags"
                ]
            }
            
            return {
                "success": True,
                "meta_tags": meta_tags,
                "validation": {
                    "title_length": len(title),
                    "title_optimal": 50 <= len(title) <= 60,
                    "description_length": len(description),
                    "description_optimal": 150 <= len(description) <= 160,
                    "keywords_count": len(keywords)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating meta tags: {str(e)}"
            }
