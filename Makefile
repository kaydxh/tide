# Tide Framework Makefile
# 参考 Go 版本 sea 的 Makefile

.PHONY: all build install test lint clean docs example help

# 默认目标
all: build

# 构建项目
build:
	@echo "Building Tide..."
	pip install -e .

# 安装完整依赖
install:
	@echo "Installing Tide with all dependencies..."
	pip install -e ".[all]"

# 安装开发依赖
install-dev:
	@echo "Installing development dependencies..."
	pip install -e ".[dev]"

# 运行测试
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src/tide --cov-report=html

# 代码检查
lint:
	@echo "Running linters..."
	flake8 src/tide/
	mypy src/tide/
	black --check src/tide/
	isort --check-only src/tide/

# 格式化代码
format:
	@echo "Formatting code..."
	black src/tide/
	isort src/tide/

# 清理
clean:
	@echo "Cleaning..."
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 生成文档
docs:
	@echo "Generating documentation..."
	cd docs && make html

# 运行示例
example:
	@echo "Running tide-date example..."
	cd examples/tide-date && python main.py serve --config config.yaml

# 创建新项目
new:
	@if [ -z "$(TARGET)" ]; then \
		echo "Usage: make new TARGET=project-name"; \
		exit 1; \
	fi
	tide new $(TARGET)

# 发布到 PyPI
publish:
	@echo "Publishing to PyPI..."
	python -m build
	twine upload dist/*

# 发布到 TestPyPI
publish-test:
	@echo "Publishing to TestPyPI..."
	python -m build
	twine upload --repository testpypi dist/*

# 版本信息
version:
	@python -c "import tide; print(tide.__version__)"

# 帮助信息
help:
	@echo "Tide Framework - Makefile Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  all          - Build the project (default)"
	@echo "  build        - Build and install in development mode"
	@echo "  install      - Install with all dependencies"
	@echo "  install-dev  - Install with development dependencies"
	@echo "  test         - Run tests with coverage"
	@echo "  lint         - Run code linters"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean build artifacts"
	@echo "  docs         - Generate documentation"
	@echo "  example      - Run tide-date example"
	@echo "  new          - Create new project (TARGET=name)"
	@echo "  publish      - Publish to PyPI"
	@echo "  publish-test - Publish to TestPyPI"
	@echo "  version      - Show version"
	@echo "  help         - Show this help"
