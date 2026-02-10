#!/bin/bash

# 五倍返回测试脚本
# 用于本地测试多账号回关功能

echo "🎯 五倍返回测试脚本"
echo "================================"
echo ""

# 检查主账号 Cookie
if [ -z "$JUEJIN_COOKIES" ]; then
    echo "❌ 错误：未设置 JUEJIN_COOKIES 环境变量"
    echo ""
    echo "使用方法："
    echo "  export JUEJIN_COOKIES='你的主账号Cookie'"
    echo "  export JUEJIN_COOKIES_ACCOUNT2='小号1的Cookie'  # 可选"
    echo "  export JUEJIN_COOKIES_ACCOUNT3='小号2的Cookie'  # 可选"
    echo "  export JUEJIN_COOKIES_ACCOUNT4='小号3的Cookie'  # 可选"
    echo "  export JUEJIN_COOKIES_ACCOUNT5='小号4的Cookie'  # 可选"
    echo "  ./test_multi_account.sh"
    exit 1
fi

# 统计配置的账号数量
ACCOUNT_COUNT=1

if [ ! -z "$JUEJIN_COOKIES_ACCOUNT2" ]; then
    ACCOUNT_COUNT=$((ACCOUNT_COUNT + 1))
fi

if [ ! -z "$JUEJIN_COOKIES_ACCOUNT3" ]; then
    ACCOUNT_COUNT=$((ACCOUNT_COUNT + 1))
fi

if [ ! -z "$JUEJIN_COOKIES_ACCOUNT4" ]; then
    ACCOUNT_COUNT=$((ACCOUNT_COUNT + 1))
fi

if [ ! -z "$JUEJIN_COOKIES_ACCOUNT5" ]; then
    ACCOUNT_COUNT=$((ACCOUNT_COUNT + 1))
fi

echo "✅ 已配置 $ACCOUNT_COUNT 个账号"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 python3"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少 requests 库，正在安装..."
    pip3 install requests
fi

echo ""
echo "🚀 开始执行回关脚本..."
echo "================================"
echo ""

# 执行脚本
python3 scripts/follow_back.py

echo ""
echo "================================"
echo "✅ 测试完成！"
