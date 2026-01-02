#!/bin/bash

# Logo 替换脚本
# 使用方法: ./replace_logo.sh <logo图片路径>

LOGO_FILE=$1

if [ -z "$LOGO_FILE" ]; then
    echo "❌ 错误: 请提供 Logo 图片路径"
    echo ""
    echo "使用方法:"
    echo "  ./replace_logo.sh <logo图片路径>"
    echo ""
    echo "例如:"
    echo "  ./replace_logo.sh ~/Downloads/geo-logo.png"
    echo ""
    exit 1
fi

if [ ! -f "$LOGO_FILE" ]; then
    echo "❌ 错误: 文件不存在: $LOGO_FILE"
    exit 1
fi

echo "🔄 正在替换 Logo..."
echo "   源文件: $LOGO_FILE"
echo ""

# 检查文件类型
FILE_EXT="${LOGO_FILE##*.}"
if [[ ! "$FILE_EXT" =~ ^(png|jpg|jpeg|svg)$ ]]; then
    echo "⚠️  警告: 建议使用 PNG 格式（支持透明背景）"
fi

# 目标文件位置
TARGETS=(
    "backend/open_webui/static/favicon.png"
    "build/static/favicon.png"
)

# 如果使用非 PNG 文件，需要先转换为 PNG
if [ "$FILE_EXT" != "png" ]; then
    echo "📝 检测到非 PNG 文件，需要转换..."
    CONVERTED_FILE="/tmp/logo_converted.png"
    
    # 检查是否有 ImageMagick 或 sips (macOS)
    if command -v convert &> /dev/null; then
        convert "$LOGO_FILE" -resize 512x512 "$CONVERTED_FILE"
        echo "✅ 使用 ImageMagick 转换为 PNG"
        LOGO_FILE="$CONVERTED_FILE"
    elif command -v sips &> /dev/null; then
        sips -s format png "$LOGO_FILE" --out "$CONVERTED_FILE" &> /dev/null
        sips -Z 512 "$CONVERTED_FILE" &> /dev/null
        echo "✅ 使用 sips 转换为 PNG"
        LOGO_FILE="$CONVERTED_FILE"
    else
        echo "⚠️  警告: 未找到图片转换工具"
        echo "   请手动将图片转换为 PNG 格式，或安装 ImageMagick"
        echo "   macOS: brew install imagemagick"
    fi
fi

# 备份原文件并复制新 Logo
for target in "${TARGETS[@]}"; do
    if [ -f "$target" ]; then
        # 备份原文件
        BACKUP="${target}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$target" "$BACKUP"
        echo "✅ 已备份原文件: $BACKUP"
    fi
    
    # 创建目录（如果不存在）
    mkdir -p "$(dirname "$target")"
    
    # 复制新 Logo
    cp "$LOGO_FILE" "$target"
    
    if [ -f "$target" ]; then
        echo "✅ 已替换: $target"
    else
        echo "❌ 替换失败: $target"
    fi
done

echo ""
echo "🎉 Logo 替换完成！"
echo ""
echo "📝 下一步:"
echo "   1. 如果后端正在运行，请重启后端以生效"
echo "   2. 清除浏览器缓存（Ctrl+Shift+R 或 Cmd+Shift+R）"
echo "   3. 如果前端是开发模式，可能需要刷新页面"
echo ""

