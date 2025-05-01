import json
from typing import (
    List,
    Optional,
    Tuple,
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
        flight_host: str = "0.0.0.0",
        flight_port: str = "8815",
        tls: bool = True,
        verify_client: bool = True,
        tls_certificates: Optional[List[Tuple[str, str]]] = None,
        root_certificates: Optional[bytes] = None,
    ) -> None:

        scheme = "grpc+tcp"
        if tls:
            scheme = "grpc+tls"

        flight_url = f"{scheme}://{flight_host}:{flight_port}",

        super(FalkorFlightServer, self).__init__(
            location=flight_url,
            verify_client=verify_client,
            tls_certificates=tls_certificates,
            root_certificates=root_certificates,
        )

        self._falkordb_host = falkordb_host
        self._falkordb_port = falkordb_port
        self._falkordb_url = f"http://{falkordb_host}:{falkordb_port}"

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
        #
        # Also, FalkorDB has support for authentication using password or ssl_certs
        # maybe should think about using those if possible?
        self._falkordb_client = FalkorDB(host=falkordb_host, port=falkordb_port)

    def do_get(
        self,
        context: flight.ServerCallContext,
        ticket: flight.Ticket,
    ) -> flight.FlightDataStream:
        """Perform an OpenCypher on a FalkorDB graph."""

        payload = json.loads(ticket.ticket.decode("utf-8"))
        graph_name = payload["graph"]
        cypher_query = payload["query"]

        g = self._falkordb_client.select_graph(graph_name)
        result = g.query(cypher_query)

        # TODO: process result and return to user
