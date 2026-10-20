"""Controleert dat ClaudeLLM een geldige request opbouwt en het antwoord parseert,
zonder echte API-call (transport wordt gemockt)."""

import json

import anthropic
import httpx2

from hvac_agent.checklists import load_checklists
from hvac_agent.config import ROOT
from hvac_agent.llm.claude import ClaudeLLM


def make_llm(answer: dict, captured: list):
    def handler(request: httpx2.Request) -> httpx2.Response:
        captured.append(json.loads(request.content))
        return httpx2.Response(200, json={
            "id": "msg_test", "type": "message", "role": "assistant", "model": "claude-opus-5-5",
            "content": [{"type": "text", "text": json.dumps(answer)}],
            "stop_reason": "end_turn", "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 10},
        })

    client = anthropic.Anthropic(api_key="test", http_client=httpx2.Client(transport=httpx2.MockTransport(handler)))
    return ClaudeLLM("claude-opus-5-5", client=client)


def test_analyze_photo_sends_image_and_schema():
    captured = []
    llm = make_llm({
        "matched_item_key": "foto_typeplaatje_buitenunit", "is_usable": True, "issue": None,
        "extracted": [{"name": "serienummer", "value": "SN123"}],
    }, captured)
    items = load_checklists(ROOT / "config" / "checklists")["warmtepomp_installatie"].items
    result = llm.analyze_photo(b"jpeg", "image/jpeg", "typeplaatje", items)

    assert result.extracted[0].value == "SN123"
    body = captured[0]
    assert body["model"] == "claude-opus-5-5"
    assert body["messages"][0]["content"][0]["type"] == "image"
    assert body["output_config"]["format"]["type"] == "json_schema"
