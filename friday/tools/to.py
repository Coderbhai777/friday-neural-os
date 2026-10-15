"""
Dynamically Synthesized Tool for ULTRON: to
Created: 2026-10-05 13:26:16
Instruction: make a tool to calculate compound interest for savings
"""

import math

async def to(principal: float, rate: float, time: float, compounding_frequency: int = 1) -> str:
    """
    Calculate the compound interest for a savings account.

    Parameters:
        principal (float): The initial amount of money. Must be greater than 0.
        rate (float): The annual interest rate (as a decimal, e.g., 0.05 for 5%). Must be greater than or equal to 0.
        time (float): The time the money is invested for, in years. Must be greater than or equal to 0.
        compounding_frequency (int, optional): The number of times interest is compounded per year. Defaults to 1 (annual compounding).

    Returns:
        str: The final amount after compound interest, formatted as a string with 2 decimal places.

    Raises:
        ValueError: If any of the input parameters are invalid.
    """
    try:
        if principal <= 0:
            raise ValueError("Principal must be greater than 0.")
        if rate < 0:
            raise ValueError("Rate must be greater than or equal to 0.")
        if time < 0:
            raise ValueError("Time must be greater than or equal to 0.")
        if compounding_frequency <= 0:
            raise ValueError("Compounding frequency must be greater than 0.")
        
        # Calculate compound interest using the formula: A = P * (1 + r/n)^(nt)
        amount = principal * math.pow(1 + (rate / compounding_frequency), compounding_frequency * time)
        
        return f"{amount:.2f}"
    except Exception as e:
        return f"Error calculating compound interest: {str(e)}"