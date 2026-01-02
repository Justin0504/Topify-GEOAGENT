"""
required_open_webui_version: 0.6.0
description: GEO Generator for AI prompt expansion and monitoring
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        default_prompts_count: int = Field(
            default=40,
            description="Default number of prompts to generate"
        )

    def __init__(self):
        self.valves = self.Valves()

    async def generate_prompts(
        self,
        product_description: str,
        num_prompts: int = 40
    ) -> Dict[str, Any]:
        """
        Generate AI prompts based on product/service description
        
        :param product_description: Product or service description
        :param num_prompts: Number of prompts to generate (default: 40)
        :return: Generated prompts and monitoring templates
        """
        try:
            # Extract key concepts
            key_concepts = self._extract_concepts(product_description)
            
            # Generate prompt variations
            prompts = self._generate_prompt_variations(product_description, key_concepts, num_prompts)
            
            # Generate monitoring templates
            monitoring_templates = self._generate_monitoring_templates(product_description, key_concepts)
            
            return {
                "success": True,
                "product_description": product_description,
                "key_concepts": key_concepts,
                "prompts": prompts,
                "total_prompts": len(prompts),
                "monitoring_templates": monitoring_templates,
                "categories": {
                    "informational": [p for p in prompts if "what" in p.lower() or "介绍" in p][:10],
                    "comparison": [p for p in prompts if "compare" in p.lower() or "对比" in p][:10],
                    "how_to": [p for p in prompts if "how" in p.lower() or "如何" in p][:10],
                    "best_practices": [p for p in prompts if "best" in p.lower() or "最佳" in p][:10]
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating prompts: {str(e)}"
            }

    def _extract_concepts(self, description: str) -> List[str]:
        """Extract key concepts from description"""
        # Simple concept extraction (can be enhanced with NLP)
        words = description.lower().split()
        # Filter meaningful words (length > 3)
        concepts = [w for w in words if len(w) > 3]
        return concepts[:10]  # Top 10 concepts

    def _generate_prompt_variations(self, description: str, concepts: List[str], num_prompts: int) -> List[str]:
        """Generate prompt variations"""
        prompts = []
        
        # Base prompt templates
        templates = [
            "What is {product}?",
            "How does {product} work?",
            "Benefits of {product}",
            "Best practices for {product}",
            "How to use {product}",
            "Compare {product} with alternatives",
            "Guide to {product}",
            "Tips for {product}",
            "Introduction to {product}",
            "Complete guide to {product}",
            "什么是 {product}？",
            "{product} 的工作原理",
            "{product} 的优势",
            "{product} 的最佳实践",
            "如何使用 {product}",
            "{product} 与其他产品的对比",
            "{product} 指南",
            "{product} 技巧",
            "{product} 介绍",
            "{product} 完整指南"
        ]
        
        # Generate variations
        for template in templates:
            if len(prompts) >= num_prompts:
                break
            prompt = template.format(product=description[:50])  # Limit length
            prompts.append(prompt)
        
        # Add concept-based prompts
        for concept in concepts[:10]:
            if len(prompts) >= num_prompts:
                break
            prompts.extend([
                f"关于 {concept} 的详细信息",
                f"{concept} 相关的最佳实践",
                f"如何优化 {concept}"
            ])
        
        return prompts[:num_prompts]

    def _generate_monitoring_templates(self, description: str, concepts: List[str]) -> List[Dict[str, Any]]:
        """Generate monitoring templates"""
        templates = []
        
        for concept in concepts[:5]:
            templates.append({
                "keyword": concept,
                "search_queries": [
                    f"{concept} 是什么",
                    f"如何 {concept}",
                    f"{concept} 最佳实践",
                    f"{concept} 教程"
                ],
                "monitoring_frequency": "weekly",
                "metrics": ["排名", "点击率", "转化率"]
            })
        
        return templates


