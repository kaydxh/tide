#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tide CLI

提供命令行工具支持
"""

import os
import shutil
from pathlib import Path
from typing import Optional

import click


@click.group()
@click.version_option(version="0.1.0", prog_name="tide")
def main():
    """Tide - Python Web/gRPC Service Framework CLI"""
    pass


@main.command()
@click.argument("name")
@click.option("--template", "-t", default="basic", help="项目模板 (basic/full)")
def new(name: str, template: str):
    """
    创建新项目

    NAME: 项目名称
    """
    project_dir = Path(name)

    if project_dir.exists():
        click.echo(f"Error: Directory '{name}' already exists", err=True)
        return

    # 创建目录结构
    dirs = [
        "api",
        "cmd/{name}/app/plugins",
        "pkg/{name}/application",
        "pkg/{name}/domain",
        "pkg/{name}/infrastructure",
        "pkg/{name}/provider",
        "web",
        "conf",
        "tests",
        "scripts",
    ]

    for d in dirs:
        dir_path = project_dir / d.format(name=name.replace("-", "_"))
        dir_path.mkdir(parents=True, exist_ok=True)
        # 创建 __init__.py
        if "pkg" in d or "cmd" in d or "web" in d:
            (dir_path / "__init__.py").write_text('"""Module"""\n')

    # 创建基础文件
    _create_pyproject(project_dir, name)
    _create_readme(project_dir, name)
    _create_config(project_dir, name)
    _create_main(project_dir, name)
    _create_makefile(project_dir, name)
    _create_gitignore(project_dir)

    click.echo(f"✅ Project '{name}' created successfully!")
    click.echo(f"\nNext steps:")
    click.echo(f"  cd {name}")
    click.echo(f"  pip install -e .")
    click.echo(f"  python cmd/{name.replace('-', '_')}/main.py serve")


def _create_pyproject(project_dir: Path, name: str):
    """创建 pyproject.toml"""
    content = f'''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = "{name} - Built with Tide Framework"
requires-python = ">=3.9"
dependencies = [
    "tide>=0.1.0",
    "peek>=0.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
]

[tool.setuptools]
package-dir = {{"" = "."}}

[tool.setuptools.packages.find]
where = ["."]
'''
    (project_dir / "pyproject.toml").write_text(content)


def _create_readme(project_dir: Path, name: str):
    """创建 README.md"""
    content = f'''# {name}

Built with [Tide](https://github.com/kaydxh/tide) Framework.

## Quick Start

```bash
# Install dependencies
pip install -e .

# Run server
python cmd/{name.replace("-", "_")}/main.py serve --config conf/config.yaml
```

## Project Structure

```
{name}/
├── api/                    # Proto/API definitions
├── cmd/{name.replace("-", "_")}/            # Application entry
├── pkg/{name.replace("-", "_")}/            # Business logic (DDD)
│   ├── application/        # Application layer
│   ├── domain/             # Domain layer
│   └── infrastructure/     # Infrastructure layer
├── web/                    # Web controllers
├── conf/                   # Configuration files
└── tests/                  # Tests
```
'''
    (project_dir / "README.md").write_text(content)


def _create_config(project_dir: Path, name: str):
    """创建配置文件"""
    content = f'''# {name} Configuration

name: {name}
version: 0.1.0

log:
  level: info
  format: text

web:
  bind_address:
    host: "0.0.0.0"
    port: 8080
  grpc:
    enabled: true
    port: 50051
  http:
    enabled: true

database:
  mysql:
    enabled: false
  redis:
    enabled: false

open_telemetry:
  enabled: false
'''
    (project_dir / "conf" / "config.yaml").write_text(content)


def _create_main(project_dir: Path, name: str):
    """创建主入口文件"""
    module_name = name.replace("-", "_")
    content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
{name} - Main Entry
"""

from tide import TideApp
from tide.plugins import LogPlugin, OpenTelemetryPlugin


def main():
    app = TideApp(
        name="{name}",
        version="0.1.0",
        description="{name} Service",
    )

    # Register plugins
    app.register_plugin(LogPlugin())
    app.register_plugin(OpenTelemetryPlugin())

    # Run CLI
    app.cli()


if __name__ == "__main__":
    main()
'''
    main_dir = project_dir / "cmd" / module_name
    main_dir.mkdir(parents=True, exist_ok=True)
    (main_dir / "main.py").write_text(content)
    (main_dir / "__init__.py").write_text('"""Main module"""\n')


def _create_makefile(project_dir: Path, name: str):
    """创建 Makefile"""
    module_name = name.replace("-", "_")
    content = f'''.PHONY: all build run test clean install

all: build

build:
\t@echo "Building {name}..."
\tpip install -e .

run:
\t@echo "Running {name}..."
\tpython cmd/{module_name}/main.py serve --config conf/config.yaml

test:
\t@echo "Running tests..."
\tpytest tests/ -v

lint:
\t@echo "Linting..."
\tflake8 .
\tmypy .

clean:
\t@echo "Cleaning..."
\trm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/
\tfind . -type d -name "__pycache__" -exec rm -rf {{}} + 2>/dev/null || true

install:
\tpip install -e ".[dev]"

help:
\t@echo "Available targets:"
\t@echo "  make build   - Build the project"
\t@echo "  make run     - Run the server"
\t@echo "  make test    - Run tests"
\t@echo "  make lint    - Run linters"
\t@echo "  make clean   - Clean build artifacts"
\t@echo "  make install - Install with dev dependencies"
'''
    (project_dir / "Makefile").write_text(content)


def _create_gitignore(project_dir: Path):
    """创建 .gitignore"""
    content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
log/

# OS
.DS_Store
Thumbs.db
'''
    (project_dir / ".gitignore").write_text(content)


@main.command()
def init():
    """
    在当前目录初始化 Tide 项目
    """
    name = Path.cwd().name
    click.echo(f"Initializing Tide project: {name}")

    # 创建基础结构
    dirs = ["conf", "tests"]
    for d in dirs:
        Path(d).mkdir(exist_ok=True)

    _create_config(Path("."), name)
    _create_gitignore(Path("."))

    click.echo(f"✅ Tide project initialized in current directory")


@main.command()
def info():
    """显示 Tide 框架信息"""
    click.echo("Tide - Python Web/gRPC Service Framework")
    click.echo("Version: 0.1.0")
    click.echo("Based on: Peek (Python Base Library)")
    click.echo("Inspired by: Sea (Go Version)")
    click.echo("\nFeatures:")
    click.echo("  - HTTP/gRPC dual protocol support")
    click.echo("  - DDD (Domain-Driven Design) architecture")
    click.echo("  - Plugin-based component loading")
    click.echo("  - YAML configuration management")
    click.echo("  - OpenTelemetry observability")


if __name__ == "__main__":
    main()
