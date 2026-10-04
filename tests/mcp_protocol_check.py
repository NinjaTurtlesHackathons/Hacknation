"""Protokoll-Test über echtes stdio (Ersatz für den interaktiven MCP-Inspector):
  python tests/mcp_protocol_check.py [befehl ...]   (Default: python -m asd.mcp_server)"""
import asyncio, json, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main(cmd):
    params = StdioServerParameters(command=cmd[0], args=cmd[1:], env=dict(os.environ))
    async with stdio_client(params) as (r, w), ClientSession(r, w) as s:
        info = await s.initialize()
        print("server:", info.serverInfo.name, info.serverInfo.version)
        print("tools:", [t.name for t in (await s.list_tools()).tools])
        print("resources:", [str(x.uri) for x in (await s.list_resources()).resources])
        print("resource templates:", [x.uriTemplate for x in (await s.list_resource_templates()).resourceTemplates])
        print("prompts:", [p.name for p in (await s.list_prompts()).prompts])
        res = await s.call_tool("list_domains", {})
        print("list_domains ->", res.content[0].text[:200].replace("\n", " "))
        g = await s.read_resource("probatum://guide"); print("guide ->", g.contents[0].text[:80].replace("\n", " "))
        if VOLL:                                             # Ende-zu-Ende: Selbsttest, bestätigter und abgelehnter Claim
            call = lambda n, a: s.call_tool(n, a)
            print("selftest ->", (await call("selftest", {"domain": "proofreading"})).content[0].text.replace("\n", " ")[:160])
            P = {"bind+": 5.345, "bind-": 9.248, "akt0+": -1.038, "verw1+": 3.299, "verw1-": 5.857, "prod+": -7.902, "mu": 10.212, "muP": 0.0}
            for eta_max in (1e-3, 1e-6):
                r = await call("submit_claim", {"domain": "proofreading", "claim": {"typ": "erreichbar", "topologie": "hopfield_n1", "params": P, "eta_max": eta_max}})
                print(f"submit_claim eta_max={eta_max} ->", r.content[0].text.replace("\n", " ")[:220])


VOLL = "--voll" in sys.argv
asyncio.run(main([a for a in sys.argv[1:] if a != "--voll"] or [sys.executable, "-m", "asd.mcp_server"]))
