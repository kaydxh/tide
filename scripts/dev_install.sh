#!/bin/bash
# 开发环境安装脚本 - 使用本地 peek 库
# Usage: ./scripts/dev_install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIDE_ROOT="$(dirname "$SCRIPT_DIR")"
PEEK_ROOT="${TIDE_ROOT}/../peek"

echo "=== Tide 开发环境安装 ==="
echo "Tide 路径: $TIDE_ROOT"
echo "Peek 路径: $PEEK_ROOT"
echo ""

# 检查 peek 是否存在
if [ ! -d "$PEEK_ROOT" ]; then
    echo "错误: peek 库不存在于 $PEEK_ROOT"
    echo "请先克隆 peek 库到同级目录"
    exit 1
fi

# 创建虚拟环境（可选）
if [ ! -d "$TIDE_ROOT/.venv" ]; then
    echo ">>> 创建虚拟环境..."
    python3 -m venv "$TIDE_ROOT/.venv"
fi

# 激活虚拟环境
echo ">>> 激活虚拟环境..."
source "$TIDE_ROOT/.venv/bin/activate"

# 升级 pip
echo ">>> 升级 pip..."
pip install --upgrade pip

# 安装本地 peek（editable 模式）
echo ">>> 安装本地 peek 库（editable 模式）..."
pip install -e "$PEEK_ROOT"

# 安装本地 tide（editable 模式）
echo ">>> 安装本地 tide 库（editable 模式）..."
pip install -e "$TIDE_ROOT[all]"

echo ""
echo "=== 安装完成 ==="
echo ""
echo "已安装的包:"
pip list | grep -E "peek|tide"
echo ""
echo "激活虚拟环境: source $TIDE_ROOT/.venv/bin/activate"
echo "运行示例服务: python cmd/tide-date/main.py --config conf/tide-date.yaml"
