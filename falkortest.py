import os
from falkordb import FalkorDB


if __name__ == "__main__":
    client = FalkorDB(
        host="r-6jissuruar.instance-9sb5dmc9t.hc-2uaqqpjgg.us-east-2.aws.f2e0a955bb84.cloud",
        port="49708",
        username="falkordb",
        password=os.environ.get("FALKOR_PASS", None),
    )

    graph = client.select_graph("flight")

    graph.query(
        "MATCH (n) DETACH DELETE n",
    )

    queries = [
        "CREATE (:Person {name: 'Alice', age: 25})",
        "CREATE (:Person {name: 'Bob', age: 30})",
        "CREATE (:Person {name: 'Charlie', age: 18})",
    ]

    for q in queries:
        graph.query(q)

    rqs = [
        "MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'}) CREATE (a)-[:FRIEND_OF {since: 2015}]->(b)",
        "MATCH (a:Person {name: 'Bob'}), (b:Person {name: 'Charlie'}) CREATE (a)-[:FRIEND_OF {since: 1998}]->(b)",
    ]

    for rq in rqs:
        graph.query(rq)

    result = graph.query(
        "MATCH (p:Person) RETURN p.name, p.age",
    )

    cols = [h[1] for h in result.header]
    print(cols)

    print(result.header)
    print(result.result_set)
