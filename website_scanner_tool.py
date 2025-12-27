"""
required_open_webui_version: 0.6.0
description: Website Scanner for Technical SEO Audit - Analyze websites and generate problem lists with repair suggestions
requirements: aiohttp, beautifulsoup4
"""

import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urljoin
from pydantic import BaseModel, Field
import re
import asyncio


class Tools:
    class Valves(BaseModel):
        timeout: int = Field(
            default=10,
            description="Request timeout in seconds"
        )
        check_ssl: bool = Field(
            default=True,
            description="Check SSL certificate"
        )
        max_pages: int = Field(
            default=10,
            description="Maximum number of pages to scan"
        )

    def __init__(self):
        self.valves = self.Valves()

    async def scan_website(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive technical SEO audit of a website
        
        :param url: Website URL to scan (e.g., https://example.com)
        :return: Technical SEO audit results with problems and suggestions
        """
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            results = {
                "success": True,
                "url": url,
                "base_url": base_url,
                "problems": [],
                "suggestions": [],
                "seo_score": 0,
                "technical_issues": [],
                "recommendations": []
            }
            
            # Scan main page
            page_analysis = await self._analyze_page(url)
            results.update(page_analysis)
            
            # Check technical issues
            technical_issues = await self._check_technical_issues(url)
            results["technical_issues"] = technical_issues
            results["problems"].extend(technical_issues)
            
            # Calculate SEO score
            results["seo_score"] = self._calculate_seo_score(results)
            
            # Generate recommendations
            results["recommendations"] = self._generate_recommendations(results)
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error scanning website: {str(e)}"
            }

    async def _analyze_page(self, url: str) -> Dict[str, Any]:
        """Analyze a single page"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.valves.timeout)) as response:
                    if response.status != 200:
                        return {
                            "problems": [f"Page returned status code {response.status}"],
                            "seo_elements": {}
                        }
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Check SEO elements
                    seo_elements = {
                        "title": self._get_title(soup),
                        "meta_description": self._get_meta_description(soup),
                        "meta_keywords": self._get_meta_keywords(soup),
                        "h1_count": len(soup.find_all('h1')),
                        "h1_text": [h1.get_text().strip() for h1 in soup.find_all('h1')],
                        "images_without_alt": len([img for img in soup.find_all('img') if not img.get('alt')]),
                        "links_count": len(soup.find_all('a')),
                        "has_canonical": bool(soup.find('link', rel='canonical')),
                        "has_robots_meta": bool(soup.find('meta', attrs={'name': 'robots'})),
                        "has_open_graph": bool(soup.find('meta', property=re.compile(r'^og:'))),
                        "has_twitter_card": bool(soup.find('meta', attrs={'name': re.compile(r'^twitter:')})),
                        "has_schema": bool(soup.find('script', type='application/ld+json')),
                    }
                    
                    problems = []
                    
                    # Check for problems
                    if not seo_elements["title"]:
                        problems.append("缺少页面标题 (Title)")
                    elif len(seo_elements["title"]) > 60:
                        problems.append(f"标题过长 ({len(seo_elements['title'])} 字符，建议 50-60 字符)")
                    elif len(seo_elements["title"]) < 30:
                        problems.append(f"标题过短 ({len(seo_elements['title'])} 字符，建议至少 30 字符)")
                    
                    if not seo_elements["meta_description"]:
                        problems.append("缺少元描述 (Meta Description)")
                    elif len(seo_elements["meta_description"]) > 160:
                        problems.append(f"元描述过长 ({len(seo_elements['meta_description'])} 字符，建议 150-160 字符)")
                    elif len(seo_elements["meta_description"]) < 120:
                        problems.append(f"元描述过短 ({len(seo_elements['meta_description'])} 字符，建议至少 120 字符)")
                    
                    if seo_elements["h1_count"] == 0:
                        problems.append("缺少 H1 标题")
                    elif seo_elements["h1_count"] > 1:
                        problems.append(f"有多个 H1 标题 ({seo_elements['h1_count']} 个，建议只有 1 个)")
                    
                    if seo_elements["images_without_alt"] > 0:
                        problems.append(f"有 {seo_elements['images_without_alt']} 张图片缺少 alt 属性")
                    
                    if not seo_elements["has_canonical"]:
                        problems.append("缺少 Canonical 标签")
                    
                    if not seo_elements["has_schema"]:
                        problems.append("缺少结构化数据 (Schema.org)")
                    
                    return {
                        "seo_elements": seo_elements,
                        "problems": problems
                    }
                    
        except asyncio.TimeoutError:
            return {
                "problems": ["页面加载超时"],
                "seo_elements": {}
            }
        except Exception as e:
            return {
                "problems": [f"分析页面时出错: {str(e)}"],
                "seo_elements": {}
            }

    def _get_title(self, soup: Any) -> Optional[str]:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else None

    def _get_meta_description(self, soup: Any) -> Optional[str]:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else None

    def _get_meta_keywords(self, soup: Any) -> Optional[str]:
        """Extract meta keywords"""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        return meta_keywords.get('content', '').strip() if meta_keywords else None

    async def _check_technical_issues(self, url: str) -> List[str]:
        """Check technical SEO issues"""
        issues = []
        
        try:
            parsed_url = urlparse(url)
            
            # Check HTTPS
            if parsed_url.scheme != 'https':
                issues.append("网站未使用 HTTPS（安全连接）")
            
            # Check URL structure
            if len(parsed_url.path.split('/')) > 4:
                issues.append("URL 层级过深，可能影响 SEO")
            
            # Check for www vs non-www
            if parsed_url.netloc.startswith('www.'):
                issues.append("建议统一使用 www 或非 www 版本（当前使用 www）")
            
        except Exception as e:
            issues.append(f"检查技术问题时出错: {str(e)}")
        
        return issues

    def _calculate_seo_score(self, results: Dict[str, Any]) -> int:
        """Calculate SEO score (0-100)"""
        score = 100
        problems = results.get("problems", [])
        
        # Deduct points for each problem
        score -= len(problems) * 5
        
        # Check specific issues
        seo_elements = results.get("seo_elements", {})
        if not seo_elements.get("title"):
            score -= 20
        if not seo_elements.get("meta_description"):
            score -= 15
        if seo_elements.get("h1_count", 0) == 0:
            score -= 15
        if seo_elements.get("images_without_alt", 0) > 0:
            score -= 10
        if not seo_elements.get("has_schema"):
            score -= 10
        
        return max(0, min(100, score))

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate repair suggestions"""
        recommendations = []
        problems = results.get("problems", [])
        seo_elements = results.get("seo_elements", {})
        
        if "缺少页面标题" in str(problems):
            recommendations.append("添加页面标题 (Title)，长度建议 50-60 字符，包含主要关键词")
        
        if "缺少元描述" in str(problems):
            recommendations.append("添加元描述 (Meta Description)，长度建议 150-160 字符，吸引用户点击")
        
        if "缺少 H1 标题" in str(problems):
            recommendations.append("添加 H1 标题，每个页面建议只有 1 个 H1，包含主要关键词")
        
        if seo_elements.get("images_without_alt", 0) > 0:
            recommendations.append(f"为 {seo_elements['images_without_alt']} 张图片添加 alt 属性，提高可访问性和 SEO")
        
        if not seo_elements.get("has_schema"):
            recommendations.append("添加结构化数据 (Schema.org)，帮助搜索引擎理解内容")
        
        if not seo_elements.get("has_canonical"):
            recommendations.append("添加 Canonical 标签，避免重复内容问题")
        
        if results.get("seo_score", 0) < 70:
            recommendations.append("整体 SEO 评分较低，建议进行全面优化")
        
        return recommendations

