from langchain_core.tools import tool

@tool("add", return_direct=False)
def add(a: float, b: float) -> float:
    """Addition de deux nombres."""
    return a + b

@tool("multiply", return_direct=False)
def multiply(a: float, b: float) -> float:
    """Multiplication de deux nombres."""
    return a * b

@tool("divide", return_direct=False)
def divide(a: float, b: float) -> float:
    """Division de deux nombres (lance une erreur si b=0)."""
    if b == 0:
        raise ValueError("Division par zéro interdite.")
    return a / b
