"""
required_open_webui_version: 0.6.0
description: Content Planner for generating pillar content calendars
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        default_articles_per_month: int = Field(
            default=13,
            description="Default number of articles per month"
        )

    def __init__(self):
        self.valves = self.Valves()

    async def generate_content_calendar(
        self,
        keywords: List[str],
        months: int = 6,
        articles_per_month: int = 13
    ) -> Dict[str, Any]:
        """
        Generate pillar content calendar based on keywords
        
        :param keywords: List of keywords for content planning
        :param months: Number of months to plan (default: 6)
        :param articles_per_month: Number of articles per month (default: 13)
        :return: Content calendar with 6-month 80-article plan
        """
        try:
            total_articles = months * articles_per_month
            
            # Organize keywords into pillars
            pillars = self._organize_into_pillars(keywords)
            
            # Generate calendar
            calendar = self._generate_calendar(pillars, months, articles_per_month)
            
            # Generate article plans
            article_plans = self._generate_article_plans(keywords, total_articles)
            
            return {
                "success": True,
                "months": months,
                "articles_per_month": articles_per_month,
                "total_articles": total_articles,
                "pillars": pillars,
                "calendar": calendar,
                "article_plans": article_plans,
                "summary": {
                    "total_pillars": len(pillars),
                    "articles_per_pillar": total_articles // len(pillars) if pillars else 0,
                    "publishing_schedule": f"{articles_per_month} articles per month for {months} months"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating content calendar: {str(e)}"
            }

    def _organize_into_pillars(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Organize keywords into content pillars"""
        # Simple pillar organization (can be enhanced)
        pillars = []
        
        # Group keywords by theme
        themes = {}
        for keyword in keywords[:20]:  # Top 20 keywords
            # Extract theme (first word or main concept)
            theme = keyword.split()[0] if keyword.split() else keyword
            if theme not in themes:
                themes[theme] = []
            themes[theme].append(keyword)
        
        # Create pillars
        for theme, theme_keywords in list(themes.items())[:5]:  # Top 5 themes
            pillars.append({
                "pillar_name": theme.title(),
                "keywords": theme_keywords,
                "target_articles": len(theme_keywords) * 2
            })
        
        return pillars

    def _generate_calendar(self, pillars: List[Dict[str, Any]], months: int, articles_per_month: int) -> List[Dict[str, Any]]:
        """Generate monthly calendar"""
        calendar = []
        start_date = datetime.now()
        
        for month in range(months):
            month_start = start_date + timedelta(days=30 * month)
            month_name = month_start.strftime("%Y年%m月")
            
            # Distribute articles across weeks
            articles_per_week = articles_per_month // 4
            weeks = []
            
            for week in range(4):
                week_start = month_start + timedelta(days=7 * week)
                week_articles = []
                
                for i in range(articles_per_week):
                    article_idx = week * articles_per_week + i
                    if article_idx < len(pillars) * 2:
                        pillar_idx = article_idx % len(pillars)
                        pillar = pillars[pillar_idx]
                        week_articles.append({
                            "title": f"{pillar['pillar_name']} 相关文章 {article_idx + 1}",
                            "pillar": pillar['pillar_name'],
                            "keywords": pillar['keywords'][:3]
                        })
                
                weeks.append({
                    "week": week + 1,
                    "date": week_start.strftime("%Y-%m-%d"),
                    "articles": week_articles
                })
            
            calendar.append({
                "month": month_name,
                "articles_count": articles_per_month,
                "weeks": weeks
            })
        
        return calendar

    def _generate_article_plans(self, keywords: List[str], total_articles: int) -> List[Dict[str, Any]]:
        """Generate detailed article plans"""
        plans = []
        
        for i in range(min(total_articles, len(keywords) * 2)):
            keyword_idx = i % len(keywords)
            keyword = keywords[keyword_idx]
            
            plans.append({
                "article_number": i + 1,
                "title": f"Complete Guide to {keyword.title()}",
                "target_keyword": keyword,
                "estimated_words": 2000,
                "content_type": "guide",
                "priority": "high" if i < total_articles // 4 else "medium",
                "suggested_sections": [
                    f"What is {keyword}?",
                    f"Benefits of {keyword}",
                    f"How to use {keyword}",
                    f"Best practices for {keyword}",
                    "FAQ"
                ]
            })
        
        return plans


