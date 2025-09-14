import os, json
from typing import List, Dict, Optional
from .llm import LLM
from . import rag

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

try:
    from mcp.client.session import ClientSession
    from mcp.transport.http import HTTPClientTransport
    HAVE_MCP = True
except Exception:
    HAVE_MCP = False

SYSTEM_PROMPT = (
    "You are an enterprise assistant with access to a knowledge base. "
    "When responding to questions, ALWAYS use the provided CONTEXT section to answer questions about documents. "
    "If CONTEXT is provided, base your answer primarily on that information. "
    "If tools are available and needed, you may request a tool call by emitting a JSON object on a single line: "
    '{"tool":"calc","input":{"expression":"2+2"}} or {"tool":"ping","input":{}}. '
    "Otherwise, answer directly and be concise."
)

class Agent:
    def __init__(self):
        self.llm = LLM()
        self.history: List[Dict[str, str]] = [{"role":"system","content":SYSTEM_PROMPT}]

    async def maybe_call_mcp(self, tool: str, tool_input: Dict) -> Optional[str]:
        if not (HAVE_MCP and MCP_SERVER_URL):
            return None
        async with HTTPClientTransport(MCP_SERVER_URL) as transport:
            async with ClientSession(transport) as session:
                await session.initialize()
                result = await session.call_tool(tool, tool_input)
                return json.dumps(result)

    async def chat(self, user_msg: str) -> str:
        contexts = await rag.retrieve(user_msg, n=4)
        ctx_text = "\n\n".join([c["text"] for c in contexts])
        ctx_block = f"\n\nCONTEXT:\n{ctx_text}\n\n"

        self.history.append({"role":"user","content": user_msg + ctx_block})
        reply = await self.llm.chat(self.history)
        self.history.append({"role":"assistant","content": reply})

        if reply.strip().startswith("{") and reply.strip().endswith("}"):
            try:
                obj = json.loads(reply.strip())
                if "tool" in obj and "input" in obj:
                    tool_name = obj["tool"]
                    tool_input = obj["input"]
                    tool_resp = await self.maybe_call_mcp(tool_name, tool_input) or "Tool unavailable"
                    self.history.append({"role":"user","content": f"Tool result: {tool_resp}"})
                    final = await self.llm.chat(self.history)
                    self.history.append({"role":"assistant","content": final})
                    return final
            except Exception:
                pass
        return reply
