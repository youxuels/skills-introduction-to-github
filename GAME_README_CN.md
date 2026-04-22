# 初中英语剧情游戏（沉浸式学习）

现在提供两种形态：
- **前端可视版（推荐）**：`web_game.html`
- **命令行版**：`english_story_game.py`

## 1) 前端可视版（实现“前端可视”）

直接用浏览器打开 `web_game.html`，或用本地静态服务：

```bash
python3 -m http.server 8000
```

然后访问：

```text
http://localhost:8000/web_game.html
```

你会得到：
- 剧情文本区（章节推进）
- 实时问答区（词汇/语法）
- 学习仪表盘（XP、正确率、策略、词汇/语法权重）
- 错题本与事件日志
- “自动迭代模拟”按钮（可视化策略优化过程）

## 2) 命令行版

```bash
python3 english_story_game.py --mode play
```

自动优化（2 小时）：

```bash
python3 english_story_game.py --mode auto --hours 2
```

## 扩展到“全量初中英语”的建议

1. 在词汇表中按年级和单元补齐。
2. 在语法表中补齐全部语法点、规则和例句。
3. 每个单元对应至少一个剧情任务，做到“学-用-测”闭环。
4. 按学习数据继续调参（复现间隔、奖励机制、策略阈值）。
