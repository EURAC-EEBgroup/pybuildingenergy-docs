"""
mylib.core
Core module of the example library.
"""

def add(a: float, b: float) -> float:
    """
    Add two numbers.

    Args:
        a (float): First number.
        b (float): Second number.

    Returns:
        float: The sum of a and b.
    """
    return a + b


class Calculator:
    """Simple calculator class."""

    def multiply(self, x: float, y: float) -> float:
        """Return the product of x and y."""
        return x * y