"""
title: Anthropic API Integration
author: grandx, based on Balaxxe & lavantien
version: 0.3.0
license: MIT
requirements: pydantic>=2.0.0
environment_variables:
    - ANTHROPIC_API_KEY (required)
    - THINKING_BUDGET_TOKENS

Supports:
- All Claude models (Opus 4.5, Opus 4, Sonnet 4, Sonnet 3.7, Sonnet 3.5)
- Streaming responses
- Image processing with validation
- Prompt caching (5m and 1h)
- Function calling (OpenAI format conversion)
- PDF processing
- Thinking
- Citations
- Files API references
- Cache Control
"""

import os
import json
import logging
import asyncio
import aiohttp
from datetime import datetime
from typing import (
    List,
    Union,
    Dict,
    Optional,
    AsyncIterator,
    AsyncGenerator,
)
from pydantic import BaseModel, Field
from open_webui.utils.misc import pop_system_message
from types import SimpleNamespace


class Pipe:
    API_VERSION = "2023-06-01"
    MODEL_URL = "https://api.anthropic.com/v1/messages"
    SUPPORTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    MAX_IMAGE_SIZE = 5 * 1024 * 1024
    MAX_PDF_SIZE = 32 * 1024 * 1024
    TOTAL_MAX_IMAGE_SIZE = 100 * 1024 * 1024
    MAX_IMAGES_PER_REQUEST = 100

    MODEL_MAX_TOKENS = {
        # Claude 4.5 Opus models (最新旗舰模型 - 2025年5月发布)
        "claude-opus-4-5-20250514": 32000,
        "claude-4-5-opus-20250514": 32000,  # 备用命名格式
        # Claude 4 models
        "claude-opus-4-20250514": 32000,
        "claude-opus-4-0": 32000,
        "claude-sonnet-4-20250514": 64000,
        "claude-sonnet-4-0": 64000,
        # Claude 3.7 models
        "claude-3-7-sonnet-20250219": 128000,
        "claude-3-7-sonnet-latest": 128000,
        # Claude 3.5 models
        "claude-3-5-sonnet-20241022": 8192,
        "claude-3-5-sonnet-20240620": 8192,
        "claude-3-5-sonnet-latest": 8192,
    }

    THINKING_BUDGET_TOKENS = 16000
    PDF_HEADER = "pdfs-2024-09-25"
    PROMPT_CACHE_HEADER = "prompt-caching-2024-07-31"
    OUTPUT128K_HEADER = "output-128k-2025-02-19"
    EXTENDED_CACHE_HEADER = "extended-cache-ttl-2025-04-11"
    INTERLEAVED_THINKING_HEADER = "interleaved-thinking-2025-05-14"
    FILES_API_HEADER = "files-api-2025-04-14"
    REQUEST_TIMEOUT = 300

    class Valves(BaseModel):
        ANTHROPIC_API_KEY: str = Field(
            default=os.getenv("ANTHROPIC_API_KEY", ""),
            description="Your Anthropic API key",
        )
        THINKING_BUDGET_TOKENS: int = Field(default=16000, ge=0, le=96000)

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.type = "manifold"
        self.id = "anthropic"
        self.valves = self.Valves()
        self.request_id = None

    def get_anthropic_models(self) -> List[dict]:
        models = []
        
        # Claude 4.5 Opus models (最新旗舰模型 - 2025年5月发布)
        # 这是 Anthropic 最强大的模型，适合复杂推理、代码生成、创意写作
        for name in [
            "claude-opus-4-5-20250514",
            "claude-opus-4-5-20250514-thinking",  # 带扩展思考的版本
            "claude-4-5-opus-20250514",           # 备用命名格式
        ]:
            models.append(
                {
                    "id": f"api/{name}",
                    "name": name,
                    "context_length": 200000,
                    "supports_vision": True,
                }
            )
        
        # Claude 4 models
        for name in [
            "claude-opus-4-20250514",
            "claude-opus-4-0",
            "claude-opus-4-0-thinking",
            "claude-sonnet-4-20250514",
            "claude-sonnet-4-0",
            "claude-sonnet-4-0-thinking",
        ]:
            models.append(
                {
                    "id": f"api/{name}",
                    "name": name,
                    "context_length": 200000,
                    "supports_vision": True,
                }
            )

        # Claude 3.7 models
        for name in [
            "claude-3-7-sonnet-20250219",
            "claude-3-7-sonnet-latest",
            "claude-3-7-sonnet-latest-thinking",
        ]:
            models.append(
                {
                    "id": f"api/{name}",
                    "name": name,
                    "context_length": 200000,
                    "supports_vision": True,
                }
            )

        # Claude 3.5 models
        for name in [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620",
            "claude-3-5-sonnet-latest",
        ]:
            models.append(
                {
                    "id": f"api/{name}",
                    "name": name,
                    "context_length": 200000,
                    "supports_vision": True,
                }
            )

        return models

    def pipes(self) -> List[dict]:
        return self.get_anthropic_models()

    def process_content(self, content: Union[str, List[dict]]) -> List[dict]:
        if isinstance(content, str):
            return [{"type": "text", "text": content}]

        processed_content = []
        for item in content:
            if item["type"] == "text":
                processed_content.append({"type": "text", "text": item["text"]})
            elif item["type"] == "image_url":
                processed_content.append(self.process_image(item))
            elif item["type"] == "pdf_url":
                processed_content.append(self.process_pdf(item))
            elif item["type"] == "document":
                processed_content.append(self.process_document(item))
            elif item["type"] == "file_reference":
                file_ref = self.process_file_reference(item)
                if file_ref:
                    processed_content.append(file_ref)
            elif item["type"] == "tool_calls":
                processed_content.append(item)
            elif item["type"] == "tool_results":
                processed_content.append(item)
        return processed_content

    def process_image(self, image_data):
        if image_data["image_url"]["url"].startswith("data:image"):
            mime_type, base64_data = image_data["image_url"]["url"].split(",", 1)
            media_type = mime_type.split(":")[1].split(";")[0]

            if media_type not in self.SUPPORTED_IMAGE_TYPES:
                raise ValueError(f"Unsupported media type: {media_type}")

            # Check image size
            image_size = len(base64_data) * 3 / 4  # Approximate size of decoded base64
            if image_size > self.MAX_IMAGE_SIZE:
                raise ValueError(
                    f"Image size exceeds {self.MAX_IMAGE_SIZE/(1024*1024)}MB limit: {image_size/(1024*1024):.2f}MB"
                )

            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64_data,
                },
            }
        else:
            return {
                "type": "image",
                "source": {"type": "url", "url": image_data["image_url"]["url"]},
            }

    def process_pdf(self, pdf_data):
        if pdf_data["pdf_url"]["url"].startswith("data:application/pdf"):
            mime_type, base64_data = pdf_data["pdf_url"]["url"].split(",", 1)

            # Check PDF size
            pdf_size = len(base64_data) * 3 / 4  # Approximate size of decoded base64
            if pdf_size > self.MAX_PDF_SIZE:
                raise ValueError(
                    f"PDF size exceeds {self.MAX_PDF_SIZE/(1024*1024)}MB limit: {pdf_size/(1024*1024):.2f}MB"
                )

            document = {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": base64_data,
                },
            }

            if pdf_data.get("cache_control"):
                document["cache_control"] = pdf_data["cache_control"]

            return document
        else:
            document = {
                "type": "document",
                "source": {"type": "url", "url": pdf_data["pdf_url"]["url"]},
            }

            if pdf_data.get("cache_control"):
                document["cache_control"] = pdf_data["cache_control"]

            return document

    def process_document(self, doc_data):
        """Process documents for citations"""
        document = {
            "type": "document",
            "source": doc_data.get("source"),
        }

        # Add optional fields
        if doc_data.get("title"):
            document["title"] = doc_data["title"]

        if doc_data.get("context"):
            document["context"] = doc_data["context"]

        # Enable citations if specified
        if doc_data.get("citations", {}).get("enabled"):
            document["citations"] = {"enabled": True}

        # Add cache_control if specified
        if doc_data.get("cache_control"):
            document["cache_control"] = doc_data["cache_control"]

        return document

    def process_file_reference(self, file_data):
        """Process file references through Files API"""
        if file_data.get("file_id"):
            return {
                "type": "document",
                "source": {"type": "file", "file_id": file_data["file_id"]},
            }
        return None

    def convert_openai_tools_to_anthropic(self, tools: List[dict]) -> List[dict]:
        """Convert OpenAI format tools to Anthropic format"""
        anthropic_tools = []
        for tool in tools:
            if tool.get("type") == "function":
                function = tool.get("function", {})
                anthropic_tool = {
                    "name": function.get("name"),
                    "description": function.get("description"),
                    "input_schema": function.get("parameters", {}),
                }
                anthropic_tools.append(anthropic_tool)
        return anthropic_tools

    def validate_total_image_size(self, messages: List[dict]) -> None:
        """Validate total size of all images"""
        total_size = 0
        image_count = 0

        for message in messages:
            if isinstance(message.get("content"), list):
                for item in message["content"]:
                    if item.get("type") == "image_url" and item["image_url"][
                        "url"
                    ].startswith("data:image"):
                        _, base64_data = item["image_url"]["url"].split(",", 1)
                        image_size = len(base64_data) * 3 / 4
                        total_size += image_size
                        image_count += 1

        if total_size > self.TOTAL_MAX_IMAGE_SIZE:
            raise ValueError(
                f"Total image size exceeds {self.TOTAL_MAX_IMAGE_SIZE/(1024*1024)}MB limit: {total_size/(1024*1024):.2f}MB"
            )

        if image_count > self.MAX_IMAGES_PER_REQUEST:
            raise ValueError(
                f"Too many images: {image_count}. Maximum is {self.MAX_IMAGES_PER_REQUEST}."
            )

    async def pipe(self, body: Dict) -> Union[str, AsyncGenerator[str, None]]:
        if not self.valves.ANTHROPIC_API_KEY:
            return {"content": "Error: ANTHROPIC_API_KEY is required", "format": "text"}

        try:
            system_message, messages = pop_system_message(body["messages"])

            # Validate images
            self.validate_total_image_size(messages)

            # Determine if using thinking mode
            model_name = body["model"].split("/")[-1]
            is_thinking_mode = "-thinking" in body["model"]
            if is_thinking_mode:
                # Strip the "-thinking" suffix for API call
                model_name = model_name.replace("-thinking", "")

            max_tokens_limit = self.MODEL_MAX_TOKENS.get(model_name, 4096)

            payload = {
                "model": model_name,
                "messages": self._process_messages(messages),
                "max_tokens": min(
                    body.get("max_tokens", max_tokens_limit), max_tokens_limit
                ),
                "temperature": (
                    float(body.get("temperature"))
                    if body.get("temperature") is not None
                    else None
                ),
                "top_k": (
                    int(body.get("top_k")) if body.get("top_k") is not None else None
                ),
                "top_p": (
                    float(body.get("top_p")) if body.get("top_p") is not None else None
                ),
                "stream": body.get("stream", True),
                "metadata": body.get("metadata", {}),
            }

            payload = {k: v for k, v in payload.items() if v is not None}

            if system_message:
                payload["system"] = str(system_message)

            # Convert OpenAI tools to Anthropic format
            if "tools" in body:
                anthropic_tools = self.convert_openai_tools_to_anthropic(body["tools"])
                payload["tools"] = anthropic_tools
                
                # DEBUG: Log tools being passed to Claude
                logging.info(f"[TOOL DEBUG] Passing {len(anthropic_tools)} tools to Claude:")
                for t in anthropic_tools:
                    logging.info(f"  - {t.get('name')}")

                # Convert tool_choice
                tool_choice = body.get("tool_choice", "auto")
                if tool_choice == "none":
                    payload["tool_choice"] = {"type": "none"}
                elif tool_choice == "auto":
                    payload["tool_choice"] = {"type": "auto"}
                elif isinstance(tool_choice, dict) and tool_choice.get("function"):
                    payload["tool_choice"] = {
                        "type": "tool",
                        "name": tool_choice["function"]["name"],
                    }
                    
                logging.info(f"[TOOL DEBUG] tool_choice = {payload.get('tool_choice')}")
            else:
                logging.warning("[TOOL DEBUG] No tools in request body!")

            if "response_format" in body:
                payload["response_format"] = {
                    "type": body["response_format"].get("type")
                }

            # Add thinking parameters if using thinking mode
            if is_thinking_mode:
                payload["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": self.valves.THINKING_BUDGET_TOKENS,
                }

            headers = {
                "x-api-key": self.valves.ANTHROPIC_API_KEY,
                "anthropic-version": self.API_VERSION,
                "content-type": "application/json",
            }

            beta_headers = []

            # Add 128K output beta header for Claude 3.7+ and Claude 4.5
            if model_name in [
                "claude-3-7-sonnet-20250219", 
                "claude-3-7-sonnet-latest",
                # Claude 4.5 Opus (最新旗舰)
                "claude-opus-4-5-20250514",
                "claude-4-5-opus-20250514",
                # Claude 4 models
                "claude-opus-4-20250514",
                "claude-opus-4-0",
                "claude-sonnet-4-20250514",
                "claude-sonnet-4-0",
            ]:
                beta_headers.append(self.OUTPUT128K_HEADER)

            # Check for beta features in messages
            has_pdf = False
            has_cache = False
            has_1h_cache = False
            has_files = False

            for msg in body.get("messages", []):
                if isinstance(msg["content"], list):
                    for item in msg["content"]:
                        if item.get("type") == "pdf_url":
                            has_pdf = True
                        if item.get("cache_control"):
                            has_cache = True
                            if item.get("cache_control", {}).get("ttl") == "1h":
                                has_1h_cache = True
                        if item.get("type") == "file_reference":
                            has_files = True

            if has_pdf:
                beta_headers.append(self.PDF_HEADER)

            if has_cache:
                beta_headers.append(self.PROMPT_CACHE_HEADER)

            if has_1h_cache:
                beta_headers.append(self.EXTENDED_CACHE_HEADER)

            if has_files:
                beta_headers.append(self.FILES_API_HEADER)

            # Add interleaved thinking if requested
            if is_thinking_mode and body.get("interleaved_thinking", False):
                beta_headers.append(self.INTERLEAVED_THINKING_HEADER)

            if beta_headers:
                headers["anthropic-beta"] = ",".join(beta_headers)

            try:
                if payload["stream"]:
                    return self._stream_with_ui(self.MODEL_URL, headers, payload, body)

                response = await self._send_request(self.MODEL_URL, headers, payload)
                if response.status_code != 200:
                    return {
                        "content": f"Error: HTTP {response.status_code}: {response.text}",
                        "format": "text",
                    }

                result, cache_metrics = self._handle_response(response)
                response_text = result["content"][0]["text"]

                return response_text

            except aiohttp.ClientError as e:
                error_msg = f"Request failed: {str(e)}"
                if self.request_id:
                    error_msg += f" (Request ID: {self.request_id})"

                return {"content": error_msg, "format": "text"}

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if self.request_id:
                error_msg += f" (Request ID: {self.request_id})"

            return {"content": error_msg, "format": "text"}

    def _create_openai_tool_call_chunk(self, model: str, tool_calls: list = None, content: str = None, finish_reason: str = None) -> dict:
        """Create an OpenAI-compatible streaming chunk for tool calls"""
        import time
        chunk = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": finish_reason
            }]
        }
        
        if tool_calls:
            chunk["choices"][0]["delta"]["tool_calls"] = tool_calls
        if content:
            chunk["choices"][0]["delta"]["content"] = content
            
        return chunk

    async def _stream_with_ui(
        self, url: str, headers: dict, payload: dict, body: dict
    ) -> AsyncGenerator[str, None]:
        try:
            # Track tool_use blocks being built
            current_tool_use = None
            tool_use_input_json = ""
            tool_call_index = 0
            model_name = payload.get("model", "claude")
            has_tool_calls = False
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT),
                ) as response:
                    self.request_id = response.headers.get("x-request-id")
                    if response.status != 200:
                        error_msg = (
                            f"Error: HTTP {response.status}: {await response.text()}"
                        )
                        if self.request_id:
                            error_msg += f" (Request ID: {self.request_id})"
                        yield error_msg
                        return

                    async for line in response.content:
                        if line and line.startswith(b"data: "):
                            try:
                                data = json.loads(line[6:])

                                # Handle content_block_start - detect tool_use
                                if data["type"] == "content_block_start":
                                    content_block = data.get("content_block", {})
                                    logging.info(f"[STREAM DEBUG] content_block_start: type={content_block.get('type')}")
                                    
                                    if content_block.get("type") == "tool_use":
                                        has_tool_calls = True
                                        current_tool_use = {
                                            "id": content_block.get("id", f"call_{tool_call_index}"),
                                            "name": content_block.get("name", ""),
                                            "index": tool_call_index
                                        }
                                        tool_use_input_json = ""
                                        
                                        logging.info(f"[STREAM DEBUG] Claude wants to call tool: {current_tool_use['name']}")
                                        
                                        # Emit initial tool_call chunk with name
                                        initial_chunk = self._create_openai_tool_call_chunk(
                                            model_name,
                                            tool_calls=[{
                                                "index": tool_call_index,
                                                "id": current_tool_use["id"],
                                                "type": "function",
                                                "function": {
                                                    "name": current_tool_use["name"],
                                                    "arguments": ""
                                                }
                                            }]
                                        )
                                        yield f"data: {json.dumps(initial_chunk)}\n\n"

                                elif data["type"] == "content_block_delta":
                                    delta = data.get("delta", {})

                                    # Handle text_delta - yield as OpenAI format
                                    if delta.get("type") == "text_delta":
                                        text = delta.get("text", "")
                                        if text:
                                            chunk = self._create_openai_tool_call_chunk(model_name, content=text)
                                            yield f"data: {json.dumps(chunk)}\n\n"

                                    # Handle input_json_delta (for tool_use) - stream arguments
                                    elif delta.get("type") == "input_json_delta":
                                        partial_json = delta.get("partial_json", "")
                                        if partial_json and current_tool_use:
                                            tool_use_input_json += partial_json
                                            # Stream the arguments incrementally
                                            arg_chunk = self._create_openai_tool_call_chunk(
                                                model_name,
                                                tool_calls=[{
                                                    "index": current_tool_use["index"],
                                                    "function": {
                                                        "arguments": partial_json
                                                    }
                                                }]
                                            )
                                            yield f"data: {json.dumps(arg_chunk)}\n\n"

                                    # Handle thinking_delta (for thinking mode)
                                    elif delta.get("type") == "thinking_delta":
                                        thinking_text = delta.get("thinking", "")
                                        if thinking_text:
                                            # Emit as reasoning_content for Open WebUI
                                            chunk = {
                                                "id": f"chatcmpl-{int(__import__('time').time())}",
                                                "object": "chat.completion.chunk",
                                                "model": model_name,
                                                "choices": [{
                                                    "index": 0,
                                                    "delta": {"reasoning_content": thinking_text},
                                                    "finish_reason": None
                                                }]
                                            }
                                            yield f"data: {json.dumps(chunk)}\n\n"

                                    # Handle citations_delta
                                    elif delta.get("type") == "citations_delta":
                                        citation = delta.get("citation", {})
                                        if citation:
                                            doc_index = citation.get("document_index", 0)
                                            doc_title = citation.get("document_title", "")
                                            cite_text = f" [{doc_index}: {doc_title}]" if doc_title else f" [{doc_index}]"
                                            chunk = self._create_openai_tool_call_chunk(model_name, content=cite_text)
                                            yield f"data: {json.dumps(chunk)}\n\n"

                                # Handle content_block_stop
                                elif data["type"] == "content_block_stop":
                                    if current_tool_use:
                                        tool_call_index += 1
                                        current_tool_use = None
                                        tool_use_input_json = ""

                                elif data["type"] == "message_stop":
                                    # Send finish chunk
                                    finish_reason = "tool_calls" if has_tool_calls else "stop"
                                    finish_chunk = self._create_openai_tool_call_chunk(
                                        model_name, 
                                        finish_reason=finish_reason
                                    )
                                    yield f"data: {json.dumps(finish_chunk)}\n\n"
                                    yield "data: [DONE]\n\n"
                                    break
                                    
                            except json.JSONDecodeError as e:
                                logging.error(
                                    f"Failed to parse streaming response: {e}"
                                )
                                continue
                                
        except asyncio.TimeoutError:
            error_msg = "Request timed out"
            if self.request_id:
                error_msg += f" (Request ID: {self.request_id})"
            yield error_msg
        except Exception as e:
            error_msg = f"Stream error: {str(e)}"
            if self.request_id:
                error_msg += f" (Request ID: {self.request_id})"
            yield error_msg

    def _normalize_tool_result_content(self, content: Union[str, dict, list]) -> str:
        """
        规范化工具结果内容，确保换行符等特殊字符被正确处理
        
        目标：将工具返回的格式化文本（如 Markdown）正确提取，避免被当作 JSON 字符串显示
        
        处理情况：
        1. JSON 字符串（包含转义的 \n）-> 解析后返回原始文本
        2. 普通字符串（包含 \n 转义符）-> 转换为实际换行
        3. 字典或列表 -> JSON 序列化（格式化）
        4. 已经是格式化好的文本 -> 直接返回
        """
        # 如果不是字符串，先序列化
        if isinstance(content, (dict, list)):
            content = json.dumps(content, indent=2, ensure_ascii=False)
        elif not isinstance(content, str):
            content = str(content) if content else ""
        
        # 如果内容为空，直接返回
        if not content:
            return ""
        
        content_stripped = content.strip()
        
        # 情况1: JSON 字符串格式（以 " 开头和结尾）
        # 这是最常见的情况：工具返回的格式化文本被 JSON 序列化后传递
        if content_stripped.startswith('"') and content_stripped.endswith('"') and len(content_stripped) > 1:
            try:
                # 尝试解析为 JSON 字符串
                parsed = json.loads(content_stripped)
                if isinstance(parsed, str):
                    # 解析成功！返回解析后的字符串（JSON.loads 已自动处理所有转义字符）
                    # 这样 "\\n" 会变成 "\n"，前端就能正确显示了
                    return parsed
            except (json.JSONDecodeError, ValueError):
                # JSON 解析失败，可能是格式不完整的 JSON 字符串
                # 尝试手动提取内容
                if len(content_stripped) > 2:
                    inner = content_stripped[1:-1]  # 移除首尾引号
                    # 处理转义字符
                    inner = inner.replace('\\n', '\n')
                    inner = inner.replace('\\t', '\t')
                    inner = inner.replace('\\r', '\r')
                    inner = inner.replace('\\"', '"')
                    inner = inner.replace("\\'", "'")
                    # 检查是否包含 Markdown 标记（说明是格式化文本）
                    if any(marker in inner for marker in ['**', '##', '📊', '═', '📄', '💾']):
                        return inner
        
        # 情况2: 不是 JSON 字符串格式，但包含转义字符
        # 检查是否包含转义的换行符（工具返回的是字符串，但包含了 \n 转义序列）
        if '\\n' in content:
            # 替换转义字符为实际字符
            normalized = content.replace('\\n', '\n')
            normalized = normalized.replace('\\t', '\t')
            normalized = normalized.replace('\\r', '\r')
            normalized = normalized.replace('\\"', '"')
            normalized = normalized.replace("\\'", "'")
            # 如果包含 Markdown 标记，说明是格式化文本，直接返回
            if any(marker in normalized for marker in ['**', '##', '📊', '═', '📄', '💾']):
                return normalized
            return normalized
        
        # 情况3: 已经是格式化好的文本，直接返回
        return content
    
    def _process_messages(self, messages: List[dict]) -> List[dict]:
        """
        Process messages and convert OpenAI format to Anthropic format.
        
        Handles:
        - Regular text messages
        - OpenAI tool_calls in assistant messages -> Anthropic tool_use
        - OpenAI tool role messages -> Anthropic tool_result in user message
        """
        processed_messages = []
        pending_tool_results = []  # Collect tool results to batch into user message
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            # Handle tool role messages (OpenAI format) - collect for batching
            if role == "tool":
                tool_call_id = message.get("tool_call_id", "")
                # 规范化工具结果内容，确保换行符被正确处理
                tool_content_raw = content if isinstance(content, str) else json.dumps(content)
                tool_content = self._normalize_tool_result_content(tool_content_raw)
                
                pending_tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call_id,
                    "content": tool_content
                })
                continue
            
            # If we have pending tool results, emit them as a user message
            if pending_tool_results and role != "tool":
                processed_messages.append({
                    "role": "user",
                    "content": pending_tool_results
                })
                pending_tool_results = []
            
            # Handle assistant messages with tool_calls (OpenAI format)
            if role == "assistant":
                tool_calls = message.get("tool_calls", [])
                
                if tool_calls:
                    # Convert OpenAI tool_calls to Anthropic tool_use blocks
                    assistant_content = []
                    
                    # Add any text content first
                    if content:
                        if isinstance(content, str):
                            assistant_content.append({"type": "text", "text": content})
                        elif isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get("type") == "text":
                                    assistant_content.append(item)
                    
                    # Add tool_use blocks
                    for tc in tool_calls:
                        tool_use = {
                            "type": "tool_use",
                            "id": tc.get("id", ""),
                            "name": tc.get("function", {}).get("name", ""),
                            "input": {}
                        }
                        # Parse arguments
                        args = tc.get("function", {}).get("arguments", "{}")
                        try:
                            tool_use["input"] = json.loads(args) if isinstance(args, str) else args
                        except json.JSONDecodeError:
                            tool_use["input"] = {"raw": args}
                        
                        assistant_content.append(tool_use)
                    
                    processed_messages.append({
                        "role": "assistant",
                        "content": assistant_content
                    })
                    continue
            
            # Regular message processing
            processed_content = []
            if isinstance(content, str):
                if content:
                    processed_content.append({"type": "text", "text": content})
            elif isinstance(content, list):
                for item in self.process_content(content):
                    if (
                        role == "assistant"
                        and item.get("type") == "tool_calls"
                    ):
                        item["cache_control"] = {"type": "ephemeral"}
                    elif (
                        role == "user"
                        and item.get("type") == "tool_results"
                    ):
                        item["cache_control"] = {"type": "ephemeral"}
                    processed_content.append(item)
            
            if processed_content or role == "assistant":
                processed_messages.append({
                    "role": role,
                    "content": processed_content if processed_content else [{"type": "text", "text": ""}]
                })
        
        # Don't forget any remaining tool results
        if pending_tool_results:
            processed_messages.append({
                "role": "user",
                "content": pending_tool_results
            })
        
        return processed_messages

    async def _send_request(
        self, url: str, headers: dict, payload: dict
    ) -> SimpleNamespace:
        retry_count = 0
        base_delay = 1  # Start with 1 second delay
        max_retries = 3

        async with aiohttp.ClientSession() as session:
            while retry_count < max_retries:
                try:
                    async with session.post(
                        url,
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT),
                    ) as response:
                        self.request_id = response.headers.get("x-request-id")

                        if response.status == 429:
                            retry_after = int(
                                response.headers.get(
                                    "retry-after", base_delay * (2**retry_count)
                                )
                            )
                            logging.warning(
                                f"Rate limit hit. Retrying in {retry_after} seconds. Retry count: {retry_count + 1}"
                            )
                            await asyncio.sleep(retry_after)
                            retry_count += 1
                            continue

                        response_text = await response.text()

                        response_wrapper = SimpleNamespace(
                            status_code=response.status,
                            headers=response.headers,
                            text=response_text,
                            json=lambda: json.loads(response_text),
                        )
                        return response_wrapper

                except aiohttp.ClientError as e:
                    logging.error(f"Request failed: {str(e)}")
                    raise e

        logging.error("Max retries exceeded for rate limit.")
        return SimpleNamespace(
            status_code=429,
            headers={},
            text="Max retries exceeded",
            json=lambda: {"error": {"message": "Max retries exceeded"}},
        )

    def _handle_response(self, response):
        if response.status_code != 200:
            error_msg = f"Error: HTTP {response.status_code}"
            try:
                error_data = response.json().get("error", {})
                error_msg += f": {error_data.get('message', response.text)}"

                error_type = error_data.get("type")
                if error_type:
                    error_msg += f" (Type: {error_type})"
            except:
                error_msg += f": {response.text}"

            self.request_id = response.headers.get("x-request-id")
            if self.request_id:
                error_msg += f" (Request ID: {self.request_id})"

            return {"content": error_msg, "format": "text"}, None

        result = response.json()
        usage = result.get("usage", {})
        cache_metrics = {
            "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
            "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
        }
        return result, cache_metrics

