from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from manim import *

from manim_helpers import maths_text


ROW_GAP = 0.55
FONT_SIZE = 28
BIT_FONT_SIZE = 24
LABEL_WIDTH = 2.35
OP_WIDTH = 0.8
CARRY_WIDTH = 0.55
EXP_WIDTH = 1.05
ROW_HEIGHT = 0.52


@dataclass(frozen=True)
class BinaryField:
    label: str
    bits: str


def _bit_group(bits: str) -> VGroup:
    cells = VGroup()
    for bit in bits:
        cell = RoundedRectangle(corner_radius=0.08, width=0.44, height=0.44, stroke_width=2)
        cell.set_stroke(color=WHITE, opacity=0.75)
        cell.set_fill(BLACK, opacity=0)
        cell.add(maths_text(bit, font_size=BIT_FONT_SIZE).move_to(cell))
        cells.add(cell)
    cells.arrange(RIGHT, buff=0.07)
    return cells


def _field_row(field: BinaryField) -> VGroup:
    label = Text(field.label, font_size=FONT_SIZE)
    bits = _bit_group(field.bits)
    return VGroup(label, bits).arrange(RIGHT, buff=0.35, aligned_edge=UP)


def _align_rows(rows: VGroup) -> None:
    ref = max(rows, key=lambda row: row[1].width)
    for row in rows:
        row[1].align_to(ref[1], RIGHT)


def _binary_bits(value: int, bits: int) -> str:
    return format(value & ((1 << bits) - 1), f"0{bits}b")


def rename_rendered_video(scene_name: str, output_name: str) -> Path:
    media_root = Path.cwd() / "media" / "videos"
    matches = sorted(media_root.rglob(f"{scene_name}.mp4"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not matches:
        raise FileNotFoundError(f"Could not find rendered video for {scene_name}")

    source = matches[0]
    target = source.with_name(f"{output_name}.mp4")
    if target.exists():
        target.unlink()
    return source.replace(target)


def _slot(text: str, width: float, font_size: int = FONT_SIZE, color=WHITE) -> VGroup:
    box = RoundedRectangle(corner_radius=0.08, width=width, height=ROW_HEIGHT, stroke_width=0)
    box.set_fill(BLACK, opacity=0)
    label = Text(text, font_size=font_size, color=color)
    label.move_to(box)
    return VGroup(box, label)


def _blank_slot(width: float, font_size: int = FONT_SIZE) -> VGroup:
    return _slot(" ", width, font_size=font_size, color=BLACK)


def _point_marker(bits_group: VGroup, after_index: int) -> VMobject:
    point = maths_text(".", font_size=BIT_FONT_SIZE + 10, color=YELLOW)
    point.next_to(bits_group[after_index], RIGHT, buff=0.03)
    point.align_to(bits_group[after_index], DOWN)
    return point


def _standard_row(
    description: str,
    operator: str = "",
    carry: str = "",
    bits: str = "",
    exponent: str = "",
    point_after: int | None = None,
) -> VGroup:
    description_col = _slot(description, LABEL_WIDTH)
    operator_col = _slot(operator, OP_WIDTH) if operator else _blank_slot(OP_WIDTH)
    carry_col = _blank_slot(CARRY_WIDTH, font_size=BIT_FONT_SIZE)
    if carry:
        carry_text = maths_text(carry, font_size=BIT_FONT_SIZE)
        carry_text.move_to(carry_col[0])
        carry_col[1] = carry_text
    bits_col = _bit_group(bits)
    exponent_col = _bit_group(exponent) if exponent else _blank_slot(EXP_WIDTH)
    row = VGroup(description_col, operator_col, carry_col, bits_col, exponent_col).arrange(
        RIGHT, buff=0.22, aligned_edge=UP
    )
    if point_after is not None and 0 <= point_after < len(bits_col):
        row.point_marker = _point_marker(bits_col, point_after)
        row.add(row.point_marker)
    return row


class BinaryAdditionScene(Scene):
    def __init__(
        self,
        a: int = 65,
        b: int = 43,
        bits: int = 8,
        detailed_conversion: bool = False,
        show_denary_headers: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.a = a
        self.b = b
        self.bits = bits
        self.detailed_conversion = detailed_conversion
        self.show_denary_headers = show_denary_headers

    def _animate_denary_to_binary_breakdown(
        self,
        value: int,
        bits: str,
        bit_cells: VGroup,
        color=YELLOW,
    ) -> None:
        """Animate a denary number sweeping across a row, revealing each bit in place."""
        remaining = value
        tracker = maths_text(str(value), font_size=BIT_FONT_SIZE, color=color)
        tracker.move_to(bit_cells[0][0].get_center() + UP * 0.33)

        self.play(FadeIn(tracker), run_time=0.2)

        for col_index in range(self.bits):
            target = bit_cells[col_index][0].get_center() + UP * 0.33
            self.play(
                tracker.animate.move_to(target),
                bit_cells[col_index][1].animate.set_opacity(1.0),
                run_time=0.18,
            )

            if bits[col_index] == "1":
                column_value = 1 << (self.bits - 1 - col_index)
                remaining -= column_value
                updated = maths_text(str(remaining), font_size=BIT_FONT_SIZE, color=color)
                updated.move_to(tracker)
                self.play(Transform(tracker, updated), run_time=0.12)

        self.play(FadeOut(tracker), run_time=0.2)

    def construct(self):
        title = Text("Binary Addition", font_size=40).to_edge(UP)
        subtitle = Text(f"{self.a} + {self.b}", font_size=28, color=BLUE)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.1))

        a_bin = _binary_bits(self.a, self.bits)
        b_bin = _binary_bits(self.b, self.bits)

        # Build the full final layout with empty answer and carry rows.
        # Carry and sum rows need cell slots for each bit position, so pass spaces.
        rows = VGroup(
            _standard_row("", "", "", a_bin),
            _standard_row("", "+", "", b_bin),
            _standard_row("Carry", "", "", " " * self.bits),  # carry row - empty cells to start
            _standard_row("", "=", "", " " * self.bits),  # sum row - empty cells to start
        ).arrange(DOWN, buff=ROW_GAP, aligned_edge=LEFT)
        rows.next_to(subtitle, DOWN, buff=0.6).to_edge(LEFT, buff=0.65)
        _align_rows(rows)

        if self.show_denary_headers:
            denary_headers = VGroup()
            for col_index in range(self.bits):
                weight = 1 << (self.bits - 1 - col_index)
                header = Text(str(weight), font_size=16, color=GREY_B)
                header.next_to(rows[0][3][col_index][0], UP, buff=0.08)
                denary_headers.add(header)
            self.play(FadeIn(denary_headers, shift=UP * 0.08), run_time=0.35)

        if self.detailed_conversion:
            self.add(rows)
            for col_index in range(self.bits):
                rows[0][3][col_index][1].set_opacity(0)
                rows[1][3][col_index][1].set_opacity(0)
            self.wait(0.2)
            self._animate_denary_to_binary_breakdown(self.a, a_bin, rows[0][3], color=YELLOW)
            self._animate_denary_to_binary_breakdown(self.b, b_bin, rows[1][3], color=ORANGE)
            self.wait(0.2)
        else:
            # Show denary numbers morphing to binary inputs.
            denary_a = maths_text(str(self.a), font_size=BIT_FONT_SIZE)
            denary_b = maths_text(str(self.b), font_size=BIT_FONT_SIZE)
            op_plus = Text("+", font_size=FONT_SIZE)
            denary_a.align_to(rows[0][3], RIGHT).align_to(rows[0][3], UP)
            denary_b.align_to(rows[1][3], RIGHT).align_to(rows[1][3], UP)
            op_plus.move_to(rows[1][1])

            self.play(
                FadeIn(denary_a, shift=UP * 0.1),
                FadeIn(op_plus, shift=UP * 0.1),
                FadeIn(denary_b, shift=UP * 0.1),
            )
            self.wait(0.6)

            # Morph denary to binary.
            self.play(
                Transform(denary_a, rows[0][3]),
                Transform(denary_b, rows[1][3]),
                run_time=1.2,
            )
            self.wait(0.3)

            # Seamlessly replace with actual row structure.
            self.remove(denary_a, denary_b, op_plus)
            self.add(rows)
            self.wait(0.3)

        # Draw lines bracketing the work area.
        x_left  = rows[0][3].get_left()[0] - 0.05
        x_right = rows[0][3].get_right()[0] + 0.05
        top_y   = rows[1].get_bottom()[1] - 0.12
        bot_y   = rows[2].get_bottom()[1] - 0.12
        top_line = Line([x_left, top_y, 0], [x_right, top_y, 0], color=GREY_B, stroke_width=2)
        bot_line = Line([x_left, bot_y, 0], [x_right, bot_y, 0], color=WHITE, stroke_width=2)
        self.play(Create(top_line), Create(bot_line), run_time=0.4)
        self.wait(0.2)

        # Compute addition column by column, right to left.
        carry = 0
        for col_index in range(self.bits - 1, -1, -1):
            incoming_carry = carry

            # Extract bits from input strings.
            bit_a = int(a_bin[col_index])
            bit_b = int(b_bin[col_index])
            
            # Compute sum for this column.
            col_sum = bit_a + bit_b + incoming_carry
            result_bit = col_sum % 2
            carry_out = col_sum // 2
            carry = carry_out

            # Highlight the column (inputs + carry row).
            col_cells = [rows[0][3][col_index], rows[1][3][col_index]]
            if incoming_carry > 0 or col_index < self.bits - 1:  # Include carry cell if used
                col_cells.append(rows[2][3][col_index])
            
            col_group = VGroup(*col_cells)
            col_box = Rectangle(
                width=rows[0][3][col_index].width + 0.14,
                height=col_group.height + 0.14,
                color=BLUE,
                stroke_width=4,
            )
            col_box.move_to(col_group)
            self.play(Create(col_box), run_time=0.25)
            self.wait(0.15)

            # Display result and carry together so the column update happens simultaneously.
            result_target = rows[3][3][col_index][1]
            result_cell_box = rows[3][3][col_index][0]
            result_text = maths_text(str(result_bit), font_size=BIT_FONT_SIZE)
            result_text.move_to(result_cell_box)

            reveal_anims = [Transform(result_target, result_text)]
            if carry_out > 0 and col_index > 0:
                carry_target = rows[2][3][col_index - 1][1]
                carry_cell_box = rows[2][3][col_index - 1][0]
                carry_text = maths_text("1", font_size=BIT_FONT_SIZE)
                carry_text.move_to(carry_cell_box)
                reveal_anims.append(Transform(carry_target, carry_text))

            self.play(*reveal_anims, run_time=0.2)

            self.play(FadeOut(col_box), run_time=0.15)
            self.wait(0.1)

        # Highlight final answer bits by turning them green.
        answer_bits = VGroup(*[rows[3][3][i][1] for i in range(self.bits)])
        self.play(*[bit.animate.set_color(GREEN) for bit in answer_bits], run_time=0.35)

        # Show overflow carry in carry row, then mark overflow answer bit as discarded.
        carry_overflow_bit = None
        carry_overflow_box = None
        overflow_bit = None
        overflow_box = None
        if carry > 0:
            carry_overflow_bit = maths_text("1", font_size=BIT_FONT_SIZE, color=RED)
            carry_overflow_box = RoundedRectangle(corner_radius=0.08, width=0.44, height=0.44, stroke_width=2)
            carry_overflow_box.next_to(rows[2][3][0][0], LEFT, buff=0.07)
            carry_overflow_box.align_to(rows[2][3][0][0], UP)
            carry_overflow_box.set_stroke(color=RED, opacity=0.9, width=2.5)
            carry_overflow_box.set_fill(BLACK, opacity=0)
            carry_overflow_bit.move_to(carry_overflow_box)

            overflow_bit = maths_text("1", font_size=BIT_FONT_SIZE, color=RED)
            overflow_box = RoundedRectangle(corner_radius=0.08, width=0.44, height=0.44, stroke_width=2)
            overflow_box.move_to(rows[3][2][0])
            overflow_box.match_x(carry_overflow_box)
            overflow_box.align_to(rows[3][3][0][0], UP)
            overflow_box.set_stroke(color=RED, opacity=0.9, width=2.5)
            overflow_box.set_fill(BLACK, opacity=0)
            overflow_bit.move_to(overflow_box)
            # Match normal bit-reveal timing: overflow carry and overflow answer appear together.
            self.play(
                FadeIn(carry_overflow_box),
                FadeIn(carry_overflow_bit),
                FadeIn(overflow_box),
                FadeIn(overflow_bit),
                run_time=0.2,
            )

        # Convert the displayed binary result back to denary without removing binary output.
        displayed_result = (self.a + self.b) & ((1 << self.bits) - 1)
        denary_result = Text(f"= {displayed_result}", font_size=BIT_FONT_SIZE + 2, color=GREEN)
        denary_result.next_to(rows[3][3], RIGHT, buff=0.32)
        denary_result.align_to(rows[3][3][0][1], DOWN)
        self.play(FadeIn(denary_result, shift=RIGHT * 0.12), run_time=0.35)
        self.wait(1.2)


class TwosComplementScene(Scene):
    def __init__(self, value: int = 43, bits: int = 8, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.bits = bits

    def construct(self):
        title = Text("Two's Complement", font_size=40).to_edge(UP)
        subtitle = Text(f"Find -{self.value} in {self.bits} bits", font_size=28, color=BLUE)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.1))

        positive = _binary_bits(self.value, self.bits)
        flipped = "".join("1" if bit == "0" else "0" for bit in positive)
        negative = _binary_bits((1 << self.bits) - self.value, self.bits)

        rows = VGroup(
            _standard_row(f"+{self.value}", "=", "", positive),
            _standard_row("Flip", "→", "", flipped),
            _standard_row("Add 1", "+", "1", negative),
        ).arrange(DOWN, buff=ROW_GAP, aligned_edge=LEFT)
        rows.next_to(subtitle, DOWN, buff=0.6).to_edge(LEFT, buff=0.65)
        _align_rows(rows)

        self.play(FadeIn(rows[0], shift=UP * 0.1))
        self.play(FadeIn(rows[1], shift=UP * 0.1))
        for index in range(self.bits):
            box = SurroundingRectangle(rows[1][3][index], color=BLUE, buff=0.03)
            self.play(Create(box), run_time=0.14)
            self.play(FadeOut(box), run_time=0.08)

        self.play(FadeIn(rows[2], shift=UP * 0.1))
        plus_one_box = SurroundingRectangle(rows[2][3][0], color=YELLOW, buff=0.03)
        self.play(Create(plus_one_box), run_time=0.25)
        self.wait(1)


class FixedToFloatingScene(Scene):
    def __init__(self, fixed_value: str = "1101.0000", exponent: int = 4, exponent_bits: int = 4, **kwargs):
        super().__init__(**kwargs)
        self.fixed_value = fixed_value
        self.exponent = exponent
        self.exponent_bits = exponent_bits

    def construct(self):
        title = Text("Fixed to Floating Point", font_size=40).to_edge(UP)
        subtitle = Text("Normalise one step at a time", font_size=28, color=BLUE)
        subtitle.next_to(title, DOWN, buff=0.35)
        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.1))

        fixed_bits = self.fixed_value.replace(".", "")
        point_after = self.fixed_value.index(".") - 1
        normalised = fixed_bits[0] + fixed_bits[1:]
        exponent_bits = format(self.exponent & ((1 << self.exponent_bits) - 1), f"0{self.exponent_bits}b")

        rows = VGroup(
            _standard_row("Fixed", "=", "", fixed_bits),
            _standard_row("Mantissa", "→", "", normalised, point_after=point_after),
            _standard_row("Exponent", "=", "", "", exponent_bits),
        ).arrange(DOWN, buff=ROW_GAP, aligned_edge=LEFT)
        rows.next_to(subtitle, DOWN, buff=0.6).to_edge(LEFT, buff=0.65)
        _align_rows(rows)

        self.play(FadeIn(rows[0], shift=UP * 0.1))
        shift_note = Text("Move the binary point until the leading 1 is just left of it", font_size=24, color=YELLOW)
        shift_note.next_to(rows[0], DOWN, buff=0.25)
        self.play(FadeIn(shift_note, shift=UP * 0.1))

        self.play(FadeIn(rows[1], shift=UP * 0.1), FadeIn(rows[2], shift=UP * 0.1))

        for index in range(len(normalised)):
            box = SurroundingRectangle(rows[1][3][index], color=GREEN, buff=0.03)
            self.play(Create(box), run_time=0.12)
            self.play(FadeOut(box), run_time=0.08)

        exponent_box = SurroundingRectangle(rows[2][4], color=BLUE, buff=0.06)
        self.play(Create(exponent_box), run_time=0.25)
        self.wait(1)
