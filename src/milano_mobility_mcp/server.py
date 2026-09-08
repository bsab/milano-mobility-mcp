"""Entry point MCP stdio: nessun banner o log degli input su stdout."""

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .adapters import UnavailableSmogAdapter
from .models import (
    AccessRequest, AccessResult, CostsRequest, CostsResult, MoveInRequest,
    MoveInResult, SmogRequest, SmogResult,
)
from .service import MobilityService, calculate_movein
from .sources import MOVEIN_SOURCE_CHECKS, PUBLIC_SNAPSHOT, SMOG_REFERENCE_URLS, SMOG_SOURCE_CHECKS


def create_server() -> FastMCP:
    service = MobilityService(
        PUBLIC_SNAPSHOT, UnavailableSmogAdapter(SMOG_REFERENCE_URLS, SMOG_SOURCE_CHECKS),
    )
    server = FastMCP(
        "milano-mobility-mcp",
        instructions=(
            "Informazioni parziali, non consulenza legale o autorizzazione. "
            "Non interpretare non_determinabile, null o budget residuo come via libera. "
            "Mostrare sempre motivazioni, fonti, freschezza e limiti."
        ),
        log_level="CRITICAL",
    )
    annotations = ToolAnnotations(
        readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False,
    )

    @server.tool(annotations=annotations, structured_output=True)
    def check_vehicle_access(request: AccessRequest) -> AccessResult:
        """Profilo/perimetro dichiarati, ora Europe/Rome: nessun divieto abilitato nel catalogo attuale."""
        return service.check_vehicle_access(request)

    @server.tool(annotations=annotations, structured_output=True)
    def get_active_smog_level(request: SmogRequest) -> SmogResult:
        """Stato antismog: adapter non live, restituisce onestamente livello e validità sconosciuti."""
        return service.get_active_smog_level(request)

    @server.tool(annotations=annotations, structured_output=True)
    def query_movein_allowance(request: MoveInRequest) -> MoveInResult:
        """Sottrae km dichiarati con Decimal; NON saldo autenticato né autorizzazione alla circolazione."""
        return calculate_movein(request, MOVEIN_SOURCE_CHECKS)

    @server.tool(annotations=annotations, structured_output=True)
    def get_daily_costs(request: CostsRequest) -> CostsResult:
        """Nessuna tariffa/scadenza abilitata nel catalogo attuale: importi null, mai zero implicito."""
        return service.get_daily_costs(request)

    return server


def main() -> None:
    create_server().run(transport="stdio")
