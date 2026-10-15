"""
Dynamically Synthesized Tool for ULTRON: caesar_cipher_vault
Created: 2026-10-04 22:27:41
Instruction: Encode or decode text with a Caesar cipher shift key (default shift=3). Parameters: text: str, shift: int = 3, mode: str = 'encode'. Returns the transformed string with formatted details.
"""

"""
ULTRON Core Systems Module: Caesar Cipher Vault

Provides a production-grade async implementation of the Caesar cipher
for encoding and decoding text with configurable shift values.
"""

import re
from typing import Optional


async def caesar_cipher_vault(
    text: str,
    shift: int = 3,
    mode: str = "encode"
) -> str:
    """
    Encode or decode text using a Caesar cipher with a specified shift key.

    This function performs a classic Caesar cipher transformation on the
    provided text. It preserves non-alphabetic characters and maintains
    the original case of letters. The shift is applied modulo 26 to handle
    any integer value, including negative shifts.

    Args:
        text (str): The input string to be transformed.
        shift (int): The number of positions to shift each letter.
                     Default is 3. Can be any integer (positive, negative, or zero).
        mode (str): The operation mode. Must be either 'encode' or 'decode'.
                    Default is 'encode'.

    Returns:
        str: A formatted string containing the transformed text along with
             metadata about the operation (mode, shift, original length,
             and transformed length). If an error occurs, returns a descriptive
             error message string.

    Examples:
        >>> await caesar_cipher_vault("Hello, World!", shift=3, mode="encode")
        'Operation: encode | Shift: 3 | Input Length: 13 | Output Length: 13\nResult: Khoor, Zruog!'

        >>> await caesar_cipher_vault("Khoor, Zruog!", shift=3, mode="decode")
        'Operation: decode | Shift: 3 | Input Length: 13 | Output Length: 13\nResult: Hello, World!'
    """
    try:
        # Validate mode
        if mode not in ("encode", "decode"):
            return f"Error: Invalid mode '{mode}'. Must be either 'encode' or 'decode'."

        # Validate text type
        if not isinstance(text, str):
            return f"Error: Text must be a string, got {type(text).__name__}."

        # Normalize shift to be within 0-25 range
        normalized_shift = shift % 26

        # For decode, we shift in the opposite direction
        if mode == "decode":
            effective_shift = (-normalized_shift) % 26
        else:
            effective_shift = normalized_shift

        def transform_char(char: str) -> str:
            """Transform a single character based on the cipher rules."""
            if char.isalpha():
                # Determine the base ASCII value for the case
                base = ord('A') if char.isupper() else ord('a')
                # Shift the character
                shifted = (ord(char) - base + effective_shift) % 26
                return chr(base + shifted)
            else:
                # Non-alphabetic characters remain unchanged
                return char

        # Apply transformation to each character
        transformed_text = "".join(transform_char(c) for c in text)

        # Format the output with metadata
        result = (
            f"Operation: {mode} | "
            f"Shift: {shift} (effective: {effective_shift}) | "
            f"Input Length: {len(text)} | "
            f"Output Length: {len(transformed_text)}\n"
            f"Result: {transformed_text}"
        )

        return result

    except Exception as e:
        return f"Error: An unexpected error occurred during Caesar cipher operation: {str(e)}"


if __name__ == "__main__":
    import asyncio

    async def main():
        # Test encoding
        encoded = await caesar_cipher_vault("Hello, World!", shift=3, mode="encode")
        print("Encoded:", encoded)
        print()

        # Test decoding
        decoded = await caesar_cipher_vault("Khoor, Zruog!", shift=3, mode="decode")
        print("Decoded:", decoded)
        print()

        # Test with negative shift
        neg_encoded = await caesar_cipher_vault("Hello", shift=-1, mode="encode")
        print("Negative shift encode:", neg_encoded)
        print()

        # Test with invalid mode
        invalid = await caesar_cipher_vault("Hello", mode="invalid")
        print("Invalid mode:", invalid)

    asyncio.run(main())