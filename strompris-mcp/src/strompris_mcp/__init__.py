import datetime
from typing import Literal

import httpx
from mcp.server.mcpserver import MCPServer

API_URL = (
    "https://www.hvakosterstrommen.no/api/v1/prices/{date:%Y}/{date:%m-%d}_{area}.json"
)

mcp = MCPServer("strompris")


@mcp.tool()
async def get_electricity_price(
    date: datetime.date, area: Literal["NO1", "NO2", "NO3", "NO4", "NO5"]
) -> list[dict]:
    """Get Norwegian spot electricity prices for one day and price area.

    Areas: NO1 Oslo/East, NO2 Kristiansand/South, NO3 Trondheim/Central,
    NO4 Tromsø/North, NO5 Bergen/West. Returns one entry per period with
    NOK_per_kWh, EUR_per_kWh, EXR (exchange rate), time_start and time_end.
    Prices exclude VAT and grid fees.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(API_URL.format(date=date, area=area))
    # Next-day prices are published around 13:00 Europe/Oslo, so a 404 usually means "not yet".
    if response.status_code == 404:
        raise ValueError(
            f"No prices published for {date} in {area}. Prices for the next day "
            "appear around 13:00 Europe/Oslo; earlier dates are always available."
        )
    response.raise_for_status()
    return response.json()


def main() -> None:
    mcp.run()
