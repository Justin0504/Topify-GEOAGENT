"""
title: SEO 分析工具
description: 【网站SEO分析】分析网站流量、排名、关键词 | 【关键词研究】查搜索量、难度、相关词 | 【竞争对手分析】找竞争者、对比网站。支持中文查询，结果可用于生成报告文章。
author: GEO Agent
version: 1.2.0
required_open_webui_version: 0.4.0
requirements: requests
"""

import requests
import json
import re
from typing import Optional, List
from pydantic import BaseModel, Field


class Tools:
    """
    SEO 专业分析工具 - 网站分析、关键词研究、竞争对手分析
    
    ═══════════════════════════════════════════════════════════════
    🎯 快速匹配指南（根据用户说的话选择工具）
    ═══════════════════════════════════════════════════════════════
    
    📊 用户说"分析网站"、"分析xxx.com"、"看网站SEO" 
       → 调用 domain_analysis
       
    📊 用户说"网站的关键词"、"这个网站排名哪些词"、"官网关键词分析"
       → 调用 domain_analysis(action="organic_keywords")
    
    🔍 用户说"研究关键词"、"查某个词的搜索量"、"分析关键词难度"
       → 调用 keyword_research
    
    🏆 用户说"竞争对手"、"竞品分析"、"找竞争者"
       → 调用 competitor_analysis
    
    ═══════════════════════════════════════════════════════════════
    ⚠️ 重要区分："关键词分析" 有两种含义！
    ═══════════════════════════════════════════════════════════════
    
    情况1: "帮我对 topify.ai 做关键词分析" 
           = 分析这个网站排名了哪些关键词
           → domain_analysis(domain="topify.ai", action="organic_keywords")
    
    情况2: "帮我分析'AI工具'这个关键词"
           = 研究某个具体的关键词
           → keyword_research(keyword="AI工具")
    
    判断方法：
    - 用户提供了【网址/域名】→ domain_analysis
    - 用户提供了【关键词/搜索词】→ keyword_research
    
    ═══════════════════════════════════════════════════════════════
    
    **注意**: 请在 Valves 中配置 API_KEY
    """

    class Valves(BaseModel):
        API_KEY: str = Field(
            default="",
            description="【必填】SEO 分析 API Key"
        )
        DEFAULT_DATABASE: str = Field(
            default="us",
            description="默认数据库/地区代码 (us=美国, uk=英国, de=德国, fr=法国, cn=中国 等)"
        )
        DEFAULT_LIMIT: int = Field(
            default=10,
            description="默认返回结果数量"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.base_url = "https://api.semrush.com/"

    def _make_request(self, params: dict) -> dict:
        """
        发送 SEO API 请求
        
        :param params: API 参数
        :return: 解析后的响应数据
        """
        api_key = self.valves.API_KEY.strip()
        
        if not api_key:
            return {
                "success": False,
                "error": "❌ 未配置 API Key。请在工具设置(Valves)中配置 API_KEY。"
            }
        
        params["key"] = api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            raw_text = response.text.strip()
            
            # 检查错误响应
            if raw_text.startswith("ERROR"):
                error_code = raw_text.split("::")[0] if "::" in raw_text else raw_text
                error_messages = {
                    "ERROR 50": "API Key 无效或已过期",
                    "ERROR 40": "超出 API 调用限制",
                    "ERROR 120": "无效的数据库/地区代码",
                    "ERROR 130": "请求的数据库中没有此数据"
                }
                friendly_error = error_messages.get(error_code.split(" ")[0] + " " + error_code.split(" ")[1] if len(error_code.split(" ")) > 1 else error_code, raw_text)
                return {"success": False, "error": f"API 错误: {friendly_error}", "raw": raw_text}
            
            # 解析 CSV 格式响应
            lines = raw_text.split("\n")
            if not lines or not lines[0]:
                return {"success": True, "data": [], "columns": [], "count": 0}
            
            columns = lines[0].split(";")
            data = []
            for line in lines[1:]:
                if line.strip():
                    values = line.split(";")
                    row = dict(zip(columns, values))
                    data.append(row)
            
            return {
                "success": True,
                "data": data,
                "columns": columns,
                "count": len(data)
            }
            
        except requests.exceptions.Timeout:
            return {"success": False, "error": "请求超时，请稍后重试"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"网络错误: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"解析错误: {str(e)}"}

    def _format_keyword_result(self, data: list, action: str) -> str:
        """格式化关键词结果"""
        if not data:
            return "未找到相关数据"
        
        column_names = {
            "Ph": "关键词",
            "Nq": "月搜索量",
            "Cp": "CPC($)",
            "Co": "竞争度",
            "Kd": "难度",
            "Nr": "结果数",
            "Td": "趋势",
            "Dn": "域名",
            "Ur": "URL",
            "Po": "排名位置"
        }
        
        lines = []
        for i, item in enumerate(data[:20], 1):
            line_parts = [f"{i}."]
            for key, value in item.items():
                display_name = column_names.get(key, key)
                line_parts.append(f"{display_name}: {value}")
            lines.append(" | ".join(line_parts))
        
        return "\n".join(lines)

    def _format_domain_result(self, data: list, action: str) -> str:
        """格式化域名结果"""
        if not data:
            return "未找到相关数据"
        
        column_names = {
            "Dn": "域名",
            "Rk": "排名",
            "Or": "自然关键词数",
            "Ot": "自然流量",
            "Oc": "自然流量成本",
            "Ad": "付费关键词数",
            "At": "付费流量",
            "Ac": "付费流量成本",
            "Ph": "关键词",
            "Po": "排名",
            "Nq": "搜索量",
            "Tr": "流量",
            "Ur": "URL",
            "Pc": "关键词数"
        }
        
        lines = []
        for i, item in enumerate(data[:20], 1):
            line_parts = [f"{i}."]
            for key, value in item.items():
                display_name = column_names.get(key, key)
                line_parts.append(f"{display_name}: {value}")
            lines.append(" | ".join(line_parts))
        
        return "\n".join(lines)

    def domain_analysis(
        self,
        domain: str,
        action: str = "overview",
        database: Optional[str] = None,
        limit: Optional[int] = None,
        __user__: dict = None
    ) -> str:
        """
        🌐 网站SEO分析 - 分析任何网站/域名的流量、排名、关键词
        
        ════════════════════════════════════════════════════════
        🎯 何时使用此工具（优先级最高）
        ════════════════════════════════════════════════════════
        
        当用户说以下任何一种时，使用此工具：
        
        ✅ "分析 xxx.com"、"分析这个网站"、"分析官网"
        ✅ "看看 xxx 的 SEO"、"xxx 网站表现怎么样"
        ✅ "帮我对 xxx 做关键词分析"（注意：这里指网站的关键词）
        ✅ "这个网站排名哪些词"、"网站流量怎么样"
        ✅ "分析 https://xxx.com"、"分析 www.xxx.com"
        ✅ "帮我分析 xxx 官网"、"看下 xxx 的 SEO 数据"
        
        ════════════════════════════════════════════════════════
        📋 参数说明
        ════════════════════════════════════════════════════════
        
        :param domain: 【必填】要分析的网站域名
            ✓ 支持格式: "topify.ai", "https://topify.ai", "www.topify.ai"
            ✓ 系统会自动清理，只保留域名部分
            
        :param action: 分析类型（默认 overview）
            • overview     - 【默认】SEO概览：排名、流量、关键词数量
            • organic_keywords - 关键词列表：该网站排名的所有关键词 ⭐常用
            • top_pages    - 热门页面：流量最高的页面
            • paid_keywords - 付费关键词：广告投放的词
            • overview_global - 全球数据
            
        :param database: 地区代码（默认 us）
            • us=美国, uk=英国, cn=中国, de=德国, fr=法国, jp=日本
            
        :param limit: 返回结果数量（默认 10）
        
        :return: 网站SEO分析数据
        
        ════════════════════════════════════════════════════════
        📝 典型用户查询 → 参数映射
        ════════════════════════════════════════════════════════
        
        "分析 topify.ai" 
        → domain="topify.ai", action="overview"
        
        "帮我对 topify.ai 做关键词分析" 
        → domain="topify.ai", action="organic_keywords"
        
        "topify.ai 官网排名了哪些词" 
        → domain="topify.ai", action="organic_keywords"
        
        "看看 topify.ai 流量最高的页面" 
        → domain="topify.ai", action="top_pages"
        
        "分析 https://www.topify.ai 的SEO并写报告"
        → domain="topify.ai", action="overview"，然后用结果写文章
        """
        if not domain or not domain.strip():
            return "❌ 请提供要分析的域名，例如: topify.ai"
        
        # 清理域名
        domain = domain.strip().lower()
        domain = domain.replace("https://", "").replace("http://", "")
        domain = domain.replace("www.", "").split("/")[0]
        
        database = database or self.valves.DEFAULT_DATABASE
        limit = limit or self.valves.DEFAULT_LIMIT
        
        action_map = {
            "overview": ("domain_rank", "Dn,Rk,Or,Ot,Oc,Ad,At,Ac"),
            "overview_global": ("domain_ranks", "Db,Dn,Rk,Or,Ot,Oc,Ad,At,Ac"),
            "organic_keywords": ("domain_organic", "Ph,Po,Pp,Pd,Nq,Cp,Ur,Tr,Tc,Co,Kd"),
            "paid_keywords": ("domain_adwords", "Ph,Po,Nq,Cp,Tr,Tc,Co"),
            "top_pages": ("domain_organic_pages", "Ur,Pc,Tg")
        }
        
        if action not in action_map:
            return f"""❌ 未知的 action 类型: {action}

可选值:
• overview - SEO概览（默认）
• organic_keywords - 排名关键词列表 ⭐
• top_pages - 热门页面
• paid_keywords - 付费关键词
• overview_global - 全球数据"""
        
        report_type, columns = action_map[action]
        
        params = {
            "type": report_type,
            "domain": domain,
            "export_columns": columns
        }
        
        if action != "overview_global":
            params["database"] = database
        
        if action in ["organic_keywords", "paid_keywords", "top_pages"]:
            params["display_limit"] = limit
            params["display_sort"] = "tr_desc"
        
        result = self._make_request(params)
        
        if not result["success"]:
            return f"❌ {result['error']}"
        
        action_titles = {
            "overview": "🌐 网站 SEO 概览",
            "overview_global": "🌍 全球数据概览",
            "organic_keywords": "🔑 网站排名关键词",
            "paid_keywords": "💰 付费广告关键词",
            "top_pages": "📄 热门页面"
        }
        
        formatted = self._format_domain_result(result["data"], action)
        
        return f"""{action_titles[action]} - {domain}

📍 数据库: {database.upper() if action != 'overview_global' else '全球'}
📈 结果数量: {result['count']}

{formatted}

---
💡 提示: 
• 查看网站排名的关键词: action="organic_keywords"
• 查看流量最高的页面: action="top_pages"
"""

    def keyword_research(
        self,
        keyword: str,
        action: str = "overview",
        database: Optional[str] = None,
        limit: Optional[int] = None,
        __user__: dict = None
    ) -> str:
        """
        🔍 关键词研究 - 分析某个搜索词的数据，找相关关键词
        
        ════════════════════════════════════════════════════════
        🎯 何时使用此工具
        ════════════════════════════════════════════════════════
        
        当用户说以下任何一种时，使用此工具：
        
        ✅ "研究关键词 xxx"、"分析'xxx'这个关键词"
        ✅ "xxx 这个词搜索量多少"、"xxx 难度高吗"
        ✅ "找与 xxx 相关的关键词"、"xxx 的长尾词"
        ✅ "查一下 xxx 的搜索数据"
        ✅ "谁在 xxx 这个词排名"、"xxx 的搜索结果"
        
        ════════════════════════════════════════════════════════
        ⚠️ 注意区分
        ════════════════════════════════════════════════════════
        
        ❌ "帮我对 topify.ai 做关键词分析" 
           → 这是分析【网站】的关键词，应该用 domain_analysis
           
        ✅ "帮我分析'AI工具'这个关键词" 
           → 这是研究【搜索词】，用此工具 keyword_research
        
        ════════════════════════════════════════════════════════
        📋 参数说明
        ════════════════════════════════════════════════════════
        
        :param keyword: 【必填】要研究的关键词/搜索词
            ✓ 示例: "AI工具", "seo tools", "人工智能"
            
        :param action: 分析类型（默认 overview）
            • overview  - 【默认】关键词概览：搜索量、CPC、难度
            • related   - 相关关键词：类似的词 ⭐常用
            • broad_match - 广泛匹配：包含该词的所有关键词
            • questions - 问题关键词：如"如何..."、"什么是..."
            • difficulty - SEO难度评分
            • serp - 搜索排名：哪些网站在这个词排名
            
        :param database: 地区代码（默认 us）
        :param limit: 返回结果数量（默认 10）
        
        :return: 关键词分析数据
        
        ════════════════════════════════════════════════════════
        📝 典型用户查询 → 参数映射
        ════════════════════════════════════════════════════════
        
        "分析'AI写作工具'这个关键词" 
        → keyword="AI写作工具", action="overview"
        
        "找与 SEO 相关的关键词" 
        → keyword="SEO", action="related"
        
        "'人工智能'的搜索量是多少" 
        → keyword="人工智能", action="overview"
        
        "谁在'content marketing'这个词排名" 
        → keyword="content marketing", action="serp"
        
        "找一些关于学习Python的问题关键词"
        → keyword="learn python", action="questions"
        """
        if not keyword or not keyword.strip():
            return "❌ 请提供要研究的关键词，例如: AI工具"
        
        keyword = keyword.strip()
        database = database or self.valves.DEFAULT_DATABASE
        limit = limit or self.valves.DEFAULT_LIMIT
        
        action_map = {
            "overview": ("phrase_this", "Ph,Nq,Cp,Co,Kd,Nr,Td"),
            "related": ("phrase_related", "Ph,Nq,Cp,Co,Kd,Nr"),
            "broad_match": ("phrase_fullsearch", "Ph,Nq,Cp,Co,Kd"),
            "questions": ("phrase_questions", "Ph,Nq,Cp,Co,Kd"),
            "difficulty": ("phrase_kdi", "Ph,Kd"),
            "serp": ("phrase_organic", "Dn,Ur,Po,Nq")
        }
        
        if action not in action_map:
            return f"""❌ 未知的 action 类型: {action}

可选值:
• overview - 关键词概览（默认）
• related - 相关关键词 ⭐
• broad_match - 广泛匹配
• questions - 问题类关键词
• difficulty - SEO难度
• serp - 搜索排名"""
        
        report_type, columns = action_map[action]
        
        params = {
            "type": report_type,
            "phrase": keyword,
            "database": database,
            "export_columns": columns
        }
        
        if action not in ["overview", "difficulty"]:
            params["display_limit"] = limit
        
        result = self._make_request(params)
        
        if not result["success"]:
            return f"❌ {result['error']}"
        
        action_titles = {
            "overview": "📊 关键词概览",
            "related": "🔗 相关关键词",
            "broad_match": "📋 广泛匹配关键词",
            "questions": "❓ 问题类关键词",
            "difficulty": "📈 SEO难度",
            "serp": "🏆 搜索结果排名"
        }
        
        formatted = self._format_keyword_result(result["data"], action)
        
        return f"""{action_titles[action]} - "{keyword}"

🌐 数据库: {database.upper()}
📈 结果数量: {result['count']}

{formatted}

---
💡 提示:
• 发现更多相关词: action="related"
• 找问题类长尾词: action="questions"
• 看谁在这个词排名: action="serp"
"""

    def competitor_analysis(
        self,
        domain: str,
        action: str = "find_organic",
        domains: Optional[str] = None,
        database: Optional[str] = None,
        limit: Optional[int] = None,
        __user__: dict = None
    ) -> str:
        """
        🏆 竞争对手分析 - 找竞争者、对比网站、分析差距
        
        ════════════════════════════════════════════════════════
        🎯 何时使用此工具
        ════════════════════════════════════════════════════════
        
        当用户说以下任何一种时，使用此工具：
        
        ✅ "分析 xxx 的竞争对手"、"xxx 的竞品有哪些"
        ✅ "找出 xxx 的竞争者"、"谁是 xxx 的对手"
        ✅ "帮我找 xxx.com 的竞争网站"
        ✅ "对比 A 和 B 两个网站"
        ✅ "分析我和竞争对手的关键词差距"
        
        ════════════════════════════════════════════════════════
        📋 参数说明
        ════════════════════════════════════════════════════════
        
        :param domain: 【必填】要分析的网站域名
            ✓ 示例: "topify.ai", "https://topify.ai"
        
        :param action: 分析类型（默认 find_organic）
            • find_organic - 【默认】发现SEO竞争对手 ⭐最常用
            • find_paid    - 发现付费广告竞争对手
            • compare      - 对比多个网站（需要 domains 参数）
            • gap_analysis - 关键词差距分析（需要 domains 参数）
            
        :param domains: 多个域名，逗号分隔（仅 compare/gap_analysis 需要）
            ✓ 示例: "mysite.com,competitor1.com,competitor2.com"
            
        :param database: 地区代码（默认 us）
        :param limit: 返回结果数量（默认 10）
        
        :return: 竞争分析数据
        
        ════════════════════════════════════════════════════════
        📝 典型用户查询 → 参数映射
        ════════════════════════════════════════════════════════
        
        "帮我分析 topify.ai 的竞争对手" 
        → domain="topify.ai", action="find_organic"
        
        "找出 example.com 的竞争者" 
        → domain="example.com", action="find_organic"
        
        "topify.ai 的竞品有哪些"
        → domain="topify.ai", action="find_organic"
        
        "对比 siteA.com 和 siteB.com"
        → domain="siteA.com", action="compare", domains="siteA.com,siteB.com"
        
        "分析我的网站和竞争对手的关键词差距"
        → action="gap_analysis", domains="mysite.com,competitor.com"
        """
        database = database or self.valves.DEFAULT_DATABASE
        limit = limit or self.valves.DEFAULT_LIMIT
        
        # 清理域名
        def clean_domain(d: str) -> str:
            if not d:
                return ""
            return d.strip().lower().replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        
        # 解析 domains 字符串为列表
        domains_list = []
        if domains:
            parts = re.split(r'[,;\s]+', domains)
            domains_list = [clean_domain(d) for d in parts if d.strip()]
        
        # 清理主域名
        if domain:
            domain = clean_domain(domain)
        
        # 智能处理：如果 domain 包含多个域名
        if not domains_list and domain and (',' in domain or ';' in domain):
            parts = re.split(r'[,;\s]+', domain)
            domains_list = [clean_domain(d) for d in parts if d.strip()]
            if len(domains_list) == 1:
                domain = domains_list[0]
                domains_list = []
            elif len(domains_list) > 1:
                domain = domains_list[0]
        
        if action == "find_organic":
            if not domain:
                return "❌ 请提供要分析的域名，例如: topify.ai"
            params = {
                "type": "domain_organic_organic",
                "domain": domain,
                "database": database,
                "display_limit": limit,
                "export_columns": "Dn,Cr,Np,Or,Ot,Oc,Ad"
            }
            title = f"🏆 SEO 竞争对手 - {domain}"
        
        elif action == "find_paid":
            if not domain:
                return "❌ 请提供要分析的域名，例如: topify.ai"
            params = {
                "type": "domain_adwords_adwords",
                "domain": domain,
                "database": database,
                "display_limit": limit,
                "export_columns": "Dn,Cr,Np,Ad,At,Ac"
            }
            title = f"💰 付费广告竞争对手 - {domain}"
        
        elif action == "compare":
            if len(domains_list) < 2:
                return f"""❌ 对比分析需要至少 2 个域名

请使用 domains 参数提供多个域名，用逗号分隔
例如: domains="site1.com,site2.com"

当前收到: domain={domain}, domains={domains}"""
            
            domains_param = "|".join([f"or|{d}" for d in domains_list])
            params = {
                "type": "domain_domains",
                "domains": domains_param,
                "database": database,
                "display_limit": limit,
                "display_sort": "nq_desc",
                "export_columns": "Ph,P0,P1,P2,Nq,Kd,Co,Cp"
            }
            title = f"⚖️ 网站对比 - {', '.join(domains_list)}"
        
        elif action == "gap_analysis":
            if len(domains_list) < 2:
                return f"""❌ 差距分析需要至少 2 个域名

请使用 domains 参数：第一个是你的网站，其余是竞争对手
例如: domains="mysite.com,competitor.com"

当前收到: domain={domain}, domains={domains}"""
            
            my_domain = domains_list[0]
            competitors = domains_list[1:]
            domains_param = "*|or|" + "|+|or|".join(competitors) + f"|-|or|{my_domain}"
            params = {
                "type": "domain_domains",
                "domains": domains_param,
                "database": database,
                "display_limit": limit,
                "display_sort": "nq_desc",
                "export_columns": "Ph,P0,P1,P2,Nq,Kd,Co,Cp"
            }
            title = f"📊 关键词差距 - {my_domain} vs {', '.join(competitors)}"
        
        else:
            return f"""❌ 未知的 action 类型: {action}

可选值:
• find_organic - 发现SEO竞争对手（默认）⭐
• find_paid - 发现付费竞争对手
• compare - 对比多个网站
• gap_analysis - 关键词差距分析"""
        
        result = self._make_request(params)
        
        if not result["success"]:
            error_msg = result.get('error', '未知错误')
            raw_error = result.get('raw', '')
            
            # 检查订阅限制
            if any(kw in str(error_msg).lower() or kw in str(raw_error) 
                   for kw in ["120", "130", "134", "limit", "quota"]):
                return f"""❌ API 限制

错误: {error_msg}

⚠️ 可能原因:
1. API 订阅不支持此功能
2. 该地区数据库 ({database}) 无数据
3. API 调用配额已用完

💡 建议: 尝试 action="find_organic"（基础订阅通常支持）"""
            
            return f"❌ API 调用失败: {error_msg}"
        
        # 格式化结果
        column_names = {
            "Dn": "域名",
            "Cr": "共同关键词比例",
            "Np": "共同关键词数",
            "Or": "自然关键词",
            "Ot": "自然流量",
            "Oc": "流量成本",
            "Ad": "付费关键词",
            "At": "付费流量",
            "Ac": "付费成本",
            "Ph": "关键词",
            "P0": "域名1排名",
            "P1": "域名2排名",
            "P2": "域名3排名",
            "Nq": "搜索量",
            "Kd": "难度",
            "Co": "竞争度",
            "Cp": "CPC"
        }
        
        lines = []
        for i, item in enumerate(result["data"][:20], 1):
            line_parts = [f"{i}."]
            for key, value in item.items():
                display_name = column_names.get(key, key)
                line_parts.append(f"{display_name}: {value}")
            lines.append(" | ".join(line_parts))
        
        formatted = "\n".join(lines) if lines else "未找到相关数据"
        
        return f"""{title}

📍 数据库: {database.upper()}
📈 结果数量: {result['count']}

{formatted}

---
💡 提示:
• 发现更多竞争对手: action="find_organic"
• 分析关键词差距: action="gap_analysis", domains="你的网站,竞争对手"
"""


# ==================== 兼容性别名 ====================
Functions = Tools
Function = Tools


# ==================== 辅助函数 ====================
def get_seo_client():
    """获取 SEO Tools 实例"""
    return Tools()
