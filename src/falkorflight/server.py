import json
from typing import (
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)

from falkordb import FalkorDB
from pyarrow import flight


class FalkorFlightServer(flight.FlightServerBase):
    """Apache Arrow Flight server for interacting with FalkorDB using OpenCypher."""

    def __init__(
        self,
        falkordb_host: str,
        falkordb_port: str,
        *,
        falkordb_username: Optional[str] = None,
        falkordb_password: Optional[str] = None,
        flight_host: str = "0.0.0.0",
        flight_port: str = "8815",
        tls: bool = False,
        verify_client: bool = False,
        tls_certificates: Optional[List[Tuple[str, str]]] = None,
        root_certificates: Optional[bytes] = None,
    ) -> None:

        scheme = "grpc+tcp"
        if tls:
            scheme = "grpc+tls"

        flight_url = f"{scheme}://{flight_host}:{flight_port}"

        super(FalkorFlightServer, self).__init__(
            location=flight_url,
            verify_client=verify_client,
            tls_certificates=tls_certificates,
            root_certificates=root_certificates,
        )

        self._falkordb_host = falkordb_host
        self._falkordb_port = falkordb_port
        self._falkordb_url = f"http://{falkordb_host}:{falkordb_port}"
        self._falkordb_username = falkordb_username
        self._falkordb_password = falkordb_password

        self._flight_host = flight_host
        self._flight_port = flight_port
        self._flight_url = flight_url
        self._tls = tls
        self._verify_client = verify_client
        self._tls_certificates = tls_certificates
        self._root_certificates = root_certificates

        # Apache Arrow Flight does not yet have support for asyncio, but
        # there is a tracking issue for this on the arrow GitHub repo:
        # https://github.com/apache/arrow/issues/34607
        self._falkordb_client = FalkorDB(
            host=falkordb_host,
            port=falkordb_port,
            username=falkordb_username,
            password=falkordb_password,
        )

    def do_action(
        self,
        context: flight.ServerCallContext,
        action: flight.Action,
    ) -> Iterable[bytes]:
        """Execute a custom command."""
        if action.type == "do_delete":
            self.do_delete_graph(action.body.to_pybytes().decode("utf-8"))
        else:
            raise ValueError(f"Unknown action: {action.type}")

    def do_get(
        self,
        context: flight.ServerCallContext,
        ticket: flight.Ticket,
    ) -> flight.FlightDataStream:
        """Perform an OpenCypher query on a FalkorDB graph."""

        payload = json.loads(ticket.ticket.decode("utf-8"))
        graph_name = payload["graph"]
        cypher_query = payload["query"]

        graph = self._falkordb_client.select_graph(graph_name)
        result = graph.query(cypher_query)

        print(result.header)

    def do_put(
        context: flight.ServerCallContext,
        descriptor: flight.FlightDescriptor,
        reader: flight.MetadataRecordBatchReader,
        writer: flight.FlightMetadataWriter,
    ) -> None:
        """Write data to a flight."""
        raise NotImplementedError

    def list_actions(
        self,
        context: flight.ServerCallContext,
    ) -> Union[Iterable[flight.ActionType], Tuple[str, str]]:
        """List custom actions available on this server."""
        return ("delete_graph", "Delete a graph from FalkorDB.")


    def do_delete_graph(self, graph_name: str) -> None:
        """Delete a graph from FalkorDB."""
        graph = self._falkordb_client.select_graph(graph_name)
        graph.query("MATCH (n) DETACH DELETE n")

