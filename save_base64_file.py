#!/usr/bin/env python3
"""
Base64 文件保存工具
用于保存从 Open WebUI Report Factory Tool 生成的文件

使用方法:
1. 从 Open WebUI 复制 file_data 的值
2. 粘贴到下面的 BASE64_DATA 变量中
3. 设置输出文件名
4. 运行: python save_base64_file.py
"""

import base64
import sys
import os

# ============================================
# 配置区域 - 在这里粘贴你的数据
# ============================================

# 从 Open WebUI 复制的 Base64 数据（粘贴在三引号之间）
BASE64_DATA = """
粘贴你的 Base64 数据到这里
"""

# 输出文件名（根据实际格式修改扩展名）
OUTPUT_FILENAME = "report.pdf"  # 或 .docx, .xlsx

# ============================================
# 主程序（不需要修改）
# ============================================

def save_file():
    """解码 Base64 并保存为文件"""
    
    # 清理输入数据
    print("🔄 正在处理 Base64 数据...")
    data = BASE64_DATA.strip().replace('\n', '').replace(' ', '').replace('\r', '')
    
    # 检查数据是否有效
    if not data or data == "粘贴你的 Base64 数据到这里":
        print("❌ 错误: 请先在脚本中粘贴 Base64 数据")
        print("提示: 编辑此文件，在 BASE64_DATA 变量中粘贴数据")
        sys.exit(1)
    
    if len(data) < 100:
        print(f"⚠️  警告: Base64 数据太短 ({len(data)} 字符)，可能不完整")
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # 解码
    try:
        print(f"📦 Base64 数据长度: {len(data)} 字符")
        decoded = base64.b64decode(data)
        print(f"📦 解码后大小: {len(decoded)} bytes ({len(decoded)/1024:.2f} KB)")
    except Exception as e:
        print(f"❌ Base64 解码失败: {e}")
        print("提示: 请确保复制了完整的 Base64 字符串")
        sys.exit(1)
    
    # 保存文件
    try:
        with open(OUTPUT_FILENAME, "wb") as f:
            f.write(decoded)
        
        abs_path = os.path.abspath(OUTPUT_FILENAME)
        print(f"\n✅ 文件已成功保存！")
        print(f"📁 文件位置: {abs_path}")
        print(f"📊 文件大小: {len(decoded)} bytes ({len(decoded)/1024:.2f} KB)")
        
        # 自动打开文件（macOS）
        try:
            os.system(f'open "{OUTPUT_FILENAME}"')
            print(f"🚀 已自动打开文件")
        except:
            print(f"💡 提示: 可以手动打开文件: open {OUTPUT_FILENAME}")
            
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        sys.exit(1)

def main():
    print("=" * 60)
    print("Base64 文件保存工具")
    print("=" * 60)
    print()
    
    save_file()
    
    print()
    print("=" * 60)
    print("✅ 完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()

