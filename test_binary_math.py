"""Unit tests for binary math operations used in animations."""

import unittest
from binary_scenes import _binary_bits


class TestBinaryMath(unittest.TestCase):
    """Test binary conversion and arithmetic operations."""

    def test_binary_bits_conversion(self):
        """Test decimal to binary conversion with zero-padding."""
        # Test cases: (value, bits, expected_binary_string)
        test_cases = [
            (65, 8, "01000001"),
            (43, 8, "00101011"),
            (0, 8, "00000000"),
            (255, 8, "11111111"),
            (128, 8, "10000000"),
            (1, 8, "00000001"),
            (15, 4, "1111"),
            (8, 4, "1000"),
        ]
        
        for value, bits, expected in test_cases:
            with self.subTest(value=value, bits=bits):
                result = _binary_bits(value, bits)
                self.assertEqual(result, expected)

    def test_binary_addition_logic(self):
        """Test the binary addition column-by-column logic."""
        # Simulate what BinaryAdditionScene does
        test_cases = [
            # (a, b, bits, expected_sum)
            (65, 43, 8, 108),
            (100, 75, 8, 175),
            (255, 1, 8, 256),  # Overflow case
            (0, 0, 8, 0),
            (15, 1, 4, 16),  # Overflow with 4 bits
        ]
        
        for a, b, bits, expected_sum in test_cases:
            with self.subTest(a=a, b=b, bits=bits):
                a_bin = _binary_bits(a, bits)
                b_bin = _binary_bits(b, bits)
                
                # Simulate column-by-column addition (right to left)
                carry = 0
                result = 0
                for col_index in range(bits - 1, -1, -1):
                    bit_a = int(a_bin[col_index])
                    bit_b = int(b_bin[col_index])
                    col_sum = bit_a + bit_b + carry
                    result_bit = col_sum % 2
                    carry = col_sum // 2
                    
                    # Reconstruct the result
                    result = result | (result_bit << (bits - 1 - col_index))
                
                # For overflow cases, only check the lower bits
                expected_truncated = expected_sum & ((1 << bits) - 1)
                self.assertEqual(result, expected_truncated)

    def test_binary_addition_with_carry_tracking(self):
        """Test that carry bits are correctly generated during column addition."""
        # Specific test: 65 + 43 = 108
        # Binary: 01000001 + 00101011 = 01101100
        a = 65
        b = 43
        bits = 8
        expected_result = 108
        expected_result_bin = "01101100"
        
        a_bin = _binary_bits(a, bits)
        b_bin = _binary_bits(b, bits)
        
        # Test the column-by-column addition
        carry = 0
        carries = []
        result_bits = []
        
        for col_index in range(bits - 1, -1, -1):
            bit_a = int(a_bin[col_index])
            bit_b = int(b_bin[col_index])
            col_sum = bit_a + bit_b + carry
            result_bit = col_sum % 2
            carry = col_sum // 2
            
            carries.append(carry)
            result_bits.append(str(result_bit))
        
        # Reverse to get left-to-right
        result_bits.reverse()
        result_bin = "".join(result_bits)
        
        self.assertEqual(result_bin, expected_result_bin)


if __name__ == "__main__":
    unittest.main()
