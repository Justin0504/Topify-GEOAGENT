"""
required_open_webui_version: 0.6.0
description: WordPress Credential Manager - Store and cache WordPress credentials for the session
requirements: none
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


# Global credential cache for the session
_credential_cache = {
    "access_token": "",
    "site_id": "",
    "username": ""
}


class Tools:
    """
    WordPress Credential Manager
    
    Securely store and manage WordPress.com credentials for content publishing.
    Credentials are cached in memory for the current session.
    
    **IMPORTANT**: After setting credentials with this tool, the WordPress CMS Tool
    can automatically use them for publishing.
    """

    class Valves(BaseModel):
        WP_ACCESS_TOKEN: str = Field(
            default="",
            description="WordPress.com API Access Token (fallback if not provided in method call)"
        )
        WP_SITE_ID: str = Field(
            default="",
            description="WordPress.com Site ID (fallback if not provided in method call)"
        )
        WP_API_BASE: str = Field(
            default="https://public-api.wordpress.com/rest/v1.1",
            description="WordPress.com API Base URL"
        )

    def __init__(self):
        self.valves = self.Valves()

    def set_wordpress_credentials(
        self,
        access_token: Optional[str] = None,
        site_id: Optional[str] = None,
        username: Optional[str] = "",
    ) -> str:
        """
        Store WordPress credentials for the current session.
        After setting credentials, you can use WordPress CMS Tool to publish articles.
        
        If access_token or site_id are not provided, will use values from Valves configuration.
        
        :param access_token: Your WordPress.com Access Token (optional, uses Valves if not provided)
        :param site_id: Your WordPress.com Site ID e.g. "251193948" or "example.wordpress.com" (optional, uses Valves if not provided)
        :param username: Your WordPress.com username (optional, for reference)
        :return: Confirmation message
        
        Example:
        - User says: "设置WordPress凭证" (will use Valves configuration)
        - User says: "设置WordPress凭证, token是xxx, site_id是123" (will use provided values)
        """
        global _credential_cache
        
        def clean_credential(value: str) -> str:
            """Clean credential value - remove all whitespace including newlines."""
            if not value:
                return ""
            return ''.join(value.split())
        
        try:
            # Resolve credentials: Valves has HIGHEST priority, then fallback to provided values
            # This prevents LLM from passing incorrect credentials
            
            # Priority 1: Valves configuration (最高优先级 - 管理员配置)
            resolved_token = clean_credential(self.valves.WP_ACCESS_TOKEN) if self.valves.WP_ACCESS_TOKEN else ""
            resolved_site_id = clean_credential(self.valves.WP_SITE_ID) if self.valves.WP_SITE_ID else ""
            
            # Priority 2: Fallback to provided parameters (if Valves not configured)
            if not resolved_token and access_token:
                resolved_token = clean_credential(access_token)
            if not resolved_site_id and site_id:
                resolved_site_id = clean_credential(str(site_id))
            
            # Validate that we have credentials
            if not resolved_token:
                return """❌ 未提供 Access Token！

请通过以下方式之一提供凭证：
1. 在工具设置(Valves)中配置 WP_ACCESS_TOKEN
2. 在调用时直接提供 access_token 参数
"""
            
            if not resolved_site_id:
                return """❌ 未提供 Site ID！

请通过以下方式之一提供凭证：
1. 在工具设置(Valves)中配置 WP_SITE_ID
2. 在调用时直接提供 site_id 参数
"""
            
            # Store in global cache
            _credential_cache["access_token"] = resolved_token
            _credential_cache["site_id"] = resolved_site_id
            _credential_cache["username"] = username or ""
            
            # Also set as environment variables for WordPress CMS Tool
            os.environ['WP_ACCESS_TOKEN'] = resolved_token
            os.environ['WP_SITE_ID'] = resolved_site_id
            os.environ['WP_USERNAME'] = username or ""
            
            masked_token = f"****{resolved_token[-4:]}" if len(resolved_token) > 4 else "****"
            
            # Indicate source of credentials
            token_source = "参数提供" if access_token else "Valves配置"
            site_source = "参数提供" if site_id else "Valves配置"
            
            return f"""✅ WordPress 凭证已配置成功！

**已存储信息：**
- 用户名: {username or '(未设置)'}
- Site ID: {resolved_site_id} (来源: {site_source})
- Access Token: {masked_token} (来源: {token_source})

**现在你可以使用 WordPress CMS Tool 发布文章了！**

示例命令：
- "写一篇关于AI的文章并发布到WordPress"
- "创建一篇草稿文章，标题是《测试》"
"""
                
        except Exception as e:
            return f"❌ 存储凭证时出错: {str(e)}"

    def get_wordpress_credentials(self) -> str:
        """
        Check currently stored WordPress credentials (masked for security).
        
        :return: Current credential status
        """
        global _credential_cache
        
        def clean_credential(value: str) -> str:
            """Clean credential value - remove all whitespace including newlines."""
            if not value:
                return ""
            return ''.join(value.split())
        
        try:
            # Check global cache first
            token = _credential_cache.get("access_token", "")
            site_id = _credential_cache.get("site_id", "")
            username = _credential_cache.get("username", "")
            token_source = "缓存"
            site_source = "缓存"
            
            # Fallback to environment variables
            if not token:
                token = clean_credential(os.environ.get('WP_ACCESS_TOKEN', ''))
                if token:
                    token_source = "环境变量"
            if not site_id:
                site_id = clean_credential(os.environ.get('WP_SITE_ID', ''))
                if site_id:
                    site_source = "环境变量"
            if not username:
                username = os.environ.get('WP_USERNAME', '')
            
            # Fallback to Valves configuration
            if not token and self.valves.WP_ACCESS_TOKEN:
                token = clean_credential(self.valves.WP_ACCESS_TOKEN)
                token_source = "Valves配置"
            if not site_id and self.valves.WP_SITE_ID:
                site_id = clean_credential(self.valves.WP_SITE_ID)
                site_source = "Valves配置"
            
            if token and site_id:
                masked_token = f"****{token[-4:]}" if len(token) > 4 else "****"
                return f"""📋 当前 WordPress 凭证：

**用户名:** {username or '(未设置)'}
**Site ID:** {site_id} (来源: {site_source})
**Access Token:** {masked_token} (来源: {token_source})
**状态:** ✅ 已配置

你可以使用 WordPress CMS Tool 发布文章。
"""
            else:
                missing = []
                if not token:
                    missing.append("Access Token")
                if not site_id:
                    missing.append("Site ID")
                    
                return f"""❌ 未配置完整的 WordPress 凭证。

**缺少:** {', '.join(missing)}

请通过以下方式之一配置凭证：
1. 在工具设置(Valves)中配置 WP_ACCESS_TOKEN 和 WP_SITE_ID
2. 使用 `set_wordpress_credentials` 设置凭证
3. 在调用 WordPress CMS Tool 时直接提供 access_token 和 site_id 参数
"""
                    
        except Exception as e:
            return f"❌ 获取凭证时出错: {str(e)}"

    def clear_wordpress_credentials(self) -> str:
        """
        Clear stored WordPress credentials.
        
        :return: Confirmation message
        """
        global _credential_cache
        
        try:
            # Clear global cache
            _credential_cache["access_token"] = ""
            _credential_cache["site_id"] = ""
            _credential_cache["username"] = ""
            
            # Clear environment variables
            os.environ.pop('WP_ACCESS_TOKEN', None)
            os.environ.pop('WP_SITE_ID', None)
            os.environ.pop('WP_USERNAME', None)
            
            return "✅ WordPress 凭证已清除！"
            
        except Exception as e:
            return f"❌ 清除凭证时出错: {str(e)}"


def get_cached_credentials():
    """
    Helper function to get cached credentials.
    Can be imported by other tools.
    """
    global _credential_cache
    
    token = _credential_cache.get("access_token", "") or os.environ.get('WP_ACCESS_TOKEN', '')
    site_id = _credential_cache.get("site_id", "") or os.environ.get('WP_SITE_ID', '')
    
    return token, site_id
