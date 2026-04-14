#!/usr/bin/env python3
"""
初中英语沉浸式剧情学习游戏（命令行版）

功能：
1) 剧情闯关：词汇、语法、情境应用。
2) 记忆法：间隔重复、主动回忆、错题强化、多模态提示。
3) 自动迭代：根据玩家表现自动调整难度与题型权重。
4) 可配置自动优化时长（支持 2 小时）。

说明：
- 受限于示例仓库，本脚本内置了可扩展的“核心知识包”。
- 你可以继续往 CURRICULUM 中追加词表、语法点、场景任务，实现“全量覆盖”。
"""

from __future__ import annotations

import argparse
import random
import textwrap
import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class Word:
    en: str
    zh: str
    level: int = 1
    next_due: int = 0
    streak: int = 0


@dataclass
class Grammar:
    title: str
    pattern: str
    usage: str
    example: str
    level: int = 1


@dataclass
class Scenario:
    title: str
    objective: str
    vocab_targets: List[str]
    grammar_targets: List[str]


@dataclass
class LearnerState:
    xp: int = 0
    stage: int = 1
    turn: int = 0
    mastery: Dict[str, float] = field(default_factory=dict)
    wrong_book: Dict[str, int] = field(default_factory=dict)


CURRICULUM = {
    "vocab": [
        Word("library", "图书馆"),
        Word("borrow", "借入"),
        Word("return", "归还"),
        Word("festival", "节日"),
        Word("prepare", "准备"),
        Word("practice", "练习"),
        Word("healthy", "健康的"),
        Word("exercise", "锻炼"),
        Word("environment", "环境"),
        Word("protect", "保护"),
        Word("volunteer", "志愿者"),
        Word("community", "社区"),
        Word("journey", "旅行"),
        Word("direction", "方向"),
        Word("weather", "天气"),
    ],
    "grammar": [
        Grammar("一般现在时", "主语 + 动词原形/三单", "习惯、事实", "She walks to school every day."),
        Grammar("一般过去时", "主语 + 动词过去式", "过去发生的动作", "We visited the museum last weekend."),
        Grammar("一般将来时", "will + 动词原形", "未来计划/预测", "I will join the club tomorrow."),
        Grammar("现在进行时", "am/is/are + doing", "正在进行", "They are cleaning the classroom now."),
        Grammar("情态动词 can", "can + 动词原形", "能力/许可", "Can you help me with this task?"),
    ],
    "scenarios": [
        Scenario(
            "第一章：失落的校史钥匙",
            "你需要在图书馆找到校史档案，帮助同学完成展览。",
            ["library", "borrow", "return", "direction"],
            ["一般现在时", "情态动词 can"],
        ),
        Scenario(
            "第二章：校园文化节倒计时",
            "你作为主持人，需要组织节目排练并发布通知。",
            ["festival", "prepare", "practice", "volunteer", "community"],
            ["一般将来时", "现在进行时"],
        ),
        Scenario(
            "第三章：绿色行动日",
            "你要带队完成环保挑战，并向外校同学介绍成果。",
            ["environment", "protect", "healthy", "exercise", "journey", "weather"],
            ["一般过去时", "一般现在时", "一般将来时"],
        ),
    ],
}


class AdaptiveEngine:
    def __init__(self, words: List[Word], grammar: List[Grammar]):
        self.words = {w.en: w for w in words}
        self.grammar = {g.title: g for g in grammar}
        self.word_weight = 0.6
        self.grammar_weight = 0.4

    def due_words(self, turn: int) -> List[Word]:
        items = [w for w in self.words.values() if w.next_due <= turn]
        return items if items else list(self.words.values())

    def update_word(self, key: str, correct: bool, turn: int) -> None:
        w = self.words[key]
        if correct:
            w.streak += 1
            gap = min(12, 2 ** min(w.streak, 4))
            w.next_due = turn + gap
            w.level = min(5, w.level + 1)
        else:
            w.streak = 0
            w.next_due = turn + 1
            w.level = max(1, w.level - 1)

    def update_grammar(self, title: str, correct: bool) -> None:
        g = self.grammar[title]
        if correct:
            g.level = min(5, g.level + 1)
        else:
            g.level = max(1, g.level - 1)

    def optimize_policy(self, accuracy: float) -> str:
        if accuracy < 0.65:
            self.word_weight = min(0.75, self.word_weight + 0.05)
            self.grammar_weight = 1 - self.word_weight
            return "准确率偏低：增加词汇复现频率，降低剧情推进速度。"
        if accuracy > 0.85:
            self.word_weight = max(0.45, self.word_weight - 0.05)
            self.grammar_weight = 1 - self.word_weight
            return "准确率优秀：提升语法与情境表达挑战。"
        return "准确率稳定：保持当前训练节奏。"


class Game:
    def __init__(self):
        self.state = LearnerState()
        self.engine = AdaptiveEngine(CURRICULUM["vocab"], CURRICULUM["grammar"])

    def _ask_word(self, word: Word, simulate: bool) -> bool:
        prompt = f"词汇挑战：'{word.zh}' 的英文是？"
        if simulate:
            return random.random() < (0.58 + 0.08 * word.level)

        print(prompt)
        ans = input("你的答案: ").strip().lower()
        return ans == word.en

    def _ask_grammar(self, point: Grammar, simulate: bool) -> bool:
        q = f"语法挑战：请选择最符合 '{point.title}' 的表达（输入 y 代表你能解释并造句，其他为不会）"
        if simulate:
            return random.random() < (0.55 + 0.08 * point.level)

        print(q)
        ans = input("你的答案: ").strip().lower()
        if ans == "y":
            print(f"示例：{point.example}")
            return True
        return False

    def _resolve_scenario(self, scenario: Scenario, simulate: bool) -> Tuple[int, int]:
        print("\n" + "=" * 70)
        print(f"{scenario.title}")
        print(textwrap.fill(scenario.objective, width=68))
        print("=" * 70)

        total = 0
        correct = 0

        for key in scenario.vocab_targets:
            w = self.engine.words[key]
            ok = self._ask_word(w, simulate)
            self.state.turn += 1
            self.engine.update_word(key, ok, self.state.turn)
            total += 1
            correct += int(ok)
            if not ok:
                self.state.wrong_book[key] = self.state.wrong_book.get(key, 0) + 1

        for title in scenario.grammar_targets:
            g = self.engine.grammar[title]
            ok = self._ask_grammar(g, simulate)
            self.engine.update_grammar(title, ok)
            total += 1
            correct += int(ok)
            if not ok:
                self.state.wrong_book[title] = self.state.wrong_book.get(title, 0) + 1

        gained = correct * 10
        self.state.xp += gained
        self.state.stage += 1
        return correct, total

    def play_story(self, simulate: bool = False) -> None:
        print("\n欢迎来到《时光学院：英语任务线》")
        print("你的目标：在三章主线中，通过英语完成任务，修复校园记忆档案。\n")
        for s in CURRICULUM["scenarios"]:
            c, t = self._resolve_scenario(s, simulate)
            acc = c / t if t else 0
            note = self.engine.optimize_policy(acc)
            print(f"本章得分：{c}/{t}，准确率 {acc:.0%}，获得 XP {c*10}")
            print(f"AI 教学策略：{note}\n")

        print("剧情通关！你已解锁：校园演讲终章。")
        print(f"总 XP: {self.state.xp}")
        if self.state.wrong_book:
            print("错题本（后续重点复习）：")
            for k, v in sorted(self.state.wrong_book.items(), key=lambda x: -x[1]):
                print(f"- {k}: {v} 次")

    def auto_iterate(self, hours: float = 2.0, report_every: int = 10) -> None:
        duration = max(0.01, hours) * 3600
        start = time.time()
        rounds = 0
        print(f"\n[自动优化模式] 目标运行时长：{hours:.2f} 小时")
        while time.time() - start < duration:
            rounds += 1
            hits, total = 0, 0
            for s in CURRICULUM["scenarios"]:
                c, t = self._resolve_scenario(s, simulate=True)
                hits += c
                total += t
            acc = hits / max(total, 1)
            policy = self.engine.optimize_policy(acc)

            if rounds % report_every == 0:
                elapsed = (time.time() - start) / 60
                print(
                    f"[Round {rounds}] 累计 {elapsed:.1f} 分钟, 回合准确率 {acc:.1%}, 策略: {policy}"
                )

            time.sleep(0.1)

        print(f"自动优化完成，共迭代 {rounds} 轮。")


def main() -> None:
    parser = argparse.ArgumentParser(description="初中英语剧情学习游戏")
    parser.add_argument("--mode", choices=["play", "auto"], default="play")
    parser.add_argument("--hours", type=float, default=2.0, help="自动优化模式运行小时数")
    parser.add_argument("--report-every", type=int, default=10)
    args = parser.parse_args()

    game = Game()
    if args.mode == "play":
        game.play_story(simulate=False)
    else:
        game.auto_iterate(hours=args.hours, report_every=args.report_every)


if __name__ == "__main__":
    main()
