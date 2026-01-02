#!/bin/bash
# PDF 下载快捷脚本

echo "============================================"
echo "📥 PDF 文件下载工具"
echo "============================================"
echo ""
echo "请复制 Open WebUI 中 'file_data:' 后面的 Base64 数据"
echo "然后粘贴到这里，粘贴完成后按 Enter，然后按 Ctrl+D 结束输入："
echo ""

# 读取多行输入
BASE64_DATA=$(cat)

# 清理数据（去除空格和换行）
CLEANED_DATA=$(echo "$BASE64_DATA" | tr -d '\n\r ' )

if [ -z "$CLEANED_DATA" ]; then
    echo "❌ 错误: 没有输入数据"
    exit 1
fi

echo ""
echo "🔄 正在解码 Base64 数据..."

# 解码并保存
echo "$CLEANED_DATA" | base64 -D > 测试.pdf

if [ $? -eq 0 ]; then
    echo "✅ 文件已成功保存: 测试.pdf"
    echo "📁 文件位置: $(pwd)/测试.pdf"
    echo "📊 文件大小: $(ls -lh 测试.pdf | awk '{print $5}')"
    echo ""
    echo "🚀 正在打开文件..."
    open 测试.pdf
else
    echo "❌ 解码失败，请检查 Base64 数据是否完整"
    exit 1
fi


