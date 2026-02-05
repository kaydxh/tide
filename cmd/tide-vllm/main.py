#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2024 The kaydxh Authors.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Tide VLLM Service - vLLM 模板示例服务
该服务演示如何使用 vLLM 启动模型并发送请求
使用千问3（Qwen3）模型作为示例
"""

import asyncio
import signal
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))  # 添加项目根目录（包含 pkg, web）
sys.path.insert(0, str(project_root / "src"))  # 添加 src 目录（包含 tide 框架）

from app.server import new_command


def main():
    """Main entry point."""
    # 设置信号处理
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # 处理关闭信号
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(shutdown(s, loop))
        )

    try:
        command = new_command()
        command()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"启动服务失败, err: {e}", file=sys.stderr)
        sys.exit(1)


async def shutdown(sig, loop):
    """清理与服务关闭相关的任务。"""
    print(f"接收到退出信号 {sig.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


if __name__ == "__main__":
    main()
