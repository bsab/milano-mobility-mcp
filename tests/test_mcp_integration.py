"""Smoke offline: vero client SDK, processo stdio, handshake e quattro chiamate."""

import asyncio
import json
from pathlib import Path
import sys
import sysconfig
import tempfile

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.parametrize("entrypoint", ["module", "console"])
def test_real_sdk_stdio_roundtrip(entrypoint):
    async def run():
        if entrypoint == "module":
            command = sys.executable
            args = ["-m", "milano_mobility_mcp"]
        else:
            name = "milano-mobility-mcp.exe" if sys.platform == "win32" else "milano-mobility-mcp"
            command = str(Path(sysconfig.get_path("scripts")) / name)
            args = []
        calls = {
            "check_vehicle_access": dict(
                vehicle=dict(category="M1", fuel="elettrico", euro_class=None,
                             exemptions="da_verificare", resident_in_milan=True),
                at="2026-09-08T12:00:00+02:00", area="area_b",
                inside_area_confirmed_by_user=True, destination="PRIVATE_TEST_MARKER",
            ),
            "get_active_smog_level": dict(territory="Comune di Milano"),
            "query_movein_allowance": dict(
                km_percorsi="100.1", soglia_annuale="100.4", distanza_viaggio="0.2",
            ),
            "get_daily_costs": dict(area="area_b", on_date="2026-09-08", tariff="ordinaria"),
        }
        with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as errors:
            params = StdioServerParameters(command=command, args=args)
            async with stdio_client(params, errlog=errors) as (read, write):
                async with ClientSession(read, write) as session:
                    initialized = await session.initialize()
                    assert initialized.serverInfo.name == "milano-mobility-mcp"
                    listed = await session.list_tools()
                    assert {tool.name for tool in listed.tools} == set(calls)
                    for tool in listed.tools:
                        assert tool.outputSchema
                        assert tool.annotations.readOnlyHint is True
                        assert tool.annotations.destructiveHint is False
                    for name, request in calls.items():
                        result = await session.call_tool(name, {"request": request})
                        assert result.isError is False, result
                        assert result.structuredContent is not None
                        data = result.structuredContent
                        assert data["decision"] == "non_determinabile"
                        assert data["reasons"]
                        assert data["source_checks"]
                        assert all(check["freshness"] == "reference_only" for check in data["source_checks"])
                        assert json.loads(result.content[0].text) == data
                        if name == "query_movein_allowance":
                            assert data["km_residui"] == "0.3"
                            assert data["authenticated_balance"] is False
                        elif name == "get_daily_costs":
                            assert data["ordinary_ticket_eur"] is None
                            assert data["total_due_eur"] is None
                        elif name == "get_active_smog_level":
                            assert data["active_level"] is None
                            assert data["last_checked"] is None
                    invalid = await session.call_tool("query_movein_allowance", {"request": {
                        "km_percorsi": "NaN", "soglia_annuale": "100", "distanza_viaggio": "1",
                    }})
                    assert invalid.isError is True
                    still_alive = await session.list_tools()
                    assert len(still_alive.tools) == 4
            errors.seek(0)
            assert "PRIVATE_TEST_MARKER" not in errors.read()

    asyncio.run(asyncio.wait_for(run(), timeout=45))
