#!/usr/bin/env python3
"""Throwaway interactive TUI prototype for the local AI Asset catalog.

Run: python3 prototype/catalog_tui.py
Keys: arrows/j/k navigate, Tab changes focus, / search, f family, h harness,
      Enter inspects, ! problems, r rescan, o/v/c source actions, ? help, q quit.
"""

from __future__ import annotations

import argparse
import curses
import textwrap
from typing import Any

FAMILIES = ("All", "Skill", "Agent", "Rule", "Prompt")

ASSETS: list[dict[str, Any]] = [
    {
        "name": "AGENTS.md",
        "family": "Rule",
        "description": "Shared repository guidance for coding agents.",
        "path": "~/projects/ai-harness-dashboard/AGENTS.md",
        "updated": "2 min ago",
        "placements": [
            ("Pi CLI", "project", "active", "./AGENTS.md"),
            ("Codex CLI", "project", "merged", "./AGENTS.md"),
            ("Cursor", "project", "active", "./AGENTS.md"),
            ("Copilot CLI", "project", "unknown", "./AGENTS.md"),
        ],
    },
    {
        "name": "research",
        "family": "Skill",
        "description": "Researches a question using primary sources.",
        "path": "~/.agents/skills/research/SKILL.md",
        "updated": "18 min ago",
        "placements": [
            ("Pi CLI", "user", "active", "~/.agents/skills/research"),
            ("Codex CLI", "user", "active", "~/.agents/skills/research"),
            ("Gemini CLI", "user", "active", "~/.agents/skills/research"),
        ],
    },
    {
        "name": "security-reviewer",
        "family": "Agent",
        "description": "Reviews trust boundaries and unsafe defaults.",
        "path": "~/.claude/agents/security-reviewer.md",
        "updated": "Yesterday",
        "placements": [("Claude Code", "user", "active", "~/.claude/agents/security-reviewer.md")],
    },
    {
        "name": "review-changes",
        "family": "Prompt",
        "description": "Reviews the working tree for actionable findings.",
        "path": "~/.pi/agent/prompts/review-changes.md",
        "updated": "3 days ago",
        "placements": [("Pi CLI", "user", "active", "~/.pi/agent/prompts/review-changes.md")],
    },
    {
        "name": "frontend-accessibility",
        "family": "Rule",
        "description": "Applies accessibility guidance to frontend files.",
        "path": "~/work/acme/.cursor/rules/frontend-accessibility.mdc",
        "updated": "5 days ago",
        "placements": [("Cursor", "project", "active", ".cursor/rules/frontend-accessibility.mdc")],
    },
]

HARNESSES = (
    "All",
    *sorted({placement[0] for asset in ASSETS for placement in asset["placements"]}),
)


def filtered_assets(query: str, family: str, harness: str) -> list[dict[str, Any]]:
    needle = query.strip().lower()
    return [
        asset
        for asset in ASSETS
        if (family == "All" or asset["family"] == family)
        and (harness == "All" or any(p[0] == harness for p in asset["placements"]))
        and (
            not needle
            or needle
            in " ".join(
                (
                    asset["name"],
                    asset["family"],
                    asset["description"],
                    asset["path"],
                    *(placement[0] for placement in asset["placements"]),
                )
            ).lower()
        )
    ]


def clipped(text: str, width: int) -> str:
    if width <= 0:
        return ""
    return text if len(text) <= width else text[: max(0, width - 1)] + "…"


def add(window: Any, y: int, x: int, text: str, style: int = 0) -> None:
    height, width = window.getmaxyx()
    if 0 <= y < height and 0 <= x < width:
        try:
            window.addstr(y, x, clipped(text, width - x), style)
        except curses.error:
            pass


def draw_header(screen: Any, width: int) -> None:
    add(screen, 0, 0, " AI Harness Dashboard ", curses.color_pair(1) | curses.A_BOLD)
    add(screen, 0, max(23, width - 14), " LOCAL ONLY ", curses.color_pair(2))


def draw_list(
    screen: Any,
    assets: list[dict[str, Any]],
    selected: int,
    focused: bool,
    top: int,
    bottom: int,
    width: int,
) -> None:
    add(screen, top, 1, "ASSETS" + (" · FOCUSED" if focused else ""), curses.A_BOLD)
    visible_rows = max(1, bottom - top - 2)
    offset = min(max(0, selected - visible_rows + 1), max(0, len(assets) - visible_rows))

    if not assets:
        add(screen, top + 2, 1, "No matching assets", curses.A_DIM)
        return

    for row, asset in enumerate(assets[offset : offset + visible_rows], start=top + 2):
        index = offset + row - top - 2
        marker = ">" if index == selected else " "
        label = f"{marker} {asset['name']}"
        style = curses.color_pair(3) | curses.A_BOLD if index == selected else 0
        add(screen, row, 1, label, style)
        family = f"[{asset['family']}]"
        add(screen, row, max(3, width - len(family) - 2), family, curses.A_DIM)


def draw_detail(
    screen: Any,
    asset: dict[str, Any] | None,
    placement_index: int,
    placements_focused: bool,
    top: int,
    bottom: int,
    left: int,
    width: int,
) -> None:
    if asset is None:
        add(screen, top, left + 2, "DETAIL", curses.A_BOLD)
        add(screen, top + 2, left + 2, "Select an asset", curses.A_DIM)
        return

    x = left + 2
    content_width = max(20, width - x - 2)
    add(screen, top, x, "DETAIL", curses.A_BOLD)
    add(screen, top + 2, x, asset["name"], curses.A_BOLD)
    add(screen, top + 3, x, f"{asset['family']}  ·  updated {asset['updated']}", curses.A_DIM)

    row = top + 5
    for line in textwrap.wrap(asset["description"], content_width):
        add(screen, row, x, line)
        row += 1

    row += 1
    add(screen, row, x, "PATH", curses.A_BOLD)
    row += 1
    for line in textwrap.wrap(asset["path"], content_width):
        add(screen, row, x, line, curses.color_pair(4))
        row += 1

    row += 1
    add(
        screen,
        row,
        x,
        "PLACEMENTS" + (" · FOCUSED" if placements_focused else ""),
        curses.A_BOLD,
    )
    row += 1
    for index, (harness, scope, state, _path) in enumerate(asset["placements"]):
        if row >= bottom - 3:
            break
        marker = ">" if placements_focused and index == placement_index else " "
        style = curses.color_pair(3) | curses.A_BOLD if marker == ">" else 0
        add(screen, row, x, f"{marker} {harness:<16} {scope:<8}", style)
        add(screen, row, min(width - len(state) - 2, x + 31), state.upper(), curses.color_pair(2) if state in ("active", "merged") else curses.A_DIM)
        row += 1

    if asset["placements"] and row < bottom - 1:
        harness, scope, state, path = asset["placements"][placement_index]
        add(screen, row + 1, x, f"Selected: {harness} · {scope} · {state}", curses.A_DIM)
        if row + 2 < bottom:
            add(screen, row + 2, x, path, curses.color_pair(4))


def draw_overlay(screen: Any, height: int, width: int, title: str, lines: tuple[str, ...]) -> None:
    box_width = min(70, width - 4)
    box_height = min(height - 2, len(lines) + 5)
    y = max(1, (height - box_height) // 2)
    x = max(2, (width - box_width) // 2)
    window = curses.newwin(box_height, box_width, y, x)
    window.bkgd(" ", curses.color_pair(5))
    window.border()
    add(window, 1, 2, title, curses.A_BOLD)
    for row, line in enumerate(lines[: box_height - 4], start=3):
        add(window, row, 2, line)
    add(window, box_height - 2, 2, "Esc or any listed toggle key to close", curses.A_DIM)
    window.refresh()


def help_lines() -> tuple[str, ...]:
    return (
        "↑/↓ or j/k   Navigate the focused list",
        "Tab          Focus Assets or Placements",
        "/            Search",
        "x            Clear search",
        "f / h        Cycle Asset Family / Harness Surface",
        "Enter        Inspect selected Asset or Placement",
        "!            Show Discovery Problems",
        "r            Rescan",
        "o / v / c    Open / reveal / copy path",
        "?            Toggle this help",
        "q            Quit",
    )


def preview_lines(asset: dict[str, Any]) -> tuple[str, ...]:
    placements = tuple(
        f"  {harness} · {scope} · {state} · {path}"
        for harness, scope, state, path in asset["placements"]
    )
    return (
        asset["description"],
        "",
        f"Family: {asset['family']}",
        f"Path: {asset['path']}",
        f"Updated: {asset['updated']}",
        "",
        "Placements:",
        *placements,
        "",
        "Read-only preview; source content is never executed.",
    )


def placement_lines(asset: dict[str, Any], index: int) -> tuple[str, ...]:
    harness, scope, state, path = asset["placements"][index]
    return (
        f"Asset: {asset['name']}",
        f"Harness Surface: {harness}",
        f"Scope: {scope}",
        f"Resolution State: {state}",
        f"Observed path: {path}",
        "",
        "This is adapter evidence, not a universal precedence decision.",
    )


def prompt_search(screen: Any, height: int, width: int, current: str) -> str:
    prompt = "/ "
    screen.move(height - 1, 0)
    screen.clrtoeol()
    add(screen, height - 1, 0, prompt + current, curses.A_REVERSE)
    screen.move(height - 1, len(prompt) + len(current))
    curses.echo()
    try:
        value = screen.getstr(height - 1, len(prompt), max(1, width - len(prompt) - 1))
        return value.decode(errors="replace")
    except curses.error:
        return current
    finally:
        curses.noecho()
        screen.keypad(True)


def run(screen: Any) -> None:
    curses.curs_set(0)
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_CYAN, -1)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_CYAN, -1)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)
    screen.keypad(True)

    selected = 0
    placement_index = 0
    focus = "assets"
    family_index = 0
    harness_index = 0
    query = ""
    status = "5 assets from 3 Source Roots · 1 Discovery Problem"
    overlay: str | None = None

    while True:
        screen.erase()
        height, width = screen.getmaxyx()
        if height < 20 or width < 78:
            add(screen, 0, 0, "Terminal too small. Resize to at least 78×20.", curses.A_BOLD)
            screen.refresh()
            if screen.getch() in (ord("q"), 27):
                return
            continue

        family = FAMILIES[family_index]
        harness = HARNESSES[harness_index]
        assets = filtered_assets(query, family, harness)
        selected = min(selected, max(0, len(assets) - 1))
        asset = assets[selected] if assets else None
        placement_index = min(
            placement_index,
            max(0, len(asset["placements"]) - 1) if asset else 0,
        )
        left_width = max(30, min(42, width // 3))
        top = 3
        bottom = height - 2

        draw_header(screen, width)
        filter_text = f"Family: {family}  ·  Harness: {harness}"
        if query:
            filter_text += f"  ·  Search: {query}"
        add(screen, 1, 1, f"{len(assets)} results  ·  {filter_text}", curses.A_DIM)
        screen.hline(2, 0, curses.ACS_HLINE, width)
        screen.vline(top, left_width, curses.ACS_VLINE, max(1, bottom - top))
        draw_list(screen, assets, selected, focus == "assets", top, bottom, left_width)
        draw_detail(
            screen,
            asset,
            placement_index,
            focus == "placements",
            top,
            bottom,
            left_width,
            width,
        )
        screen.hline(height - 2, 0, curses.ACS_HLINE, width)
        add(screen, height - 1, 0, " Tab focus  ↑↓ navigate  / search  f family  h harness  Enter inspect  ! problems  ? help  q quit ", curses.A_REVERSE)
        add(screen, height - 2, 1, status, curses.A_DIM)
        screen.refresh()

        if overlay == "help":
            draw_overlay(screen, height, width, "KEYS", help_lines())
        elif overlay == "asset" and asset:
            draw_overlay(screen, height, width, f"ASSET · {asset['name']}", preview_lines(asset))
        elif overlay == "placement" and asset:
            draw_overlay(
                screen,
                height,
                width,
                "PLACEMENT",
                placement_lines(asset, placement_index),
            )
        elif overlay == "problems":
            draw_overlay(
                screen,
                height,
                width,
                "DISCOVERY PROBLEMS",
                (
                    "Unreadable entry: ~/work/legacy/.agents/skills/old/SKILL.md",
                    "Reason: permission denied",
                    "",
                    "No partial Asset was added to the Catalog Snapshot.",
                ),
            )

        key = screen.getch()
        if overlay:
            overlay = None
            continue
        if key in (ord("q"), 27):
            return
        if key == ord("?"):
            overlay = "help"
            continue
        if key == 9 and asset:
            focus = "placements" if focus == "assets" else "assets"
            status = f"Focus: {focus.title()}"
        elif key in (curses.KEY_UP, ord("k")):
            if focus == "assets":
                selected = max(0, selected - 1)
                placement_index = 0
            elif asset:
                placement_index = max(0, placement_index - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            if focus == "assets":
                selected = min(max(0, len(assets) - 1), selected + 1)
                placement_index = 0
            elif asset:
                placement_index = min(len(asset["placements"]) - 1, placement_index + 1)
        elif key == ord("f"):
            family_index = (family_index + 1) % len(FAMILIES)
            selected = 0
            placement_index = 0
            focus = "assets"
            status = f"Asset Family: {FAMILIES[family_index]}"
        elif key == ord("h"):
            harness_index = (harness_index + 1) % len(HARNESSES)
            selected = 0
            placement_index = 0
            focus = "assets"
            status = f"Harness Surface: {HARNESSES[harness_index]}"
        elif key in (10, 13, curses.KEY_ENTER) and asset:
            overlay = "asset" if focus == "assets" else "placement"
        elif key == ord("!"):
            overlay = "problems"
        elif key == ord("/"):
            curses.curs_set(1)
            query = prompt_search(screen, height, width, query)
            curses.curs_set(0)
            selected = 0
            placement_index = 0
            focus = "assets"
            status = f"Search: {query or 'cleared'}"
        elif key == ord("x"):
            query = ""
            selected = 0
            placement_index = 0
            focus = "assets"
            status = "Search cleared"
        elif key == ord("r"):
            status = "Scan complete · no changes"
        elif key in (ord("o"), ord("v"), ord("c")) and asset:
            action = {ord("o"): "Open", ord("v"): "Reveal", ord("c"): "Copy path"}[key]
            status = f"{action}: {asset['name']} · prototype only"


def check() -> None:
    assert [asset["name"] for asset in filtered_assets("codex", "All", "All")] == [
        "AGENTS.md",
        "research",
    ]
    assert [asset["name"] for asset in filtered_assets("", "Rule", "All")] == [
        "AGENTS.md",
        "frontend-accessibility",
    ]
    assert [asset["name"] for asset in filtered_assets("", "All", "Gemini CLI")] == [
        "research",
    ]
    assert clipped("abcdef", 4) == "abc…"
    print("catalog_tui.py: check passed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="run the self-check")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        curses.wrapper(run)


if __name__ == "__main__":
    main()
