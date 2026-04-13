# CLAUDE.md

## Python Environment

Python 虚拟环境在 `.venv/` 下。运行 Python 命令时始终使用：

```bash
.venv/bin/python
.venv/bin/pip
```

安装依赖：

```bash
.venv/bin/pip install -r requirements.txt
```

去除代理

```python
import os
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
```