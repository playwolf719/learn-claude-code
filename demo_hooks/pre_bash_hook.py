#!/usr/bin/env python3
"""
PreToolUse hook - 只拦截 bash 工具。

演示三种退出码：
  exit 0 → 正常通过
  exit 1 → 阻断执行（stderr 内容作为原因告知 Claude）
  exit 2 → 通过但注入提示（stderr 内容作为额外消息传给 Claude）
"""
import json
import os
import sys

event     = os.environ.get("HOOK_EVENT", "")
tool_name = os.environ.get("HOOK_TOOL_NAME", "")
raw_input = os.environ.get("HOOK_TOOL_INPUT", "{}")

try:
    tool_input = json.loads(raw_input)
except json.JSONDecodeError:
    tool_input = {}

command = tool_input.get("command", "")

print(f"[pre_bash_hook] 检查命令: {command!r}")

# --- 退出码 1：拦截危险命令 ---
BLOCKED = ["rm -rf /", "sudo rm", "shutdown", "reboot"]
for danger in BLOCKED:
    if danger in command:
        print(f"危险命令被拦截: {command!r}", file=sys.stderr)
        sys.exit(1)

# --- 退出码 2：注入警告（命令允许执行，但 Claude 会收到提示） ---
if "git push" in command:
    print("警告：即将执行 git push，请确认分支和内容是否正确。", file=sys.stderr)
    sys.exit(2)

# --- 退出码 0：正常通过 ---
sys.exit(0)
