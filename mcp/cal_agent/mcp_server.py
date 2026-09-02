from fastmcp import FastMCP

mcp = FastMCP("calculator mcp")


@mcp.tool
def addition(a: float, b: float) -> float | str:
    """Returns addition of two numbers."""
    try:
        print("using addition tool")
        return a + b
    except ArithmeticError as e:
        return str(e)


@mcp.tool
def subtraction(a: float, b: float) -> float | str:
    """Returns subtraction of two numbers."""
    try:
        print("using subtaction tool")
        return a - b
    except ArithmeticError as e:
        return str(e)


@mcp.tool
def multiplication(a: float, b: float) -> float | str:
    """Returns product of two numbers."""
    try:
        print("using multiplication tool")
        return a * b
    except ArithmeticError as e:
        return str(e)


@mcp.tool
def division(a: float, b: float) -> float | str:
    """Performs division on two numbers."""
    try:
        print("using divisoin tool")
        if b == 0:
            return "Error: Division by zero"
        return a / b
    except ArithmeticError as e:
        return str(e)


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
