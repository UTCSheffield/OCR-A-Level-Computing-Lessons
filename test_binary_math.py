"""Pytest coverage for binary math operations used in animations."""

import pytest

from binary_scenes import _binary_bits, _floating_point_components, _twos_complement_bits


@pytest.mark.parametrize(
    ("value", "bits", "expected"),
    [
        (65, 8, "01000001"),
        (43, 8, "00101011"),
        (0, 8, "00000000"),
        (255, 8, "11111111"),
        (128, 8, "10000000"),
        (1, 8, "00000001"),
        (15, 4, "1111"),
        (8, 4, "1000"),
    ],
)
def test_binary_bits_conversion(value, bits, expected):
    assert _binary_bits(value, bits) == expected


@pytest.mark.parametrize(
    ("a", "b", "bits", "expected_sum"),
    [
        (65, 43, 8, 108),
        (100, 75, 8, 175),
        (255, 1, 8, 256),
        (0, 0, 8, 0),
        (15, 1, 4, 16),
    ],
)
def test_binary_addition_logic(a, b, bits, expected_sum):
    a_bin = _binary_bits(a, bits)
    b_bin = _binary_bits(b, bits)

    carry = 0
    result = 0
    for col_index in range(bits - 1, -1, -1):
        bit_a = int(a_bin[col_index])
        bit_b = int(b_bin[col_index])
        col_sum = bit_a + bit_b + carry
        result_bit = col_sum % 2
        carry = col_sum // 2
        result |= result_bit << (bits - 1 - col_index)

    assert result == (expected_sum & ((1 << bits) - 1))


def test_binary_addition_with_carry_tracking():
    a_bin = _binary_bits(65, 8)
    b_bin = _binary_bits(43, 8)

    carry = 0
    result_bits = []
    for col_index in range(7, -1, -1):
        bit_a = int(a_bin[col_index])
        bit_b = int(b_bin[col_index])
        col_sum = bit_a + bit_b + carry
        result_bits.append(str(col_sum % 2))
        carry = col_sum // 2

    assert "".join(reversed(result_bits)) == "01101100"


@pytest.mark.parametrize(
    ("value", "bits", "expected"),
    [
        (43, 8, "11010101"),
        (77, 8, "10110011"),
        (1, 8, "11111111"),
        (3, 4, "1101"),
    ],
)
def test_twos_complement_bits(value, bits, expected):
    assert _twos_complement_bits(value, bits) == expected


def test_fixed_to_floating_normalises_1_125():
    components = _floating_point_components(
        denary_value=1.125,
        integer_bits=4,
        fraction_bits=4,
        mantissa_bits=8,
        exponent_bits=4,
    )

    assert components.fixed_value == "0001.0010"
    assert components.mantissa_bits == "01001000"
    assert components.exponent_value == 1
    assert components.exponent_bits == "0001"
    assert components.floating_value == pytest.approx(1.125)
    assert components.precision_loss == pytest.approx(0.0)


def test_fixed_exact_but_floating_loses_sixteenth():
    components = _floating_point_components(
        denary_value=8.0625,
        integer_bits=4,
        fraction_bits=4,
        mantissa_bits=8,
        exponent_bits=4,
    )

    assert components.fixed_value == "1000.0001"
    assert components.mantissa_bits == "01000000"
    assert components.exponent_value == 4
    assert components.exponent_bits == "0100"
    assert components.fixed_value_numeric == pytest.approx(8.0625)
    assert components.floating_value == pytest.approx(8.0)
    assert components.precision_loss == pytest.approx(0.0625)
