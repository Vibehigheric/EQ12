#!/usr/bin/env bash
set -euo pipefail

# EQ12 Automated Code Quality & Formatting Script
# This script runs multiple code quality tools in sequence for comprehensive fixes

echo "🚀 EQ12 Code Quality Automation Starting..."

# Install if missing (assumes pip + python)
echo "📦 Installing/updating required packages..."
pip install ruff black autoflake autopep8 isort flake8

echo "🔧 Running ruff fixes..."
ruff check --fix .

echo "🎨 Running black formatter..."
black .

echo "📋 Running isort (sort imports)..."
isort .

echo "🧹 Running autoflake to remove unused imports/vars (run carefully)..."
autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r .

echo "⚡ Running autopep8 aggressive pass..."
autopep8 --in-place --aggressive --aggressive -r .

echo "📊 Final quality check with flake8..."
python -m flake8 scripts/ tests/ --statistics --max-line-length=100 || echo "⚠️ Some issues remain - see output above"

echo "✅ Done. Run: git add -A && git commit -m 'style: autoformat + autofix' (inspect diff first)."
echo "🎯 EQ12 Code Quality Automation Complete!"