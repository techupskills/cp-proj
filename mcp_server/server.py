"""FastMCP demo server for the capstone (streamable HTTP)."""
import os
from mcp.server.fastmcp import FastMCP

SERVICE_NAME = os.getenv("MCP_SERVICE_NAME", "CapstoneMCP")
BIND_HOST = os.getenv("MCP_HOST", "0.0.0.0")
BIND_PORT = int(os.getenv("MCP_PORT", "8000"))

server = FastMCP()

@server.tool()
def calc(expression: str):
    """Evaluate a basic arithmetic expression like '2+2*3'."""
    try:
        allowed = set("0123456789+-*/(). ")
        if not set(expression) <= allowed:
            return {"error":"invalid characters"}
        return {"expression": expression, "result": eval(expression)}
    except Exception as e:
        return {"error": str(e)}

@server.tool()
def ping():
    return {"pong": True}

@server.tool()
def whoami():
    return {"service": SERVICE_NAME}

if __name__ == "__main__":
    server.run(transport="streamable-http")
