import json
from pyarrow import flight


if __name__ == "__main__":
    client = flight.FlightClient(
        location="grpc://localhost:8815",
    )

    ticket_payload = {
        "query": "MATCH (n) RETURN n",
        "graph": "flight",
    }

    ticket = flight.Ticket(
        json.dumps(ticket_payload).encode("utf-8")
    )

    client.do_get(ticket)

