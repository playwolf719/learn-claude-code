## 用例
```
- s03
写一个 Python 函数计算斐波那契数列，然后写测试，再运行测试
- s04
用 task 工具让 subagent 读取 requirements.txt，然后告诉我里面列了哪些依赖。
- s05
do a code review of agents/s05_skill_loading.py

```


## 去除代理

```python
import os
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
```