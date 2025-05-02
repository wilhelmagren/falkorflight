from src.falkorflight import FalkorFlightServer


if __name__ == "__main__":
    server = FalkorFlightServer(
        "r-6jissuruar.instance-9sb5dmc9t.hc-2uaqqpjgg.us-east-2.aws.f2e0a955bb84.cloud",
        "49708",
        tls=False,
        verify_client=False,
        falkordb_username="falkordb",
        falkordb_password="",
    )

    print("Running server on grpc+tcp://0.0.0.0:8815")
    server.serve()
