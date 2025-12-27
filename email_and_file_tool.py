"""
title: 邮件发送与文件保存工具
description: 【发送邮件】通过 SMTP 发送邮件 | 【保存文件】将内容保存为本地文件（TXT、HTML、Markdown、JSON 等）
author: GEO Agent
version: 1.0.0
required_open_webui_version: 0.6.0
requirements: pydantic
"""

import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Tools:
    """
    邮件发送与文件保存工具
    
    ═══════════════════════════════════════════════════════════════
    🎯 快速匹配指南
    ═══════════════════════════════════════════════════════════════
    
    📧 用户说"发邮件"、"发送邮件"、"邮件发给xxx"
       → 调用 send_email
    
    💾 用户说"保存文件"、"保存到本地"、"导出文件"、"生成文件"
       → 调用 save_file
    
    📄 用户说"保存报告"、"保存分析结果"、"导出报告"
       → 调用 save_file
    
    ═══════════════════════════════════════════════════════════════
    """

    class Valves(BaseModel):
        # 文件保存配置
        OUTPUT_PATH: str = Field(
            default="/Users/justin/Downloads/open-webui-main/output",
            description="文件保存的本地目录路径"
        )
        # 邮件配置
        FROM_EMAIL: str = Field(
            default="someone@example.com",
            description="发件人邮箱地址",
        )
        PASSWORD: str = Field(
            default="password",
            description="邮箱密码或应用专用密码（Gmail 使用 16 位应用专用密码，无空格）",
        )
        SMTP_SERVER: str = Field(
            default="smtp.gmail.com",
            description="SMTP 服务器地址（如 smtp.gmail.com, smtp.qq.com, smtp.163.com）",
        )
        SMTP_PORT: int = Field(
            default=465,
            description="SMTP 端口（SSL 用 465，TLS 用 587）",
        )
        USE_TLS: bool = Field(
            default=False,
            description="使用 TLS 而非 SSL（端口 587 用 True，端口 465 用 False）",
        )

    def __init__(self):
        self.valves = self.Valves()

    def save_file(
        self,
        content: str,
        filename: str,
        file_type: str = "txt",
        encoding: str = "utf-8",
        __user__: dict = None
    ) -> str:
        """
        💾 保存文件到本地 - 将内容保存为本地文件
        
        ════════════════════════════════════════════════════════
        🎯 何时使用此工具
        ════════════════════════════════════════════════════════
        
        当用户说以下任何一种时，使用此工具：
        
        ✅ "保存到本地"、"保存文件"、"保存为文件"
        ✅ "导出报告"、"导出文件"、"导出结果"
        ✅ "生成文件"、"创建文件"、"写入文件"
        ✅ "保存分析结果"、"保存这个内容"
        ✅ "把这个保存下来"、"存成文件"
        
        ════════════════════════════════════════════════════════
        📋 参数说明
        ════════════════════════════════════════════════════════
        
        :param content: 【必填】要保存的内容
            ✓ 可以是纯文本、HTML、Markdown、JSON 等
            
        :param filename: 【必填】文件名（不含扩展名）
            ✓ 示例: "seo_report", "analysis_result", "my_article"
            ✓ 系统会自动添加时间戳避免重名
            
        :param file_type: 文件类型/扩展名（默认 txt）
            • txt - 纯文本
            • md - Markdown 格式
            • html - HTML 网页
            • json - JSON 数据
            • csv - CSV 表格
            
        :param encoding: 编码格式（默认 utf-8）
        
        :return: 保存结果，包含文件路径
        
        ════════════════════════════════════════════════════════
        📝 典型用户查询 → 参数映射
        ════════════════════════════════════════════════════════
        
        "把 SEO 分析结果保存到本地"
        → content=分析结果, filename="seo_analysis", file_type="md"
        
        "保存这篇文章为 HTML 文件"
        → content=文章内容, filename="article", file_type="html"
        
        "把数据导出成 JSON"
        → content=数据, filename="data", file_type="json"
        """
        if not content:
            return "❌ 请提供要保存的内容"
        
        if not filename:
            return "❌ 请提供文件名"
        
        # 清理文件名（移除特殊字符）
        safe_filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', ' ')).strip()
        safe_filename = safe_filename.replace(' ', '_')
        
        if not safe_filename:
            safe_filename = "output"
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{safe_filename}_{timestamp}.{file_type}"
        
        # 确保输出目录存在
        output_dir = self.valves.OUTPUT_PATH
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            return f"❌ 无法创建输出目录: {str(e)}"
        
        # 完整文件路径
        file_path = os.path.join(output_dir, full_filename)
        
        try:
            # 如果是 JSON 类型，尝试格式化
            if file_type == "json":
                try:
                    # 尝试解析并美化 JSON
                    parsed = json.loads(content) if isinstance(content, str) else content
                    content = json.dumps(parsed, ensure_ascii=False, indent=2)
                except (json.JSONDecodeError, TypeError):
                    # 如果不是有效 JSON，直接保存原内容
                    pass
            
            # 写入文件
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            size_str = f"{file_size} bytes"
            if file_size > 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            if file_size > 1024 * 1024:
                size_str = f"{file_size / (1024 * 1024):.2f} MB"
            
            return f"""✅ 文件保存成功！

📄 文件名: {full_filename}
📁 路径: {file_path}
📊 大小: {size_str}
📝 类型: {file_type.upper()}
🕐 时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        except PermissionError:
            return f"❌ 没有写入权限: {file_path}"
        except Exception as e:
            return f"❌ 保存文件失败: {str(e)}"

    def list_saved_files(self, __user__: dict = None) -> str:
        """
        📂 列出已保存的文件 - 查看输出目录中的所有文件
        
        当用户说"查看保存的文件"、"列出文件"、"看看保存了什么"时使用
        
        :return: 文件列表
        """
        output_dir = self.valves.OUTPUT_PATH
        
        if not os.path.exists(output_dir):
            return f"📂 输出目录不存在: {output_dir}"
        
        try:
            files = os.listdir(output_dir)
            if not files:
                return f"📂 输出目录为空: {output_dir}"
            
            # 按修改时间排序
            files_with_info = []
            for f in files:
                fp = os.path.join(output_dir, f)
                if os.path.isfile(fp):
                    mtime = os.path.getmtime(fp)
                    size = os.path.getsize(fp)
                    files_with_info.append((f, mtime, size))
            
            # 按时间倒序
            files_with_info.sort(key=lambda x: x[1], reverse=True)
            
            lines = [f"📂 输出目录: {output_dir}\n"]
            for i, (fname, mtime, size) in enumerate(files_with_info[:20], 1):
                mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                size_str = f"{size} B" if size < 1024 else f"{size/1024:.1f} KB"
                lines.append(f"{i}. {fname} ({size_str}, {mtime_str})")
            
            if len(files_with_info) > 20:
                lines.append(f"\n... 还有 {len(files_with_info) - 20} 个文件")
            
            return "\n".join(lines)
        
        except Exception as e:
            return f"❌ 读取目录失败: {str(e)}"

    def get_user_name_and_email_and_id(self, __user__: dict = {}) -> str:
        """
        获取用户信息
        """
        result = ""
        if "name" in __user__:
            result += f"User: {__user__['name']}"
        if "id" in __user__:
            result += f" (ID: {__user__['id']})"
        if "email" in __user__:
            result += f" (Email: {__user__['email']})"
        if result == "":
            result = "User: Unknown"
        return result

    def send_email(
        self,
        subject: str,
        body: str,
        recipients: List[str],
        attachment_path: Optional[str] = None,
        __user__: dict = None
    ) -> str:
        """
        📧 发送邮件 - 通过 SMTP 发送邮件
        
        ════════════════════════════════════════════════════════
        🎯 何时使用此工具
        ════════════════════════════════════════════════════════
        
        当用户说以下任何一种时，使用此工具：
        
        ✅ "发邮件"、"发送邮件"、"发email"
        ✅ "邮件发给xxx"、"把这个发给xxx"
        ✅ "发送到邮箱"、"发到xxx@xxx.com"
        
        ════════════════════════════════════════════════════════
        ⚠️ 重要提醒
        ════════════════════════════════════════════════════════
        
        发送邮件前必须：
        1. 向用户确认发送内容
        2. 获得用户明确同意后再发送
        
        ════════════════════════════════════════════════════════
        📋 参数说明
        ════════════════════════════════════════════════════════
        
        :param subject: 【必填】邮件主题
        :param body: 【必填】邮件正文
        :param recipients: 【必填】收件人邮箱列表
            ✓ 示例: ["user@example.com"] 或 ["a@x.com", "b@y.com"]
        :param attachment_path: 附件文件路径（可选）
            ✓ 可以附加之前保存的文件
            
        :return: 发送结果
        
        ════════════════════════════════════════════════════════
        📝 典型用户查询
        ════════════════════════════════════════════════════════
        
        "把分析报告发到 xxx@gmail.com"
        "发一封邮件给 user@example.com，主题是..."
        """
        sender: str = self.valves.FROM_EMAIL
        password: str = self.valves.PASSWORD.replace(" ", "")
        smtp_server: str = self.valves.SMTP_SERVER
        smtp_port: int = self.valves.SMTP_PORT
        use_tls: bool = self.valves.USE_TLS

        # 创建邮件
        if attachment_path:
            msg = MIMEMultipart()
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 添加附件
            if os.path.exists(attachment_path):
                try:
                    with open(attachment_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{os.path.basename(attachment_path)}"'
                    )
                    msg.attach(part)
                except Exception as e:
                    return f"❌ 无法添加附件: {str(e)}"
            else:
                return f"❌ 附件不存在: {attachment_path}"
        else:
            msg = MIMEText(body, 'plain', 'utf-8')
        
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)

        try:
            if use_tls:
                with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                    smtp.starttls()
                    smtp.login(sender, password)
                    smtp.sendmail(sender, recipients, msg.as_string())
            else:
                with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                    smtp.login(sender, password)
                    smtp.sendmail(sender, recipients, msg.as_string())

            body_preview = body[:100] + "..." if len(body) > 100 else body
            attachment_info = f"\n   📎 附件: {os.path.basename(attachment_path)}" if attachment_path else ""
            
            return f"""✅ 邮件发送成功！

📬 收件人: {', '.join(recipients)}
📝 主题: {subject}
📄 内容预览: {body_preview}{attachment_info}
🕐 时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        except smtplib.SMTPAuthenticationError as e:
            error_msg = str(e)
            help_text = ""
            if "535" in error_msg or "BadCredentials" in error_msg or "5.7.8" in error_msg:
                help_text = """

🔧 认证失败解决方案:
• Gmail: 使用应用专用密码 https://myaccount.google.com/apppasswords
• QQ邮箱: 使用授权码（在邮箱设置中获取）
• 163邮箱: 使用授权码（在邮箱设置中获取）
• 确保已启用 SMTP 服务"""
            return f"❌ 认证失败: {error_msg}{help_text}"
        except smtplib.SMTPException as e:
            return f"❌ SMTP 错误: {str(e)}"
        except Exception as e:
            return f"❌ 发送失败: {str(e)}"


# ==================== 兼容性别名 ====================
Functions = Tools
Function = Tools

