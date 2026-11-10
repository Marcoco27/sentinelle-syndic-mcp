# /// script
# requires-python = ">=3.12"
# dependencies = ["x402[evm,mcp]>=2.27"]
# ///
"""Call a paid MCP tool of Sentinelle syndic and pay it with x402 (USDC on Base).

Usage:
    PRIVATE_KEY=0x... uv run examples/pay_mcp.py AA0581645            # syndic_lookup, 0.01 USDC
    PRIVATE_KEY=0x... uv run examples/pay_mcp.py --commune 44109      # syndic_echeances, 0.03 USDC

PRIVATE_KEY is the key of a wallet holding a little USDC on Base. Use a dedicated,
low-balance wallet: never your main one. A condominium lookup costs 0.01 USDC, an area list 0.03 USDC; no ETH is needed
for gas, the facilitator pays it.
"""
import asyncio
import os
import sys

from eth_account import Account
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from x402 import x402Client
from x402.mcp.client import x402MCPSession
from x402.mechanisms.evm.exact import ExactEvmClientScheme
from x402.mechanisms.evm.signers import EthAccountSigner

URL = "https://syndic.amacunia.fr/mcp"


async def main() -> None:
    if len(sys.argv) > 2 and sys.argv[1] == "--commune":
        tool, args = "syndic_echeances", {"commune": sys.argv[2], "type_syndic": "professionnel"}
    else:
        tool, args = "syndic_lookup", {"immatriculations": sys.argv[1] if len(sys.argv) > 1 else "AA0581645"}
    payer = x402Client()
    payer.register("eip155:8453", ExactEvmClientScheme(
        EthAccountSigner(Account.from_key(os.environ["PRIVATE_KEY"]))))

    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            mcp = x402MCPSession(session, payer)
            await mcp.initialize()
            result = await mcp.call_tool(tool, args)
            text = result.content[0].text if result.content else ""
            if result.is_error:
                print("Call refused (payment or input):", text[:400])
                return
            print("Settlement:", result.payment_response)
            print(text)


asyncio.run(main())
