from m365client.graph.analysis import analyze_response_schema


def test_analyze_response_schema():
    data = [
        {"name": "John", "age": 30, "active": False},
        {"name": "Jane", "age": 25, "active": True},
        {"name": "Bob", "age": 35, "active": True},
    ]
    schema = analyze_response_schema(data)
    assert schema == {"name": "str", "age": "int", "active": "bool"}
