# 初中英语剧情游戏（沉浸式学习）

这是一个可运行的命令行原型：
- 用**完整故事线**把词汇、语法和情境任务串起来；
- 采用**记忆法则**（间隔重复、主动回忆、错题强化）；
- 支持“**自动迭代优化**”模式，可设定运行时长（例如 2 小时）。

## 快速开始

```bash
python3 english_story_game.py --mode play
```

## 自动优化（2 小时）

```bash
python3 english_story_game.py --mode auto --hours 2
```

> 由于演示环境通常不适合真的运行 2 小时，你也可以先短跑验证：

```bash
python3 english_story_game.py --mode auto --hours 0.001 --report-every 1
```

## 如何扩展到“全量初中英语”

1. 在 `CURRICULUM["vocab"]` 中补充各年级词汇。
2. 在 `CURRICULUM["grammar"]` 中补充所有语法点与例句。
3. 在 `CURRICULUM["scenarios"]` 中按单元创建剧情任务，确保每关覆盖目标词汇与语法。
4. 根据学习反馈继续调参（词汇/语法权重、复现间隔、奖励机制）。
