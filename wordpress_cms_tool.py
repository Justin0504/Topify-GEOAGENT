"""
required_open_webui_version: 0.6.0
description: WordPress CMS Tools - 文章发布和内容管理。请在工具设置(Valves)中配置 WP_ACCESS_TOKEN 和 WP_SITE_ID。
requirements: requests, urllib3
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import os
import time
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class Tools:
    """
    WordPress CMS 内容管理工具
    
    提供全面的 WordPress 内容管理能力，包括：
    - create_article: 创建文章（草稿或直接发布）- 支持发布分析报告、SEO数据等
    - update_article: 更新现有文章内容
    - publish_article: 发布文章（上线）
    - unpublish_article: 取消发布（恢复为草稿）
    - get_article_metrics: 获取文章性能指标（浏览量、点赞等）
    - list_articles_by_topic: 文章列表/库存（按主题/分类筛选）
    - get_site_stats: 获取站点统计数据
    
    **重要**: 凭证已在 Valves 中配置，调用时无需传递 access_token 和 site_id。
    
    使用示例:
    - "写一篇关于AI的文章发布到WordPress"
    - "把上面的SEO分析结果发布成文章"
    - "将分析报告发布到我的网站"
    """

    class Valves(BaseModel):
        WP_ACCESS_TOKEN: str = Field(
            default="",
            description="【必填】WordPress.com API Access Token - 在此处配置您的访问令牌"
        )
        WP_SITE_ID: str = Field(
            default="",
            description="【必填】WordPress.com Site ID - 例如: 251193948 或 example.wordpress.com"
        )
        WP_API_BASE: str = Field(
            default="https://public-api.wordpress.com/rest/v1.1",
            description="WordPress.com API 基础 URL（通常无需修改）"
        )

    def __init__(self):
        self.valves = self.Valves()
        # Runtime credential cache (set when credentials are passed to methods)
        self._runtime_token = ""
        self._runtime_site_id = ""
        # Create a session with retry mechanism for better connection stability
        self._session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry mechanism and connection pooling.
        This helps handle transient network errors and connection issues.
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # Total number of retries
            backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP status codes
            allowed_methods=["GET", "POST", "DELETE"],  # Methods to retry
            raise_on_status=False,  # Don't raise exception on bad status
        )
        
        # Mount adapter with retry strategy to both http and https
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10,
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def _resolve_credentials(self, access_token: str = None, site_id: str = None) -> Tuple[str, str]:
        """
        Resolve WordPress credentials with priority:
        1. Tool-level Valves settings (HIGHEST priority - admin configured, most reliable)
        2. Environment variables (set by WordPress Credential Manager)
        3. Runtime cache (from previous method calls in this session)
        4. Direct method parameters (lowest priority - may contain LLM errors)
        
        :param access_token: Direct access token (optional, used only if Valves not configured)
        :param site_id: Direct site ID (optional, used only if Valves not configured)
        :return: Tuple of (access_token, site_id)
        """
        resolved_token = ""
        resolved_site_id = ""
        
        def clean_credential(value: str) -> str:
            """Clean credential value - remove whitespace, newlines, etc."""
            if not value:
                return ""
            # Remove all whitespace including newlines, tabs, etc.
            return ''.join(value.split())
        
        # Priority 1: Tool-level Valves (最高优先级 - 管理员配置，最可靠)
        if self.valves.WP_ACCESS_TOKEN:
            resolved_token = clean_credential(self.valves.WP_ACCESS_TOKEN)
        if self.valves.WP_SITE_ID:
            resolved_site_id = clean_credential(self.valves.WP_SITE_ID)
        
        # Priority 2: Environment variables (由 Credential Manager 设置)
        if not resolved_token:
            resolved_token = clean_credential(os.environ.get('WP_ACCESS_TOKEN', ''))
        if not resolved_site_id:
            resolved_site_id = clean_credential(os.environ.get('WP_SITE_ID', ''))
        
        # Priority 3: Runtime cache (会话内缓存)
        if not resolved_token and self._runtime_token:
            resolved_token = self._runtime_token
        if not resolved_site_id and self._runtime_site_id:
            resolved_site_id = self._runtime_site_id
        
        # Priority 4: Direct method parameters (最低优先级 - 可能包含 LLM 错误)
        if not resolved_token and access_token:
            resolved_token = clean_credential(access_token)
            self._runtime_token = resolved_token  # Cache for subsequent calls
        if not resolved_site_id and site_id:
            resolved_site_id = clean_credential(str(site_id))
            self._runtime_site_id = resolved_site_id  # Cache for subsequent calls
        
        return resolved_token, resolved_site_id

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: dict = None, 
        params: dict = None,
        access_token: str = None,
        site_id: str = None,
        max_retries: int = 3
    ) -> dict:
        """
        Unified API request function with retry mechanism and improved error handling.
        
        :param method: HTTP method (GET, POST, DELETE)
        :param endpoint: API endpoint
        :param data: Request body data
        :param params: Query parameters
        :param access_token: Direct access token (optional, for one-sentence publishing)
        :param site_id: Direct site ID (optional, for one-sentence publishing)
        :param max_retries: Maximum number of manual retries for connection errors
        :return: Response dict with success flag and data/error
        """
        # Resolve credentials with priority: direct params > cache > env > valves
        resolved_token, resolved_site_id = self._resolve_credentials(access_token, site_id)
        
        if not resolved_token or not resolved_site_id:
            return {
                "success": False,
                "error": "WordPress 凭证未配置。请在调用时提供 access_token 和 site_id 参数，或在工具设置中配置。"
            }

        # Clean API base URL - remove all whitespace (including newlines) and trailing slashes
        api_base = ''.join(self.valves.WP_API_BASE.split()).rstrip('/')
        url = f"{api_base}{endpoint}"
        headers = {
            "Authorization": f"Bearer {resolved_token}",
            "Content-Type": "application/json",
            "User-Agent": "OpenWebUI-WordPress-CMS-Tool/1.0",
            "Accept": "application/json",
            "Connection": "keep-alive",
        }
        
        # Timeout configuration: (connect_timeout, read_timeout)
        timeout = (10, 60)  # 10 seconds to connect, 60 seconds to read response
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Ensure session is valid
                if not hasattr(self, '_session') or self._session is None:
                    self._session = self._create_session()
                
                if method.upper() == "GET":
                    response = self._session.get(
                        url, 
                        headers=headers, 
                        params=params, 
                        timeout=timeout
                    )
                elif method.upper() == "POST":
                    response = self._session.post(
                        url, 
                        headers=headers, 
                        json=data, 
                        timeout=timeout
                    )
                elif method.upper() == "DELETE":
                    response = self._session.delete(
                        url, 
                        headers=headers, 
                        timeout=timeout
                    )
                else:
                    return {"success": False, "error": f"Unsupported method: {method}"}

                # Try to parse JSON response
                try:
                    result = response.json()
                except json.JSONDecodeError:
                    # If response is not JSON, return the text
                    if response.status_code in [200, 201]:
                        return {"success": True, "data": {"raw_response": response.text}}
                    else:
                        return {
                            "success": False,
                            "error": f"Non-JSON response (status {response.status_code}): {response.text[:500]}",
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
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                    
            except requests.exceptions.ConnectionError as e:
                last_error = f"连接错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}"
                # Recreate session on connection error
                self._session = self._create_session()
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                    
            except requests.exceptions.RequestException as e:
                last_error = f"网络错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}"
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
            
            except Exception as e:
                last_error = f"未知错误: {type(e).__name__}: {str(e)}"
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
        
        # All retries failed
        return {
            "success": False, 
            "error": f"所有重试均失败。最后一次错误: {last_error}",
            "_debug": {
                "url": url,
                "method": method,
                "attempts": max_retries,
                "last_error": last_error
            }
        }

    def create_article(
        self,
        title: str,
        content: str,
        excerpt: str = None,
        categories: str = None,
        tags: str = None,
        status: str = "draft",
        slug: str = None,
        featured_image: str = None,
        access_token: str = None,
        site_id: str = None,
        __user__: dict = None,
    ) -> dict:
        """
        创建并发布文章到 WordPress - 支持发布任何内容，包括分析报告、SEO数据、研究结果等
        
        Create and publish article to WordPress - supports publishing any content including 
        analysis reports, SEO data, research results, etc.
        
        :param title: 文章标题 Article title (required)
        :param content: 文章内容，支持 HTML 格式。可以是：原创文章、分析报告、数据总结、研究结果等
        :param excerpt: 文章摘要，用于 SEO 和预览 (optional)
        :param categories: 分类，逗号分隔 e.g. "Tech,AI,SEO分析" (optional)
        :param tags: 标签，逗号分隔 e.g. "SEO,分析报告,数据" (optional)
        :param status: 发布状态 - "draft"(草稿), "publish"(立即发布), "private"(私密)
        :param slug: URL 别名 e.g. "seo-analysis-report" (optional)
        :param featured_image: 特色图片 URL (optional)
        :param access_token: WordPress.com Access Token (optional, 已在 Valves 配置则无需提供)
        :param site_id: WordPress.com Site ID (optional, 已在 Valves 配置则无需提供)
        :return: 创建结果，包含文章 ID 和 URL
        
        使用场景示例:
        - "写一篇关于AI的文章发布到WordPress" → 生成原创内容并发布
        - "把SEO分析结果发布成文章" → 将其他工具的分析数据整理成文章发布
        - "将上面的分析报告发布到网站" → 把之前的分析结果作为文章内容发布
        - "基于刚才的数据写一篇分析文章" → 根据其他工具返回的数据撰写并发布
        
        **重要**: 当需要发布其他工具（如SEO分析、关键词研究）的结果时，
        请将结果整理成文章格式后作为 content 参数传入。
        """
        # Resolve credentials - direct params have highest priority
        resolved_token, resolved_site_id = self._resolve_credentials(access_token, site_id)
        
        if not resolved_token or not resolved_site_id:
            return {
                "success": False,
                "error": "WordPress 凭证未配置。请提供 access_token 和 site_id 参数。"
            }
        
        payload = {"title": title, "content": content, "status": status}

        if excerpt:
            payload["excerpt"] = excerpt
        if categories:
            payload["categories"] = categories
        if tags:
            payload["tags"] = tags
        if slug:
            payload["slug"] = slug
        if featured_image:
            payload["featured_image"] = featured_image

        result = self._make_request(
            "POST", 
            f"/sites/{resolved_site_id}/posts/new", 
            data=payload,
            access_token=resolved_token,
            site_id=resolved_site_id
        )

        if result["success"]:
            post = result["data"]
            
            # Build detailed execution log
            execution_log = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🔧 TOOL EXECUTION LOG: create_article                        ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  📥 INPUT PARAMETERS:                                         ┃
┃    • title: {title[:40]}{'...' if len(title) > 40 else ''}
┃    • status: {status}
┃    • categories: {categories or '(none)'}
┃    • tags: {tags or '(none)'}
┃    • content_length: {len(content)} chars
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  🔐 CREDENTIALS (auto-resolved):                              ┃
┃    • site_id: {resolved_site_id}
┃    • token: ****{resolved_token[-4:] if len(resolved_token) > 4 else '****'}
┃    • source: Valves Configuration
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  📤 API REQUEST:                                              ┃
┃    • endpoint: /sites/{resolved_site_id}/posts/new
┃    • method: POST
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  ✅ RESULT: SUCCESS                                           ┃
┃    • post_id: {post['ID']}
┃    • url: {post['URL']}
┃    • short_url: {post.get('short_URL', 'N/A')}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""
            
            return {
                "success": True,
                "data": {
                    "post_id": post["ID"],
                    "title": post["title"],
                    "status": post["status"],
                    "url": post["URL"],
                    "short_url": post.get("short_URL", ""),
                    "edit_url": f"https://wordpress.com/post/{resolved_site_id}/{post['ID']}",
                    "created_at": post["date"],
                    "author": post.get("author", {}).get("name", ""),
                    "categories": list(post.get("categories", {}).keys()),
                    "tags": list(post.get("tags", {}).keys()),
                },
                "message": f"✅ 文章创建成功: {post['title']}\n\n📝 状态: {post['status']}\n🔗 编辑: https://wordpress.com/post/{resolved_site_id}/{post['ID']}\n🌐 URL: {post['URL']}",
                "_execution_log": execution_log
            }

        # Add execution log for failed requests too
        error_log = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🔧 TOOL EXECUTION LOG: create_article                        ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  📥 INPUT PARAMETERS:                                         ┃
┃    • title: {title[:40]}{'...' if len(title) > 40 else ''}
┃    • status: {status}
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  ❌ RESULT: FAILED                                            ┃
┃    • error: {result.get('error', 'Unknown error')}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""
        result["_execution_log"] = error_log
        return result

    def update_article(
        self,
        post_id: int,
        title: str = None,
        content: str = None,
        excerpt: str = None,
        categories: str = None,
        tags: str = None,
        slug: str = None,
        access_token: str = None,
        site_id: str = None,
        __user__: dict = None,
    ) -> dict:
        """
        更新现有文章 - 修改标题、内容、分类等
        
        :param post_id: 要更新的文章 ID（必填）
        :param title: 新标题（可选）
        :param content: 新内容（可选）
        :param excerpt: 新摘要（可选）
        :param categories: 新分类，逗号分隔（可选）
        :param tags: 新标签，逗号分隔（可选）
        :param slug: 新 URL 别名（可选）
        :return: 更新后的文章详情
        
        使用示例:
        - "修改文章ID 123 的标题为《新标题》"
        - "更新文章内容"
        """
        resolved_token, resolved_site_id = self._resolve_credentials(access_token, site_id)
        
        payload = {}

        if title is not None:
            payload["title"] = title
        if content is not None:
            payload["content"] = content
        if excerpt is not None:
            payload["excerpt"] = excerpt
        if categories is not None:
            payload["categories"] = categories
        if tags is not None:
            payload["tags"] = tags
        if slug is not None:
            payload["slug"] = slug

        if not payload:
            return {"success": False, "error": "No fields provided for update"}

        result = self._make_request(
            "POST", 
            f"/sites/{resolved_site_id}/posts/{post_id}", 
            data=payload,
            access_token=resolved_token,
            site_id=resolved_site_id
        )

        if result["success"]:
            post = result["data"]
            return {
                "success": True,
                "data": {
                    "post_id": post["ID"],
                    "title": post["title"],
                    "status": post["status"],
                    "url": post["URL"],
                    "modified_at": post["modified"],
                },
                "message": f"✅ 文章更新成功: {post['title']}\n\n🔗 URL: {post['URL']}\n⏰ 修改时间: {post['modified']}"
            }

        return result

    def publish_article(
        self, 
        post_id: int, 
        schedule_time: str = None, 
        access_token: str = None,
        site_id: str = None,
        __user__: dict = None
    ) -> dict:
        """
        发布文章（上线） - 将草稿发布或定时发布
        
        :param post_id: 要发布的文章 ID（必填）
        :param schedule_time: 定时发布时间，ISO 8601 格式，如 '2024-12-25T10:00:00'（可选）
        :return: 发布后的文章详情，包含 URL
        
        使用示例:
        - "发布文章ID 123"
        - "定时发布文章到明天上午10点"
        """
        resolved_token, resolved_site_id = self._resolve_credentials(access_token, site_id)
        
        payload = {}

        if schedule_time:
            # Schedule for future publication
            payload["status"] = "future"
            payload["date"] = schedule_time
            action = "scheduled"
        else:
            # Publish immediately
            payload["status"] = "publish"
            action = "published"

        result = self._make_request(
            "POST", 
            f"/sites/{resolved_site_id}/posts/{post_id}", 
            data=payload,
            access_token=resolved_token,
            site_id=resolved_site_id
        )

        if result["success"]:
            post = result["data"]
            return {
                "success": True,
                "data": {
                    "post_id": post["ID"],
                    "title": post["title"],
                    "status": post["status"],
                    "url": post["URL"],
                    "short_url": post.get("short_URL", ""),
                    "published_at": post["date"],
                    "action": action,
                },
                "message": f"✅ 文章{'已定时' if schedule_time else '已发布'}: {post['title']}\n\n🌐 URL: {post['URL']}\n📅 {'定时发布于' if schedule_time else '发布时间'}: {post['date']}"
            }

        return result

    def unpublish_article(
        self, 
        post_id: int, 
        target_status: str = "draft", 
        access_token: str = None,
        site_id: str = None,
        __user__: dict = None
    ) -> dict:
        """
        取消发布文章 - 将已发布的文章恢复为草稿或私密状态
        
        :param post_id: 要取消发布的文章 ID（必填）
        :param target_status: 目标状态 - "draft"(草稿，默认), "private"(私密), "trash"(回收站)
        :return: 取消发布后的文章详情
        
        使用示例:
        - "取消发布文章ID 123"
        - "将文章设为私密"
        """
        resolved_token, resolved_site_id = self._resolve_credentials(access_token, site_id)
        
        payload = {"status": target_status}

        result = self._make_request(
            "POST", 
            f"/sites/{resolved_site_id}/posts/{post_id}", 
            data=payload,
            access_token=resolved_token,
            site_id=resolved_site_id
        )

        if result["success"]:
            post = result["data"]
            status_names = {"draft": "Draft", "private": "Private", "trash": "Trash"}
            return {
                "success": True,
                "data": {
                    "post_id": post["ID"],
                    "title": post["title"],
                    "previous_status": "publish",
                    "current_status": post["status"],
                },
                "message": f"✅ Article unpublished: {post['title']}\n\n📝 New status: {status_names.get(target_status, target_status)}"
            }

        return result

    def get_article_metrics(
        self, 
        post_id: int, 
        days: int = 30, 
        include_daily_breakdown: bool = False, 
        access_token: str = None,
        site_id: str = None,
        __user__: dict = None
    ) -> dict:
        """
        获取文章性能指标 - 浏览量、点赞数、评论数等
        
        :param post_id: 文章 ID（必填）
        :param days: 查询最近天数（默认30天，最大365天）
        :param include_daily_breakdown: 是否包含每日详细数据
        :return: 文章指标，包括浏览量、点赞数、评论数等
        
        使用示例:
        - "查看文章ID 123 的表现数据"
        - "获取文章最近7天的浏览量"
        """
        resolved_token, resolved_site_id = self._resolve_credentials(access_token, site_id)
        
        # Limit days range
        days = min(max(1, days), 365)

        # 1. Get basic article info
        post_result = self._make_request(
            "GET", 
            f"/sites/{resolved_site_id}/posts/{post_id}",
            access_token=resolved_token,
            site_id=resolved_site_id
        )

        if not post_result["success"]:
            return post_result

        post = post_result["data"]

        # 2. Try to get views from top-posts
        total_views = 0
        views_source = "unavailable"
        daily_views = []

        # Method A: Find in top-posts endpoint
        top_posts_params = {"num": days, "max": 100}

        top_posts_result = self._make_request(
            "GET", 
            f"/sites/{resolved_site_id}/stats/top-posts", 
            params=top_posts_params,
            access_token=resolved_token,
            site_id=resolved_site_id
        )

        if top_posts_result["success"]:
            top_posts_data = top_posts_result["data"]

            # Find in summary.postviews
            if "summary" in top_posts_data and "postviews" in top_posts_data["summary"]:
                for p in top_posts_data["summary"]["postviews"]:
                    if isinstance(p, dict) and p.get("id") == post_id:
                        total_views = p.get("views", 0)
                        views_source = "top-posts-summary"
                        break

            # Accumulate from days
            if "days" in top_posts_data and isinstance(top_posts_data["days"], dict):
                for day_date, day_info in top_posts_data["days"].items():
                    if isinstance(day_info, dict) and "postviews" in day_info:
                        for p in day_info["postviews"]:
                            if isinstance(p, dict) and p.get("id") == post_id:
                                views = p.get("views", 0)
                                total_views += views
                                if include_daily_breakdown:
                                    daily_views.append({"date": day_date, "views": views})

                if total_views > 0:
                    views_source = "top-posts"

        # Method B: Try stats/post/{id} if top-posts didn't find it
        if total_views == 0:
            post_stats_result = self._make_request(
                "GET", 
                f"/sites/{resolved_site_id}/stats/post/{post_id}",
                access_token=resolved_token,
                site_id=resolved_site_id
            )

            if post_stats_result["success"]:
                stats_data = post_stats_result["data"]
                total_views = stats_data.get("views", 0)
                views_source = "post-stats"

                # Get daily data
                if include_daily_breakdown and "data" in stats_data:
                    for date_str, view_count in stats_data["data"].items():
                        daily_views.append({"date": date_str, "views": view_count})

        # 3. Get site-wide stats as reference
        site_stats = {}
        summary_result = self._make_request(
            "GET", 
            f"/sites/{resolved_site_id}/stats/summary",
            access_token=resolved_token,
            site_id=resolved_site_id
        )
        if summary_result["success"]:
            site_stats = {
                "site_views_today": summary_result["data"].get("views", 0),
                "site_visitors_today": summary_result["data"].get("visitors", 0),
                "site_followers": summary_result["data"].get("followers", 0),
            }

        # 4. Build return data
        metrics = {
            "success": True,
            "data": {
                "post_id": post["ID"],
                "title": post["title"],
                "status": post["status"],
                "url": post["URL"],
                # Basic metrics
                "metrics": {
                    "views": total_views,
                    "likes": post.get("like_count", 0),
                    "comments": post.get("comment_count", 0),
                    "word_count": post.get("word_count", 0),
                    "views_source": views_source,
                },
                # Time information
                "dates": {
                    "published": post.get("date"),
                    "modified": post.get("modified"),
                    "stats_period": f"Last {days} days",
                },
                # Taxonomy
                "taxonomy": {
                    "categories": list(post.get("categories", {}).keys()),
                    "tags": list(post.get("tags", {}).keys()),
                },
                # Site context
                "site_context": site_stats,
            },
        }

        # Add daily breakdown
        if include_daily_breakdown and daily_views:
            metrics["data"]["daily_breakdown"] = sorted(
                daily_views, key=lambda x: x["date"], reverse=True
            )

        # Calculate averages
        if days > 0 and total_views > 0:
            metrics["data"]["metrics"]["avg_daily_views"] = round(total_views / days, 2)

        # Add note if views unavailable
        if total_views == 0:
            metrics["data"]["metrics"]["note"] = "View data unavailable (article may be too new or has no visits yet)"

        # Format message
        metrics["message"] = f"📊 Metrics for: {post['title']}\n\n👁️ Views: {total_views}\n❤️ Likes: {post.get('like_count', 0)}\n💬 Comments: {post.get('comment_count', 0)}\n📅 Period: Last {days} days"

        return metrics

    def list_articles_by_topic(
        self,
        category: str = None,
        tag: str = None,
        status: str = "any",
        search: str = None,
        order_by: str = "date",
        order: str = "DESC",
        number: int = 20,
        page: int = 1,
        include_views: bool = True,
        access_token: str = None,
        site_id: str = None,
        __user__: dict = None,
    ) -> dict:
        """
        文章列表/库存 - 按条件筛选和列出文章
        
        :param category: 按分类筛选，如 "科技"（可选）
        :param tag: 按标签筛选，如 "Python"（可选）
        :param status: 按状态筛选 - "publish"(已发布), "draft"(草稿), "private"(私密), "any"(全部，默认)
        :param search: 搜索关键词，在标题和内容中搜索（可选）
        :param order_by: 排序字段 - "date"(日期), "modified"(修改时间), "title"(标题), "comment_count"(评论数)
        :param order: 排序方向 - "DESC"(降序，默认) 或 "ASC"(升序)
        :param number: 返回数量（默认20，最大100）
        :param page: 页码，从1开始（用于分页）
        :param include_views: 是否包含浏览量数据
        :return: 文章列表及指标
        
        使用示例:
        - "列出所有已发布的文章"
        - "查找关于SEO的文章"
        - "列出科技分类下的草稿"
        """
        resolved_token, resolved_site_id = self._resolve_credentials(access_token, site_id)
        
        # Limit return count
        number = min(max(1, number), 100)

        # Build query parameters
        params = {"number": number, "page": page, "order_by": order_by, "order": order}

        if status and status != "any":
            params["status"] = status
        else:
            params["status"] = "any"

        if category:
            params["category"] = category
        if tag:
            params["tag"] = tag
        if search:
            params["search"] = search

        result = self._make_request(
            "GET", 
            f"/sites/{resolved_site_id}/posts/", 
            params=params,
            access_token=resolved_token,
            site_id=resolved_site_id
        )

        if not result["success"]:
            return result

        posts_data = result["data"]
        posts = posts_data.get("posts", [])

        # Get view data
        views_map = {}
        if include_views:
            top_posts_result = self._make_request(
                "GET",
                f"/sites/{resolved_site_id}/stats/top-posts",
                params={"num": 30, "max": 100},
                access_token=resolved_token,
                site_id=resolved_site_id
            )

            if top_posts_result["success"]:
                top_data = top_posts_result["data"]
                # Extract from summary
                if "summary" in top_data and "postviews" in top_data["summary"]:
                    for p in top_data["summary"]["postviews"]:
                        views_map[p.get("id")] = p.get("views", 0)
                # Accumulate from days
                if "days" in top_data and isinstance(top_data["days"], dict):
                    for date_str, day_info in top_data["days"].items():
                        if isinstance(day_info, dict) and "postviews" in day_info:
                            for p in day_info["postviews"]:
                                if isinstance(p, dict):
                                    pid = p.get("id")
                                    views = p.get("views", 0)
                                    if pid:
                                        views_map[pid] = views_map.get(pid, 0) + views

        # Process article list
        articles = []
        status_counts = {"publish": 0, "draft": 0, "private": 0, "future": 0}
        total_views = 0
        total_likes = 0
        total_comments = 0

        for post in posts:
            post_status = post.get("status", "unknown")
            if post_status in status_counts:
                status_counts[post_status] += 1

            like_count = post.get("like_count", 0)
            comment_count = post.get("comment_count", 0)
            post_views = views_map.get(post["ID"], 0)

            total_views += post_views
            total_likes += like_count
            total_comments += comment_count

            articles.append(
                {
                    "id": post["ID"],
                    "title": post["title"],
                    "status": post_status,
                    "url": post["URL"],
                    "date": post.get("date"),
                    "modified": post.get("modified"),
                    "excerpt": (
                        post.get("excerpt", "")[:150] + "..." if post.get("excerpt") else ""
                    ),
                    "metrics": {
                        "views": post_views,
                        "likes": like_count,
                        "comments": comment_count,
                        "word_count": post.get("word_count", 0),
                    },
                    "categories": list(post.get("categories", {}).keys()),
                    "tags": list(post.get("tags", {}).keys()),
                }
            )

        # Sort by views if requested
        if include_views and order_by == "views":
            articles = sorted(
                articles, key=lambda x: x["metrics"]["views"], reverse=(order == "DESC")
            )

        # Build summary message
        filter_desc = []
        if category:
            filter_desc.append(f"Category: {category}")
        if tag:
            filter_desc.append(f"Tag: {tag}")
        if status != "any":
            filter_desc.append(f"Status: {status}")
        if search:
            filter_desc.append(f"Search: '{search}'")

        message = f"📚 Content Inventory\n\n"
        if filter_desc:
            message += f"🔍 Filters: {', '.join(filter_desc)}\n"
        message += f"📊 Found: {len(articles)} articles\n"
        message += f"👁️ Total views: {total_views}\n"
        message += f"❤️ Total likes: {total_likes}\n"
        message += f"💬 Total comments: {total_comments}"

        # Build summary info
        return {
            "success": True,
            "data": {
                # Filter conditions
                "filters": {
                    "category": category,
                    "tag": tag,
                    "status": status,
                    "search": search,
                },
                # Pagination info
                "pagination": {
                    "total": posts_data.get("found", len(articles)),
                    "page": page,
                    "per_page": number,
                    "total_pages": (
                        (posts_data.get("found", 0) + number - 1) // number
                        if number > 0
                        else 0
                    ),
                },
                # Summary statistics
                "summary": {
                    "total_articles": len(articles),
                    "status_breakdown": status_counts,
                    "total_views": total_views,
                    "total_likes": total_likes,
                    "total_comments": total_comments,
                },
                # Article list
                "articles": articles,
            },
            "message": message
        }

    def get_site_stats(
        self, 
        days: int = 7, 
        access_token: str = None,
        site_id: str = None,
        __user__: dict = None
    ) -> dict:
        """
        获取站点统计数据 - 浏览量、访客数、热门文章等
        
        :param days: 统计天数（默认7天，最大365天）
        :return: 站点浏览量、访客数、热门文章等数据
        
        使用示例:
        - "查看网站统计数据"
        - "获取最近30天的站点表现"
        """
        resolved_token, resolved_site_id = self._resolve_credentials(access_token, site_id)
        
        days = min(max(1, days), 365)

        # 1. Get site summary
        summary_result = self._make_request(
            "GET", 
            f"/sites/{resolved_site_id}/stats/summary",
            access_token=resolved_token,
            site_id=resolved_site_id
        )

        # 2. Get top posts
        top_posts_result = self._make_request(
            "GET", 
            f"/sites/{resolved_site_id}/stats/top-posts", 
            params={"num": days, "max": 10},
            access_token=resolved_token,
            site_id=resolved_site_id
        )

        # 3. Get site basic info
        site_result = self._make_request(
            "GET", 
            f"/sites/{resolved_site_id}",
            access_token=resolved_token,
            site_id=resolved_site_id
        )

        # Build return data
        data = {"period": f"Last {days} days", "today": {}, "top_posts": [], "site_info": {}}

        if summary_result["success"]:
            s = summary_result["data"]
            data["today"] = {
                "views": s.get("views", 0),
                "visitors": s.get("visitors", 0),
                "likes": s.get("likes", 0),
                "comments": s.get("comments", 0),
                "followers": s.get("followers", 0),
            }

        if top_posts_result["success"]:
            top_data = top_posts_result["data"]
            if "summary" in top_data and "postviews" in top_data["summary"]:
                for p in top_data["summary"]["postviews"][:10]:
                    data["top_posts"].append(
                        {
                            "id": p.get("id"),
                            "title": p.get("title", ""),
                            "views": p.get("views", 0),
                            "url": p.get("href", ""),
                        }
                    )

        if site_result["success"]:
            s = site_result["data"]
            data["site_info"] = {
                "name": s.get("name", ""),
                "description": s.get("description", ""),
                "url": s.get("URL", ""),
                "post_count": s.get("post_count", 0),
            }

        # Build message
        message = f"📊 Site Statistics ({data['period']})\n\n"
        if data["today"]:
            message += f"📈 Today:\n"
            message += f"  👁️ Views: {data['today']['views']}\n"
            message += f"  👥 Visitors: {data['today']['visitors']}\n"
            message += f"  👤 Followers: {data['today']['followers']}\n\n"
        if data["top_posts"]:
            message += f"🔥 Top Posts:\n"
            for i, post in enumerate(data["top_posts"][:5], 1):
                message += f"  {i}. {post['title']} ({post['views']} views)\n"

        return {"success": True, "data": data, "message": message}


# ==================== 兼容性别名 ====================
# 支持在 Tools 页面和 Functions 页面导入

Functions = Tools  # 用于 Functions 页面
Function = Tools   # 某些版本使用单数形式

