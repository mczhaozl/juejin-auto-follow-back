#!/bin/bash

# 测试签到脚本
# 使用方法: ./test_checkin.sh

echo "🧪 测试掘金签到脚本"
echo "================================"

# 检查环境变量
echo ""
echo "📋 检查环境变量:"
if [ -n "$JUEJIN_COOKIES" ]; then
    echo "✅ JUEJIN_COOKIES (主账号) 已设置"
else
    echo "❌ JUEJIN_COOKIES (主账号) 未设置"
fi

if [ -n "$JUEJIN_COOKIES_ACCOUNT2" ]; then
    echo "✅ JUEJIN_COOKIES_ACCOUNT2 (小号1) 已设置"
else
    echo "⚠️  JUEJIN_COOKIES_ACCOUNT2 (小号1) 未设置"
fi

if [ -n "$JUEJIN_COOKIES_ACCOUNT3" ]; then
    echo "✅ JUEJIN_COOKIES_ACCOUNT3 (小号2) 已设置"
else
    echo "⚠️  JUEJIN_COOKIES_ACCOUNT3 (小号2) 未设置"
fi

if [ -n "$JUEJIN_COOKIES_ACCOUNT4" ]; then
    echo "✅ JUEJIN_COOKIES_ACCOUNT4 (小号3) 已设置"
else
    echo "⚠️  JUEJIN_COOKIES_ACCOUNT4 (小号3) 未设置"
fi

if [ -n "$JUEJIN_COOKIES_ACCOUNT5" ]; then
    echo "✅ JUEJIN_COOKIES_ACCOUNT5 (小号4) 已设置"
else
    echo "⚠️  JUEJIN_COOKIES_ACCOUNT5 (小号4) 未设置"
fi

echo ""
echo "================================"
echo "🚀 开始执行签到脚本"
echo "================================"
echo ""

python3 scripts/daily_checkin.py
