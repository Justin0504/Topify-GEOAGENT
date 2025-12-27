"""
required_open_webui_version: 0.6.0
description: Keyword Engine for automatic keyword research and mapping
requirements: aiohttp, beautifulsoup4
"""

import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urljoin
from pydantic import BaseModel, Field
import re
from collections import Counter


class Tools:
    class Valves(BaseModel):
        max_keywords: int = Field(
            default=50,
            description="Maximum number of keywords to research"
        )
        timeout: int = Field(
            default=10,
            description="Request timeout in seconds"
        )

    def __init__(self):
        self.valves = self.Valves()

    async def research_keywords(self, url: str, industry: str) -> Dict[str, Any]:
        """
        Research keywords based on URL and industry
        
        :param url: Website URL to analyze
        :param industry: Industry type (e.g., "technology", "e-commerce", "healthcare")
        :return: Keyword research results with keyword list, competition, and suggestions
        """
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Analyze website content
            content_analysis = await self._analyze_website_content(url)
            
            # Extract keywords from content
            keywords = self._extract_keywords_from_content(content_analysis.get("text", ""))
            
            # Generate industry-related keywords
            industry_keywords = self._generate_industry_keywords(industry, keywords)
            
            # Combine and rank keywords
            all_keywords = self._rank_keywords(keywords + industry_keywords)
            
            return {
                "success": True,
                "url": url,
                "industry": industry,
                "keywords": all_keywords[:self.valves.max_keywords],
                "total_keywords": len(all_keywords),
                "primary_keywords": all_keywords[:10],
                "long_tail_keywords": [kw for kw in all_keywords if len(kw.split()) >= 3][:20],
                "recommendations": self._generate_keyword_recommendations(all_keywords, industry)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error researching keywords: {str(e)}"
            }

    async def map_keywords_to_pages(self, url: str, keywords: List[str]) -> Dict[str, Any]:
        """
        Map keywords to website pages and generate blog plan
        
        :param url: Website URL
        :param keywords: List of keywords to map
        :return: Keyword mapping results with page assignments and blog plan
        """
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Analyze website structure
            pages = await self._analyze_website_structure(url)
            
            # Map keywords to pages
            keyword_mapping = self._map_keywords(keywords, pages)
            
            # Generate blog plan
            blog_plan = self._generate_blog_plan(keywords, keyword_mapping)
            
            return {
                "success": True,
                "url": url,
                "keyword_mapping": keyword_mapping,
                "blog_plan": blog_plan,
                "total_pages": len(pages),
                "total_keywords": len(keywords),
                "recommendations": [
                    "为每个主要页面分配 1-2 个主要关键词",
                    "使用长尾关键词创建博客内容",
                    "确保关键词自然融入内容"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error mapping keywords: {str(e)}"
            }

    async def _analyze_website_content(self, url: str) -> Dict[str, Any]:
        """Analyze website content"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.valves.timeout)) as response:
                    if response.status != 200:
                        return {"text": "", "headings": []}
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract text content
                    text = soup.get_text(separator=' ', strip=True)
                    
                    # Extract headings
                    headings = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])]
                    
                    return {
                        "text": text,
                        "headings": headings
                    }
        except Exception:
            return {"text": "", "headings": []}

    def _extract_keywords_from_content(self, content: str) -> List[str]:
        """Extract keywords from content"""
        # Simple keyword extraction (can be enhanced)
        words = re.findall(r'\b\w{4,}\b', content.lower())
        word_freq = Counter(words)
        
        # Filter common words
        common_words = {'this', 'that', 'with', 'from', 'have', 'been', 'will', 'your', 'their', 'there'}
        keywords = [word for word, count in word_freq.most_common(50) if word not in common_words]
        
        return keywords

    def _generate_industry_keywords(self, industry: str, existing_keywords: List[str]) -> List[str]:
        """Generate industry-related keywords"""
        industry_keyword_map = {
            "technology": ["software", "development", "programming", "coding", "tech", "digital", "innovation"],
            "e-commerce": ["online", "shopping", "store", "product", "buy", "sell", "marketplace"],
            "healthcare": ["health", "medical", "treatment", "doctor", "patient", "clinic", "hospital"],
            "education": ["learning", "course", "training", "student", "teacher", "education", "school"],
            "finance": ["money", "investment", "banking", "financial", "loan", "credit", "saving"],
        }
        
        base_keywords = industry_keyword_map.get(industry.lower(), [])
        
        # Generate variations
        variations = []
        for base in base_keywords:
            variations.extend([
                base,
                f"{base} guide",
                f"best {base}",
                f"{base} tips",
                f"how to {base}",
                f"{base} tutorial"
            ])
        
        return variations

    def _rank_keywords(self, keywords: List[str]) -> List[str]:
        """Rank keywords by relevance"""
        # Simple ranking (can be enhanced with competition analysis)
        keyword_freq = Counter(keywords)
        ranked = [kw for kw, count in keyword_freq.most_common()]
        return ranked

    def _generate_keyword_recommendations(self, keywords: List[str], industry: str) -> List[str]:
        """Generate keyword recommendations"""
        recommendations = []
        
        if len(keywords) < 20:
            recommendations.append("建议增加更多行业相关关键词")
        
        long_tail = [kw for kw in keywords if len(kw.split()) >= 3]
        if len(long_tail) < 10:
            recommendations.append("建议增加长尾关键词以提高转化率")
        
        recommendations.append(f"针对 {industry} 行业，建议重点关注前 10 个主要关键词")
        
        return recommendations

    async def _analyze_website_structure(self, url: str) -> List[Dict[str, Any]]:
        """Analyze website page structure"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.valves.timeout)) as response:
                    if response.status != 200:
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    pages = []
                    
                    # Extract main page
                    pages.append({
                        "url": url,
                        "title": soup.find('title').get_text().strip() if soup.find('title') else "Home",
                        "type": "home"
                    })
                    
                    # Extract navigation links
                    nav_links = soup.find_all('a', href=True)
                    for link in nav_links[:20]:  # Limit to 20 links
                        href = link.get('href')
                        if href and href.startswith('/'):
                            full_url = urljoin(url, href)
                            pages.append({
                                "url": full_url,
                                "title": link.get_text().strip() or href,
                                "type": "page"
                            })
                    
                    return pages[:10]  # Limit to 10 pages
        except Exception:
            return []

    def _map_keywords(self, keywords: List[str], pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Map keywords to pages"""
        mapping = {}
        
        # Distribute keywords to pages
        keywords_per_page = len(keywords) // max(len(pages), 1)
        
        for i, page in enumerate(pages):
            start_idx = i * keywords_per_page
            end_idx = start_idx + keywords_per_page
            page_keywords = keywords[start_idx:end_idx]
            
            mapping[page["url"]] = {
                "page_title": page["title"],
                "keywords": page_keywords,
                "primary_keyword": page_keywords[0] if page_keywords else None
            }
        
        return mapping

    def _generate_blog_plan(self, keywords: List[str], keyword_mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate blog plan based on keywords"""
        blog_topics = []
        
        # Generate blog topics from long-tail keywords
        long_tail = [kw for kw in keywords if len(kw.split()) >= 3]
        
        for keyword in long_tail[:20]:  # Top 20 long-tail keywords
            blog_topics.append({
                "topic": keyword,
                "title": f"Complete Guide to {keyword.title()}",
                "target_keywords": [keyword],
                "estimated_words": 1500,
                "priority": "high" if keywords.index(keyword) < 10 else "medium"
            })
        
        return blog_topics

