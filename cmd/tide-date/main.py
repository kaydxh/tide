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
"""

import asyncio
import signal
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))  # 添加项目根目录（包含 pkg, web）
sys.path.insert(0, str(project_root / "src"))  # 添加 src 目录（包含 tide 框架）

from app.server import new_command


def main():
    """Main entry point."""
    # Setup signal handling
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Handle shutdown signals
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
        print(f"failed to run server, err: {e}", file=sys.stderr)
        sys.exit(1)


async def shutdown(sig, loop):
    """Cleanup tasks tied to the service's shutdown."""
    print(f"Received exit signal {sig.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


if __name__ == "__main__":
    main()
