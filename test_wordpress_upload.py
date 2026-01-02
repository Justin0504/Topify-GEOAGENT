#!/usr/bin/env python3
"""
测试WordPress图片上传功能
"""

import os
import sys
import requests
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置信息（请修改为你的实际值）
# 优先从环境变量读取，如果没有则使用默认值
import os
WP_ACCESS_TOKEN = os.getenv("WP_ACCESS_TOKEN", "xLaFY6y9GCg)3dg1AWMCCaV!9oCw*HmmPxECjZW1EpxlPkn3BlhO*UOgplhfM2)R")  # 你的WordPress Access Token
WP_SITE_ID = os.getenv("WP_SITE_ID", "251193948")  # 你的WordPress Site ID
WP_API_BASE = os.getenv("WP_API_BASE", "https://public-api.wordpress.com/rest/v1.1")

# 测试图片路径（创建一个测试图片）
TEST_IMAGE_PATH = "/tmp/test_image.png"

def create_test_image():
    """创建一个简单的测试图片"""
    try:
        from PIL import Image, ImageDraw
        
        # 创建一个简单的测试图片
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        draw.text((100, 150), "Test Image", fill='black')
        img.save(TEST_IMAGE_PATH)
        print(f"✅ 测试图片已创建: {TEST_IMAGE_PATH}")
        return True
    except ImportError:
        print("❌ 需要安装PIL库: pip install Pillow")
        print("   或者手动创建一个测试图片文件")
        return False
    except Exception as e:
        print(f"❌ 创建测试图片失败: {e}")
        return False

def test_upload_image(image_path):
    """测试上传图片到WordPress"""
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return None
    
    if not WP_ACCESS_TOKEN or not WP_SITE_ID:
        print("❌ 请先配置 WP_ACCESS_TOKEN 和 WP_SITE_ID")
        return None
    
    # 构建API URL
    api_base = WP_API_BASE.rstrip('/')
    url = f"{api_base}/sites/{WP_SITE_ID}/media/new"
    
    print(f"\n📤 开始上传图片到WordPress...")
    print(f"   端点: {url}")
    print(f"   文件: {image_path}")
    print(f"   大小: {os.path.getsize(image_path)} bytes")
    
    # 检测文件MIME类型
    file_ext = os.path.splitext(image_path)[1].lower()
    mime_type_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    mime_type = mime_type_map.get(file_ext, 'image/png')
    filename = os.path.basename(image_path)
    
    try:
        with open(image_path, 'rb') as f:
            # 尝试不同的字段名
            test_configs = [
                {'field': 'file', 'description': '使用 file 字段'},
                {'field': 'media', 'description': '使用 media 字段'},
                {'field': 'media[]', 'description': '使用 media[] 字段'},
            ]
            
            for config in test_configs:
                print(f"\n🔄 测试配置: {config['description']}")
                f.seek(0)  # 重置文件指针
                
                files = {
                    config['field']: (filename, f, mime_type)
                }
                
                data = {
                    'attrs[alt]': 'Test image uploaded via API'
                }
                
                headers = {
                    "Authorization": f"Bearer {WP_ACCESS_TOKEN}",
                    "User-Agent": "OpenWebUI-Test/1.0"
                }
                
                try:
                    response = requests.post(
                        url, 
                        files=files, 
                        data=data, 
                        headers=headers, 
                        timeout=60, 
                        verify=False
                    )
                    
                    print(f"   状态码: {response.status_code}")
                    print(f"   响应头: {dict(response.headers)}")
                    
                    if response.status_code in [200, 201]:
                        try:
                            result = response.json()
                            print(f"   ✅ 上传成功!")
                            print(f"   响应类型: {type(result)}")
                            
                            # WordPress.com API 返回格式可能是：
                            # 1. 直接是数组: [{...}]
                            # 2. 包含 media 字段的对象: {"media": [{...}]}
                            # 3. 直接是对象: {...}
                            media_item = None
                            if isinstance(result, list) and len(result) > 0:
                                media_item = result[0]
                            elif isinstance(result, dict):
                                # 检查是否有嵌套的 media 字段
                                if 'media' in result and isinstance(result['media'], list) and len(result['media']) > 0:
                                    media_item = result['media'][0]
                                else:
                                    media_item = result
                            else:
                                print(f"   ⚠️ 意外的响应格式: {type(result)}")
                                continue
                            
                            print(f"   响应键: {list(media_item.keys())}")
                            
                            # 尝试提取URL
                            image_url = (
                                media_item.get('URL') or 
                                media_item.get('url') or 
                                media_item.get('source_url') or
                                media_item.get('source') or 
                                media_item.get('file') or
                                media_item.get('link') or 
                                media_item.get('href')
                            )
                            
                            if image_url:
                                print(f"   ✅ 图片URL: {image_url}")
                                print(f"\n🎉 成功! 使用配置: {config['description']}")
                                print(f"   字段名: {config['field']}")
                                return image_url
                            else:
                                print(f"   ⚠️ 未找到URL字段")
                                print(f"   完整响应: {result}")
                        except Exception as json_error:
                            print(f"   ❌ JSON解析错误: {json_error}")
                            print(f"   响应文本: {response.text[:500]}")
                    else:
                        error_msg = response.text
                        try:
                            error_json = response.json()
                            error_msg = error_json.get("message", error_json.get("error", error_msg))
                        except:
                            pass
                        print(f"   ❌ 上传失败: {error_msg[:200]}")
                        
                except Exception as e:
                    print(f"   ❌ 请求异常: {e}")
                    continue
        
        print(f"\n❌ 所有配置都失败了")
        return None
        
    except Exception as e:
        print(f"❌ 上传过程出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    global WP_ACCESS_TOKEN, WP_SITE_ID
    
    print("=" * 60)
    print("WordPress 图片上传测试")
    print("=" * 60)
    
    # 检查配置
    if not WP_ACCESS_TOKEN:
        print("\n⚠️  请在脚本中设置 WP_ACCESS_TOKEN")
    if not WP_SITE_ID:
        print("⚠️  请在脚本中设置 WP_SITE_ID")
    
    if not WP_ACCESS_TOKEN or not WP_SITE_ID:
        print("\n❌ 请配置 WordPress 凭证")
        print("\n方法 1: 使用环境变量")
        print("   export WP_ACCESS_TOKEN='your_token'")
        print("   export WP_SITE_ID='your_site_id'")
        print("\n方法 2: 编辑此脚本，直接填入凭证")
        print("   或修改脚本中的 WP_ACCESS_TOKEN 和 WP_SITE_ID 变量")
        print("\n方法 3: 尝试从工具配置中读取...")
        
        # 尝试从工具配置中读取
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, script_dir)
            from tools.article_writer_tool import Tools
            tool = Tools()
            if tool.valves.WP_ACCESS_TOKEN.strip() and tool.valves.WP_SITE_ID.strip():
                print("✅ 从工具配置中读取到凭证")
                WP_ACCESS_TOKEN = tool.valves.WP_ACCESS_TOKEN.strip()
                WP_SITE_ID = tool.valves.WP_SITE_ID.strip()
            else:
                print("❌ 工具配置中也没有凭证，但脚本中已有默认值")
        except Exception as e:
            print(f"⚠️  无法从工具配置读取: {e}")
            print("   使用脚本中的默认值")
    
    # 创建测试图片
    if not os.path.exists(TEST_IMAGE_PATH):
        if not create_test_image():
            print("\n请手动创建一个测试图片，或安装Pillow库")
            return
    
    # 测试上传
    image_url = test_upload_image(TEST_IMAGE_PATH)
    
    if image_url:
        print("\n" + "=" * 60)
        print("✅ 测试成功!")
        print(f"图片URL: {image_url}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 测试失败")
        print("请检查:")
        print("1. WP_ACCESS_TOKEN 是否正确")
        print("2. WP_SITE_ID 是否正确")
        print("3. 网络连接是否正常")
        print("4. WordPress API端点是否正确")
        print("=" * 60)

if __name__ == "__main__":
    main()


