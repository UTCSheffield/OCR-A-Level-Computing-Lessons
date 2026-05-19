from __future__ import annotations

import re

from manim import RIGHT, Text

MATHS_FONT = "DejaVu Sans Mono"


def maths_text(text: str, font_size: int, **kwargs) -> Text:
    return Text(text, font_size=font_size, font=MATHS_FONT, **kwargs)


def align_lines_right(lines) -> None:
    lines = list(lines)
    if not lines:
        return
    ref = max(lines, key=lambda m: m.width)
    for line in lines:
        line.align_to(ref, RIGHT)


def align_group_indices_right(group, indices) -> None:
    align_lines_right(group[i] for i in indices)


def first_binary_after_equals_idx(text: str) -> int:
    match = re.search(r"=\s*([01])", text)
    return match.start(1) if match else text.find("1")
