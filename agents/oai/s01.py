#!/usr/bin/env python3
# Harness: the loop -- keep feeding real tool results back into the model.
"""
oai/s01.py - The Agent Loop (OpenAI version)

Same smallest-useful coding-agent pattern as agents/s01_agent_loop.py,
rewritten for the OpenAI API:

    user message
      -> model reply
      -> if tool_calls: execute tools
      -> write tool results back to messages
      -> continue
"""

import os
import subprocess
from dataclasses import dataclass

try:
    import readline
    readline.parse_and_bind('set bind-tty-special-chars off')
    readline.parse_and_bind('set input-meta on')
    readline.parse_and_bind('set output-meta on')
    readline.parse_and_bind('set convert-meta off')
    readline.parse_and_bind('set enable-meta-keybindings on')
except ImportError:
    pass

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL"),  # 未设置时用官方地址
    api_key=os.environ.get("OPENAI_API_KEY", ""),
)

MODEL = os.environ.get("OPENAI_MODEL_ID", "gpt-4o")

SYSTEM = (
    f"You are a coding agent at {os.getcwd()}. "
    "Use bash to inspect and change the workspace. Act first, then report clearly."
)

TOOLS = [{
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Run a shell command in the current workspace.",
        "parameters": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
}]


@dataclass
class LoopState:
    messages: list
    turn_count: int = 1
    transition_reason: str | None = None


def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(item in command for item in dangerous):
        return "Error: Dangerous command blocked"
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"

    output = (result.stdout + result.stderr).strip()
    return output[:50000] if output else "(no output)"


def execute_tool_calls(tool_calls) -> list[dict]:
    results = []
    for tc in tool_calls:
        if tc.function.name != "bash":
            continue
        import json
        command = json.loads(tc.function.arguments)["command"]
        print(f"\033[33m$ {command}\033[0m")
        output = run_bash(command)
        print(output[:1000])
        results.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": output,
        })
    return results


def run_one_turn(state: LoopState) -> bool:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM}] + state.messages,
        tools=TOOLS,
        max_tokens=8000,
    )
    message = response.choices[0].message

    # Append assistant message (preserve tool_calls if present)
    assistant_msg = {"role": "assistant", "content": message.content or ""}
    if message.tool_calls:
        assistant_msg["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in message.tool_calls
        ]
    state.messages.append(assistant_msg)

    if response.choices[0].finish_reason != "tool_calls":
        state.transition_reason = None
        return False

    results = execute_tool_calls(message.tool_calls)
    if not results:
        state.transition_reason = None
        return False

    state.messages.extend(results)
    state.turn_count += 1
    state.transition_reason = "tool_result"
    return True


def agent_loop(state: LoopState) -> None:
    while run_one_turn(state):
        pass


if __name__ == "__main__":
    history = []
    while True:
        try:
            query = input("\033[36ms01-oai >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break

        history.append({"role": "user", "content": query})
        state = LoopState(messages=history)
        agent_loop(state)

        last = history[-1]
        if last["role"] == "assistant" and last.get("content"):
            print(last["content"])
        print()
