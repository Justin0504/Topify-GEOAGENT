#!/usr/bin/env python3
"""
Open WebUI 模型和工具导入示例脚本
使用方法: python import_examples.py --help
"""

import argparse
import json
import requests
import sys
from pathlib import Path


class OpenWebUIImporter:
    def __init__(self, api_base: str, token: str):
        self.api_base = api_base.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def import_models(self, models_data: list) -> bool:
        """导入模型列表"""
        url = f"{self.api_base}/api/v1/models/import"
        payload = {"models": models_data}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            print(f"✅ 成功导入 {len(models_data)} 个模型")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ 导入模型失败: {e}")
            if hasattr(e.response, 'text'):
                print(f"   错误详情: {e.response.text}")
            return False
    
    def import_tools(self, tools_data: list) -> bool:
        """导入工具列表"""
        success_count = 0
        for tool in tools_data:
            url = f"{self.api_base}/api/v1/tools/create"
            try:
                response = requests.post(url, json=tool, headers=self.headers)
                response.raise_for_status()
                print(f"✅ 成功导入工具: {tool.get('name', tool.get('id'))}")
                success_count += 1
            except requests.exceptions.RequestException as e:
                print(f"❌ 导入工具失败 ({tool.get('id')}): {e}")
                if hasattr(e.response, 'text'):
                    print(f"   错误详情: {e.response.text}")
        
        print(f"\n📊 导入结果: {success_count}/{len(tools_data)} 个工具成功")
        return success_count == len(tools_data)
    
    def export_models(self, output_file: str):
        """导出所有模型"""
        url = f"{self.api_base}/api/v1/models"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            models = response.json()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(models, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 成功导出 {len(models)} 个模型到 {output_file}")
        except requests.exceptions.RequestException as e:
            print(f"❌ 导出模型失败: {e}")
    
    def export_tools(self, output_file: str):
        """导出所有工具"""
        url = f"{self.api_base}/api/v1/tools"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            tools = response.json()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tools, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 成功导出 {len(tools)} 个工具到 {output_file}")
        except requests.exceptions.RequestException as e:
            print(f"❌ 导出工具失败: {e}")


def load_json_file(file_path: str) -> dict:
    """加载 JSON 文件"""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式错误: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Open WebUI 模型和工具导入工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 导入模型
  python import_examples.py import-models --file models.json --api http://localhost:8080 --token YOUR_TOKEN
  
  # 导入工具
  python import_examples.py import-tools --file tools.json --api http://localhost:8080 --token YOUR_TOKEN
  
  # 导出模型
  python import_examples.py export-models --output models_backup.json --api http://localhost:8080 --token YOUR_TOKEN
  
  # 导出工具
  python import_examples.py export-tools --output tools_backup.json --api http://localhost:8080 --token YOUR_TOKEN
        """
    )
    
    parser.add_argument('--api', default='http://localhost:8080', help='API 基础 URL')
    parser.add_argument('--token', required=True, help='认证 Token')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 导入模型
    import_models_parser = subparsers.add_parser('import-models', help='导入模型')
    import_models_parser.add_argument('--file', required=True, help='模型 JSON 文件路径')
    
    # 导入工具
    import_tools_parser = subparsers.add_parser('import-tools', help='导入工具')
    import_tools_parser.add_argument('--file', required=True, help='工具 JSON 文件路径')
    
    # 导出模型
    export_models_parser = subparsers.add_parser('export-models', help='导出模型')
    export_models_parser.add_argument('--output', required=True, help='输出文件路径')
    
    # 导出工具
    export_tools_parser = subparsers.add_parser('export-tools', help='导出工具')
    export_tools_parser.add_argument('--output', required=True, help='输出文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    importer = OpenWebUIImporter(args.api, args.token)
    
    if args.command == 'import-models':
        data = load_json_file(args.file)
        if isinstance(data, list):
            importer.import_models(data)
        elif isinstance(data, dict) and 'models' in data:
            importer.import_models(data['models'])
        else:
            print("❌ JSON 格式错误: 应该是模型数组或包含 'models' 键的对象")
            sys.exit(1)
    
    elif args.command == 'import-tools':
        data = load_json_file(args.file)
        if isinstance(data, list):
            importer.import_tools(data)
        else:
            print("❌ JSON 格式错误: 应该是工具数组")
            sys.exit(1)
    
    elif args.command == 'export-models':
        importer.export_models(args.output)
    
    elif args.command == 'export-tools':
        importer.export_tools(args.output)


if __name__ == '__main__':
    main()


