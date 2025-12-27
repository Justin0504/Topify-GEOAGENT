"""
title: WordPress 文章管理工具
description: 【批量上传】将文章批量上传到WordPress | 【TDK优化】为文章生成SEO元数据 | 【批量发布】发布草稿文章 | 【URL提取】获取已发布文章URL列表
author: GEO Agent
version: 2.0.0
required_open_webui_version: 0.6.0
requirements: requests, urllib3
"""

import os
import json
import re
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field


class Tools:
    """
    WordPress 文章管理工具 - 批量上传、优化和发布文章
    
    ═══════════════════════════════════════════════════════════════
    🎯 功能匹配指南（中文触发词）
    ═══════════════════════════════════════════════════════════════
    
    📤 upload_articles - 批量上传文章
       触发词: "上传文章", "批量上传", "上传到WordPress", "保存草稿",
              "把文章上传", "文件夹上传"
       示例: "把这些文章上传到WordPress保存为草稿"
       输出: 上传结果报告
    
    🏷️ optimize_article_tdk - TDK优化
       触发词: "TDK优化", "SEO优化", "标题描述", "元数据",
              "title description", "slug优化"
       示例: "为草稿文章生成TDK"
       输出: TDK优化报告
    
    🚀 publish_articles - 批量发布
       触发词: "发布文章", "批量发布", "上线文章", "草稿发布",
              "把草稿发布", "全部发布"
       示例: "把草稿状态的文章全部发布"
       输出: 发布结果报告
    
    🔗 extract_article_urls - URL提取
       触发词: "提取URL", "文章链接", "URL列表", "获取链接",
              "导出URL", "文章地址"
       示例: "把发布的文章URL全部给我"
       输出: URL列表（标题;URL格式）
    
    ═══════════════════════════════════════════════════════════════
    """

    class Valves(BaseModel):
        WP_ACCESS_TOKEN: str = Field(
            default="",
            description="【必填】WordPress.com API Access Token"
        )
        WP_SITE_ID: str = Field(
            default="",
            description="【必填】WordPress.com Site ID（数字或域名）"
        )
        WP_API_BASE: str = Field(
            default="https://public-api.wordpress.com/rest/v1.1",
            description="WordPress.com API 基础 URL"
        )
        OUTPUT_PATH: str = Field(
            default="/app/backend/data/output",
            description="文件保存路径"
        )

    def __init__(self):
        self.valves = self.Valves()
        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        创建带重试机制和连接池的 requests session
        """
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,  # 总重试次数
            backoff_factor=1,  # 重试间隔: 1, 2, 4 秒
            status_forcelist=[429, 500, 502, 503, 504],  # 这些状态码触发重试
            allowed_methods=["GET", "POST", "DELETE"],  # 允许重试的方法
            raise_on_status=False,  # 不在错误状态时抛出异常
        )
        
        # 挂载适配器
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10,
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def _clean_credential(self, value: str) -> str:
        """清理凭证值 - 移除所有空白字符"""
        if not value:
            return ""
        return "".join(value.split())

    def _wp_ensure_output_dir(self) -> str:
        """确保输出目录存在"""
        output_path = self.valves.OUTPUT_PATH
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)
        return output_path
    
    def _clean_content(self, content: str) -> str:
        """
        清理文章内容，移除CDATA包装和其他不必要的标签
        
        :param content: 原始内容
        :return: 清理后的内容
        """
        if not content:
            return ""
        
        content = str(content).strip()
        
        # 移除 CDATA 包装
        # 匹配 <![CDATA[...]]> 格式（可能跨多行）
        content = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', content, flags=re.DOTALL)
        
        # 移除多余的空白字符
        content = content.strip()
        
        # 确保内容是有效的 HTML 字符串
        # 如果内容被额外的引号包裹，移除它们
        if (content.startswith('"') and content.endswith('"')) or \
           (content.startswith("'") and content.endswith("'")):
            try:
                # 尝试 JSON 解码（处理转义字符）
                content = json.loads(content)
            except (json.JSONDecodeError, ValueError):
                # 如果解析失败，直接移除首尾引号
                content = content[1:-1]
        
        # 处理转义字符（将 \\n 转换为实际换行）
        if '\\n' in content:
            content = content.replace('\\n', '\n')
        if '\\t' in content:
            content = content.replace('\\t', '\t')
        if '\\r' in content:
            content = content.replace('\\r', '\r')
        
        return content.strip()

    def _get_headers(self) -> dict:
        """获取API请求头"""
        token = self._clean_credential(self.valves.WP_ACCESS_TOKEN)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "OpenWebUI-WordPress-Tool/2.0",
            "Accept": "application/json",
            "Connection": "keep-alive",
        }

    def _make_request(self, method: str, endpoint: str, data: dict = None, params: dict = None, max_retries: int = 3) -> dict:
        """
        发送API请求（带重试机制）
        """
        token = self._clean_credential(self.valves.WP_ACCESS_TOKEN)
        site_id = self._clean_credential(self.valves.WP_SITE_ID)
        
        if not token:
            return {"success": False, "error": "未配置 WordPress Access Token，请在工具设置中配置"}
        
        if not site_id:
            return {"success": False, "error": "未配置 WordPress Site ID，请在工具设置中配置"}
        
        # 清理 API Base URL
        api_base = self._clean_credential(self.valves.WP_API_BASE).rstrip("/")
        url = f"{api_base}/sites/{site_id}/{endpoint}"
        headers = self._get_headers()
        
        # 超时配置: (连接超时, 读取超时)
        timeout = (10, 60)
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # 确保 session 有效
                if not hasattr(self, "_session") or self._session is None:
                    self._session = self._create_session()
                
                if method.upper() == "GET":
                    response = self._session.get(url, headers=headers, params=params, timeout=timeout)
                elif method.upper() == "POST":
                    response = self._session.post(url, headers=headers, json=data, timeout=timeout)
                elif method.upper() == "DELETE":
                    response = self._session.delete(url, headers=headers, timeout=timeout)
                else:
                    return {"success": False, "error": f"不支持的HTTP方法: {method}"}
                
                # 解析 JSON 响应
                try:
                    result = response.json()
                except json.JSONDecodeError:
                    if response.status_code in [200, 201]:
                        return {"success": True, "data": {"raw_response": response.text}}
                    else:
                        return {
                            "success": False,
                            "error": f"非JSON响应 (状态码 {response.status_code}): {response.text[:500]}",
                            "status_code": response.status_code,
                        }
                
                if response.status_code in [200, 201]:
                    return {"success": True, "data": result}
                else:
                    error_msg = result.get("message", result.get("error", str(result)))
                    return {
                        "success": False,
                        "error": error_msg,
                        "status_code": response.status_code,
                    }
                    
            except requests.exceptions.Timeout as e:
                last_error = f"请求超时 (尝试 {attempt + 1}/{max_retries}): {str(e)}"
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                    
            except requests.exceptions.ConnectionError as e:
                last_error = f"连接错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}"
                # 连接错误时重新创建 session
                self._session = self._create_session()
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                    
            except requests.exceptions.RequestException as e:
                last_error = f"网络错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}"
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                    
            except Exception as e:
                last_error = f"未知错误: {type(e).__name__}: {str(e)}"
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
        
        return {"success": False, "error": f"所有重试均失败。最后一次错误: {last_error}"}

    def _create_post(self, title: str, content: str, status: str = "draft", **kwargs) -> dict:
        """创建文章"""
        # 清理内容，移除 CDATA 包装
        cleaned_content = self._clean_content(content)
        
        data = {
            "title": title,
            "content": cleaned_content,
            "status": status
        }
        data.update(kwargs)
        return self._make_request("POST", "posts/new", data)

    def _update_post(self, post_id: int, **kwargs) -> dict:
        """更新文章"""
        # 如果 kwargs 中包含 content，清理它
        if 'content' in kwargs:
            kwargs['content'] = self._clean_content(kwargs['content'])
        return self._make_request("POST", f"posts/{post_id}", kwargs)

    def _get_posts(self, status: str = "any", number: int = 100) -> dict:
        """获取文章列表"""
        return self._make_request("GET", f"posts?status={status}&number={number}")

    # ==================== 公开工具方法 ====================

    def upload_articles(
        self,
        articles: str,
        default_category: str = "",
        default_tags: str = ""
    ) -> str:
        """
        【批量上传文章工具】将文章批量上传到WordPress保存为草稿
        
        当用户说以下内容时调用此工具：
        - "上传文章"、"批量上传"、"上传到WordPress"
        - "把文章保存为草稿"
        - "文章上传"
        
        :param articles: 文章内容，格式为JSON数组，每个元素包含title和content
                        例如: [{"title": "标题1", "content": "内容1"}, ...]
        :param default_category: 默认分类（可选）
        :param default_tags: 默认标签，逗号分隔（可选）
        :return: 上传结果报告
        """
        # 解析文章数据
        try:
            if articles.strip().startswith('['):
                article_list = json.loads(articles)
            else:
                # 尝试解析简单格式：每行 "标题|||内容"
                article_list = []
                for line in articles.strip().split('\n'):
                    if '|||' in line:
                        parts = line.split('|||', 1)
                        article_list.append({
                            "title": parts[0].strip(),
                            "content": parts[1].strip() if len(parts) > 1 else ""
                        })
        except json.JSONDecodeError as e:
            return f"❌ 文章数据格式错误: {str(e)}\n\n请使用JSON格式或 '标题|||内容' 格式"
        
        if not article_list:
            return "❌ 未检测到有效的文章数据"
        
        results = []
        success_count = 0
        failed_count = 0
        
        for idx, article in enumerate(article_list, 1):
            title = article.get("title", f"未命名文章 {idx}")
            content = article.get("content", "")
            
            # 清理内容，移除 CDATA 包装
            cleaned_content = self._clean_content(content)
            
            post_data = {
                "title": title,
                "content": cleaned_content,
                "status": "draft"
            }
            
            if default_category:
                post_data["categories"] = default_category
            if default_tags:
                post_data["tags"] = default_tags
            
            result = self._create_post(**post_data)
            
            if result["success"]:
                post_id = result["data"].get("ID", "")
                results.append(f"✅ #{idx} {title[:30]}... → ID: {post_id}")
                success_count += 1
            else:
                results.append(f"❌ #{idx} {title[:30]}... → 错误: {result.get('error', '未知')}")
                failed_count += 1
        
        results_text = "\n".join(results)
        
        return f"""
📤 **批量上传完成**

═══════════════════════════════════════
📊 **统计**
═══════════════════════════════════════
✅ 成功: {success_count} 篇
❌ 失败: {failed_count} 篇
📄 总计: {len(article_list)} 篇

═══════════════════════════════════════
📋 **详细结果**
═══════════════════════════════════════
{results_text}

═══════════════════════════════════════
💡 **下一步**
═══════════════════════════════════════
1. 使用 optimize_article_tdk 工具优化文章TDK
2. 使用 publish_articles 工具批量发布
"""

    def optimize_article_tdk(
        self,
        post_ids: str = "",
        optimize_all_drafts: bool = True
    ) -> str:
        """
        【TDK优化工具】为WordPress草稿文章生成和更新SEO元数据（Title、Description、URL Slug）
        
        当用户说以下内容时调用此工具：
        - "TDK优化"、"SEO优化"、"优化标题描述"
        - "生成元数据"、"slug优化"
        - "为草稿文章生成TDK"
        
        :param post_ids: 要优化的文章ID（逗号分隔），为空则优化所有草稿
        :param optimize_all_drafts: 是否优化所有草稿文章
        :return: 优化结果报告和TDK建议
        """
        import re
        
        # 获取文章列表
        if post_ids:
            ids = [int(id.strip()) for id in post_ids.split(',') if id.strip().isdigit()]
            posts_to_optimize = []
            for post_id in ids:
                result = self._make_request("GET", f"posts/{post_id}")
                if result["success"]:
                    posts_to_optimize.append(result["data"])
        else:
            result = self._get_posts(status="draft", number=50)
            if not result["success"]:
                return f"❌ 获取文章列表失败: {result.get('error', '未知错误')}"
            posts_to_optimize = result["data"].get("posts", [])
        
        if not posts_to_optimize:
            return "❌ 未找到需要优化的草稿文章"
        
        tdk_suggestions = []
        
        for post in posts_to_optimize:
            post_id = post.get("ID", "")
            title = post.get("title", "")
            content = post.get("content", "")[:500]
            current_slug = post.get("slug", "")
            
            # 提取关键词
            words = title.lower().replace(',', ' ').replace('.', ' ').split()
            keywords = [w for w in words if len(w) > 3][:5]
            
            # 生成SEO友好的slug
            suggested_slug = '-'.join(keywords[:4]) if keywords else current_slug
            
            # 生成description建议
            clean_content = re.sub(r'<[^>]+>', '', content)
            suggested_desc = clean_content[:150].strip() + "..." if len(clean_content) > 150 else clean_content
            
            tdk_suggestions.append({
                "post_id": post_id,
                "current_title": title,
                "suggested_title": f"{title[:55]}..." if len(title) > 60 else title,
                "suggested_description": suggested_desc,
                "suggested_slug": suggested_slug,
                "keywords": ', '.join(keywords)
            })
        
        # 生成报告
        report_lines = []
        for idx, tdk in enumerate(tdk_suggestions, 1):
            report_lines.append(f"""
📄 **文章 #{idx}** (ID: {tdk['post_id']})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 当前标题: {tdk['current_title'][:50]}...
✏️ 建议Title: {tdk['suggested_title']}
📝 建议Description: {tdk['suggested_description'][:100]}...
🔗 建议Slug: {tdk['suggested_slug']}
🏷️ 关键词: {tdk['keywords']}
""")
        
        report_text = "\n".join(report_lines)
        
        return f"""
🏷️ **TDK优化分析完成**

═══════════════════════════════════════
📊 **统计**
═══════════════════════════════════════
📄 分析文章数: {len(tdk_suggestions)} 篇

═══════════════════════════════════════
📋 **TDK建议**
═══════════════════════════════════════
{report_text}

═══════════════════════════════════════
📏 **TDK规范**
═══════════════════════════════════════
• Title: 50-60字符，包含主要关键词
• Description: 150-160字符，包含关键词和号召语
• Slug: 使用关键词，用连字符分隔，简短明了

═══════════════════════════════════════
💡 **下一步**
═══════════════════════════════════════
确认TDK后，使用 publish_articles 工具发布文章
"""

    def publish_articles(
        self,
        post_ids: str = "",
        publish_all_drafts: bool = True
    ) -> str:
        """
        【批量发布工具】将草稿状态的WordPress文章批量发布上线
        
        当用户说以下内容时调用此工具：
        - "发布文章"、"批量发布"、"上线文章"
        - "把草稿发布"、"全部发布"
        - "草稿文章发布"
        
        :param post_ids: 要发布的文章ID（逗号分隔），为空则发布所有草稿
        :param publish_all_drafts: 是否发布所有草稿文章
        :return: 发布结果报告
        """
        # 获取要发布的文章
        if post_ids:
            ids = [int(id.strip()) for id in post_ids.split(',') if id.strip().isdigit()]
        else:
            result = self._get_posts(status="draft", number=100)
            if not result["success"]:
                return f"❌ 获取草稿列表失败: {result.get('error', '未知错误')}"
            ids = [post.get("ID") for post in result["data"].get("posts", [])]
        
        if not ids:
            return "❌ 未找到需要发布的草稿文章"
        
        results = []
        success_count = 0
        failed_count = 0
        published_urls = []
        
        for post_id in ids:
            # 更新文章状态为发布
            result = self._update_post(post_id, status="publish")
            
            if result["success"]:
                post_data = result["data"]
                title = post_data.get("title", "未知标题")
                url = post_data.get("URL", "")
                results.append(f"✅ ID:{post_id} {title[:30]}...")
                published_urls.append({"id": post_id, "title": title, "url": url})
                success_count += 1
            else:
                results.append(f"❌ ID:{post_id} 发布失败: {result.get('error', '未知')}")
                failed_count += 1
        
        results_text = "\n".join(results)
        urls_text = "\n".join([f"{p['title']};{p['url']}" for p in published_urls])
        
        return f"""
🚀 **批量发布完成**

═══════════════════════════════════════
📊 **统计**
═══════════════════════════════════════
✅ 成功发布: {success_count} 篇
❌ 发布失败: {failed_count} 篇
📄 总计处理: {len(ids)} 篇

═══════════════════════════════════════
📋 **发布结果**
═══════════════════════════════════════
{results_text}

═══════════════════════════════════════
🔗 **已发布文章URL**
═══════════════════════════════════════
{urls_text if urls_text else '无成功发布的文章'}

═══════════════════════════════════════
💡 **下一步**
═══════════════════════════════════════
使用 extract_article_urls 工具导出完整URL列表
"""

    def extract_article_urls(
        self,
        status: str = "publish",
        number: int = 100,
        format_type: str = "title_url"
    ) -> str:
        """
        【URL提取工具】获取已发布文章的URL列表
        
        当用户说以下内容时调用此工具：
        - "提取URL"、"文章链接"、"URL列表"
        - "获取文章地址"、"导出链接"
        - "把文章URL给我"
        
        :param status: 文章状态 (publish=已发布, draft=草稿, any=全部)
        :param number: 获取文章数量上限
        :param format_type: 输出格式 (title_url=标题;URL, full=完整信息)
        :return: 文章URL列表
        """
        result = self._get_posts(status=status, number=number)
        
        if not result["success"]:
            return f"❌ 获取文章列表失败: {result.get('error', '未知错误')}"
        
        posts = result["data"].get("posts", [])
        
        if not posts:
            return f"❌ 未找到状态为 '{status}' 的文章"
        
        # 生成URL列表
        output_path = self._wp_ensure_output_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "title_url":
            # 简单格式：标题;URL
            url_lines = []
            for post in posts:
                title = post.get("title", "").replace(';', ',')
                url = post.get("URL", "")
                url_lines.append(f"{title};{url}")
            
            urls_text = "\n".join(url_lines)
            
            # 保存到文件
            filename = f"article_urls_{timestamp}.csv"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("标题;URL\n")
                f.write(urls_text)
            
            return f"""
🔗 **文章URL提取完成**

═══════════════════════════════════════
📊 **统计**
═══════════════════════════════════════
📄 文章数量: {len(posts)} 篇
📁 状态筛选: {status}

═══════════════════════════════════════
📋 **URL列表**（格式: 标题;URL）
═══════════════════════════════════════
{urls_text}

═══════════════════════════════════════
💾 **文件已保存**
═══════════════════════════════════════
路径: {filepath}
"""
        
        else:
            # 完整格式
            full_info = []
            for idx, post in enumerate(posts, 1):
                full_info.append(f"""
#{idx}
ID: {post.get('ID', '')}
标题: {post.get('title', '')}
URL: {post.get('URL', '')}
状态: {post.get('status', '')}
发布时间: {post.get('date', '')}
""")
            
            info_text = "\n".join(full_info)
            
            return f"""
🔗 **文章信息提取完成**

═══════════════════════════════════════
📊 **统计**
═══════════════════════════════════════
📄 文章数量: {len(posts)} 篇
📁 状态筛选: {status}

═══════════════════════════════════════
📋 **完整信息**
═══════════════════════════════════════
{info_text}
"""

    def create_article(
        self,
        title: str,
        content: str,
        excerpt: str = "",
        categories: str = "",
        tags: str = "",
        status: str = "publish",
        slug: str = "",
        save_local: bool = True,
        upload_wordpress: bool = True
    ) -> str:
        """
        【创建文章】写文章并自动发布到WordPress，同时保存到本地
        
        当用户说以下内容时调用此工具：
        - "写文章"、"创建文章"、"发布文章"
        - "把分析结果发布"、"发布报告"
        - "写一篇关于XX的文章并发布"
        
        :param title: 文章标题（必填）
        :param content: 文章内容，支持HTML格式（必填）
        :param excerpt: 文章摘要（可选）
        :param categories: 分类，逗号分隔（可选）
        :param tags: 标签，逗号分隔（可选）
        :param status: 发布状态 - "publish"(立即发布，默认), "draft"(草稿)
        :param slug: URL别名（可选）
        :param save_local: 是否保存到本地（默认True）
        :param upload_wordpress: 是否上传到WordPress（默认True）
        :return: 创建结果
        """
        results = []
        local_path = None
        wp_result = None
        
        # 1. 保存到本地
        if save_local:
            try:
                output_path = self._wp_ensure_output_dir()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # 清理文件名
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                safe_title = safe_title.replace(' ', '_') or 'article'
                
                # 保存为 HTML 文件
                html_filename = f"{safe_title}_{timestamp}.html"
                html_path = os.path.join(output_path, html_filename)
                
                # 构建完整 HTML
                html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{excerpt or ''}">
    <meta name="keywords" content="{tags or ''}">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
        .content {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <article>
        <h1>{title}</h1>
        <div class="meta">
            <span>分类: {categories or '未分类'}</span> | 
            <span>标签: {tags or '无'}</span> |
            <span>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
        </div>
        {f'<p class="excerpt"><strong>摘要:</strong> {excerpt}</p>' if excerpt else ''}
        <div class="content">
            {content}
        </div>
    </article>
</body>
</html>"""
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # 同时保存为 Markdown
                md_filename = f"{safe_title}_{timestamp}.md"
                md_path = os.path.join(output_path, md_filename)
                
                # 简单的 HTML to Markdown 转换
                import re
                md_content = content
                md_content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', md_content)
                md_content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', md_content)
                md_content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', md_content)
                md_content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', md_content)
                md_content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', md_content)
                md_content = re.sub(r'<em>(.*?)</em>', r'*\1*', md_content)
                md_content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', md_content)
                md_content = re.sub(r'<[^>]+>', '', md_content)  # 移除剩余标签
                
                md_full = f"""# {title}

**分类:** {categories or '未分类'}  
**标签:** {tags or '无'}  
**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{f'**摘要:** {excerpt}' + chr(10) + chr(10) + '---' + chr(10) if excerpt else ''}

{md_content}
"""
                
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_full)
                
                local_path = {"html": html_path, "md": md_path}
                results.append(f"✅ 本地保存成功:\n   📄 HTML: {html_path}\n   📝 Markdown: {md_path}")
                
            except Exception as e:
                results.append(f"⚠️ 本地保存失败: {str(e)}")
        
        # 2. 上传到 WordPress
        if upload_wordpress:
            # 清理内容，移除 CDATA 包装和其他问题
            cleaned_content = self._clean_content(content)
            
            post_data = {
                "title": title,
                "content": cleaned_content,
                "status": status
            }
            
            if excerpt:
                post_data["excerpt"] = excerpt
            if categories:
                post_data["categories"] = categories
            if tags:
                post_data["tags"] = tags
            if slug:
                post_data["slug"] = slug
            
            wp_result = self._make_request("POST", "posts/new", post_data)
            
            if wp_result["success"]:
                post = wp_result["data"]
                site_id = self._clean_credential(self.valves.WP_SITE_ID)
                status_text = "已发布" if status == "publish" else "草稿"
                results.append(f"✅ WordPress {status_text}成功:\n   🆔 ID: {post['ID']}\n   🔗 URL: {post['URL']}")
            else:
                results.append(f"❌ WordPress 上传失败: {wp_result.get('error', '未知错误')}")
        
        # 构建返回信息
        results_text = "\n".join(results)
        
        return f"""
📝 **文章处理完成**

═══════════════════════════════════════
📌 **文章标题**
═══════════════════════════════════════
{title}

═══════════════════════════════════════
📊 **处理结果**
═══════════════════════════════════════
{results_text}

═══════════════════════════════════════
📋 **文章详情**
═══════════════════════════════════════
📁 分类: {categories or '未分类'}
🏷️ 标签: {tags or '无'}
📝 摘要: {excerpt[:100] + '...' if excerpt and len(excerpt) > 100 else excerpt or '无'}
"""

    def save_article_local(
        self,
        title: str,
        content: str,
        file_format: str = "both",
        excerpt: str = "",
        categories: str = "",
        tags: str = ""
    ) -> str:
        """
        【仅保存本地】将文章保存到本地，不上传WordPress
        
        当用户说以下内容时调用此工具：
        - "保存文章到本地"、"只保存不上传"
        - "保存为本地文件"、"导出文章"
        
        :param title: 文章标题（必填）
        :param content: 文章内容（必填）
        :param file_format: 保存格式 - "html", "md", "both"(默认)
        :param excerpt: 文章摘要（可选）
        :param categories: 分类（可选）
        :param tags: 标签（可选）
        :return: 保存结果
        """
        return self.create_article(
            title=title,
            content=content,
            excerpt=excerpt,
            categories=categories,
            tags=tags,
            save_local=True,
            upload_wordpress=False
        )

    def write_and_publish(
        self,
        title: str,
        content: str,
        excerpt: str = "",
        categories: str = "",
        tags: str = ""
    ) -> str:
        """
        【写文章并立即发布】一步完成文章创建、本地保存和WordPress发布
        
        当用户说以下内容时调用此工具：
        - "写一篇文章并发布"
        - "创建并发布文章"
        - "把XX发布到WordPress"
        
        :param title: 文章标题（必填）
        :param content: 文章内容（必填）
        :param excerpt: 文章摘要（可选）
        :param categories: 分类（可选）
        :param tags: 标签（可选）
        :return: 发布结果
        """
        return self.create_article(
            title=title,
            content=content,
            excerpt=excerpt,
            categories=categories,
            tags=tags,
            status="publish",
            save_local=True,
            upload_wordpress=True
        )


# ==================== 兼容性别名 ====================
Functions = Tools
Function = Tools
