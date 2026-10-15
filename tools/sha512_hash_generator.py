"""
Dynamically Synthesized Tool for ULTRON: sha512_hash_generator
Created: 2026-10-04 22:41:49
Instruction: Compute SHA-512 hex digest of any input string. Parameters: text: str. Returns formatted string with input text, hash length, and sha512 hex digest.
"""

import hashlib
from typing import Optional

async def sha512_hash_generator(text: str) -> str:
    """
    Compute the SHA-512 hex digest of the input string and return a formatted string.

    Args:
        text (str): The input string to be hashed.

    Returns:
        str: A formatted string containing the input text, hash length, and SHA-512 hex digest.

    Raises:
        ValueError: If the input string is empty or None.
        Exception: For any other unexpected errors.
    """
    try:
        if not text:
            raise ValueError("Input string cannot be empty or None.")

        # Compute SHA-512 hash
        sha512_hash = hashlib.sha512(text.encode()).hexdigest()

        # Format the output string
        formatted_output = (
            f"Input Text: {text}\n"
            f"SHA-512 Hash Length: {len(sha512_hash)}\n"
            f"SHA-512 Hex Digest: {sha512_hash}"
        )

        return formatted_output

    except ValueError as ve:
        return f"Error: {ve}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"