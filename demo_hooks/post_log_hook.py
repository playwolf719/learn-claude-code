#!/usr/bin/env python3
"""
PostToolUse hook - 匹配所有工具，记录执行日志。

退出码 0：静默通过，打印日志到终端。
"""
import os
import sys

tool_name   = os.environ.get("HOOK_TOOL_NAME", "unknown")
tool_output = os.environ.get("HOOK_TOOL_OUTPUT", "")[:80]

print(f"[post_log_hook] {tool_name} 执行完毕 | 输出前80字: {tool_output!r}")
sys.exit(0)
