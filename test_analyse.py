import types
from analyse import analyse_query


class MockResponse:
    def __init__(self):
        self.choices = [
            types.SimpleNamespace(
                message=types.SimpleNamespace(content='{"mock": "response"}')
            )
        ]


def test_analyse_query(monkeypatch):

    def mock_create(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        "analyse.client.chat.completions.create",
        mock_create
    )

    result = analyse_query("Test message")

    assert result == '{"mock": "response"}'
