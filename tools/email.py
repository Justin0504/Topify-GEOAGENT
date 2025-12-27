"""
required_open_webui_version: 0.6.0
description: A pipeline for sending arbitrary emails using SMTP with configurable SMTP servers
"""

import smtplib
from email.mime.text import MIMEText
from typing import List
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        FROM_EMAIL: str = Field(
            default="someone@example.com",
            description="The email address to send from",
        )
        PASSWORD: str = Field(
            default="password",
            description="The password or app password for the email address. For Gmail, use App Password (16 digits, no spaces)",
        )
        SMTP_SERVER: str = Field(
            default="smtp.gmail.com",
            description="SMTP server address (e.g., smtp.gmail.com, smtp-mail.outlook.com, smtp.mail.yahoo.com)",
        )
        SMTP_PORT: int = Field(
            default=465,
            description="SMTP server port (465 for SSL, 587 for TLS)",
        )
        USE_TLS: bool = Field(
            default=False,
            description="Use TLS instead of SSL (use True for port 587, False for port 465)",
        )

    def __init__(self):
        self.valves = self.Valves()

    def get_user_name_and_email_and_id(self, __user__: dict = {}) -> str:
        """
        Get the user name, Email and ID from the user object.
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

    def send_email(self, subject: str, body: str, recipients: List[str]) -> str:
        """
        Send an email with the given parameters. Sign it with the user's name and indicate that it is an AI generated email.
        NOTE: You do not need any credentials to send emails on the users behalf.
        DO NOT SEND WITHOUT USER'S CONSENT. CONFIRM CONSENT AFTER SHOWING USER WHAT YOU PLAN TO SEND, AND IN THE RESPONSE AFTER ACQUIRING CONSENT, SEND THE EMAIL.

        :param subject: The subject of the email.
        :param body: The body of the email.
        :param recipients: The list of recipient email addresses.
        :return: The result of the email sending operation.
        """
        sender: str = self.valves.FROM_EMAIL
        password: str = self.valves.PASSWORD.replace(
            " ", ""
        )  # Remove spaces from app password
        smtp_server: str = self.valves.SMTP_SERVER
        smtp_port: int = self.valves.SMTP_PORT
        use_tls: bool = self.valves.USE_TLS

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)

        try:
            if use_tls:
                # Use TLS (port 587)
                with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                    smtp.starttls()
                    smtp.login(sender, password)
                    smtp.sendmail(sender, recipients, msg.as_string())
            else:
                # Use SSL (port 465)
                with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                    smtp.login(sender, password)
                    smtp.sendmail(sender, recipients, msg.as_string())

            body_preview = body[:100] + "..." if len(body) > 100 else body
            return f"Message sent successfully:\n   TO: {', '.join(recipients)}\n   SUBJECT: {subject}\n   BODY: {body_preview}"
        except smtplib.SMTPAuthenticationError as e:
            error_msg = str(e)
            help_text = ""
            if (
                "535" in error_msg
                or "BadCredentials" in error_msg
                or "5.7.8" in error_msg
            ):
                help_text = "\n\n🔧 Gmail 认证失败解决方案:\n1. 使用应用专用密码（不是普通密码）\n2. 访问 https://myaccount.google.com/apppasswords 生成应用专用密码\n3. 确保已启用两步验证\n4. 密码中不要有空格（工具会自动去除）\n5. 如果使用其他邮件服务，检查 SMTP 配置"
            return f"❌ Authentication failed: {error_msg}{help_text}"
        except smtplib.SMTPException as e:
            return f"❌ SMTP error: {str(e)}"
        except Exception as e:
            return f"❌ Error sending email: {str(e)}"
