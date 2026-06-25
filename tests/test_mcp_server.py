# Copyright 2024-2026 HUMMBL, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for base120.mcp_server — JSON-RPC 2.0 handler logic.

Tests the handler layer directly (no stdin/stdout required).
"""

from __future__ import annotations

import json

import pytest

from base120.mcp_server import Base120Server


@pytest.fixture
def server() -> Base120Server:
    return Base120Server()


# ---------------------------------------------------------------------------
# initialize
# ---------------------------------------------------------------------------

class TestInitialize:
    def test_returns_server_info(self, server: Base120Server):
        result = server.handle_initialize({})
        assert "serverInfo" in result
        assert result["serverInfo"]["name"] == "base120"

    def test_returns_capabilities(self, server: Base120Server):
        result = server.handle_initialize({})
        assert "capabilities" in result

    def test_version_present(self, server: Base120Server):
        result = server.handle_initialize({})
        assert result["serverInfo"]["version"]


# ---------------------------------------------------------------------------
# tools/list
# ---------------------------------------------------------------------------

class TestToolsList:
    def test_returns_tools_key(self, server: Base120Server):
        result = server.handle_tools_list({})
        assert "tools" in result

    def test_exactly_six_tools(self, server: Base120Server):
        tools = server.handle_tools_list({})["tools"]
        assert len(tools) == 6

    def test_tool_names(self, server: Base120Server):
        names = {t["name"] for t in server.handle_tools_list({})["tools"]}
        assert names == {
            "base120_get",
            "base120_list",
            "base120_families",
            "base120_prompt",
            "base120_select",
            "base120_record",
        }

    def test_each_tool_has_description_and_schema(self, server: Base120Server):
        for tool in server.handle_tools_list({})["tools"]:
            assert tool.get("description"), f"{tool['name']} missing description"
            assert "inputSchema" in tool, f"{tool['name']} missing inputSchema"

    def test_input_schema_type_object(self, server: Base120Server):
        for tool in server.handle_tools_list({})["tools"]:
            assert tool["inputSchema"]["type"] == "object"


# ---------------------------------------------------------------------------
# tools/call — base120_get
# ---------------------------------------------------------------------------

class TestCallGet:
    def test_valid_code_returns_operator(self, server: Base120Server):
        result = server.handle_tools_call("base120_get", {"code": "P6"})
        assert not result.get("isError")
        text = result["content"][0]["text"]
        obj = json.loads(text)
        assert obj["code"] == "P6"
        assert obj["transformation"] == "P"

    def test_all_four_operator_fields(self, server: Base120Server):
        result = server.handle_tools_call("base120_get", {"code": "DE1"})
        obj = json.loads(result["content"][0]["text"])
        assert set(obj.keys()) >= {"code", "name", "transformation", "definition"}

    def test_invalid_code_returns_error(self, server: Base120Server):
        result = server.handle_tools_call("base120_get", {"code": "XX99"})
        assert result.get("isError") is True

    def test_missing_code_param_returns_error(self, server: Base120Server):
        result = server.handle_tools_call("base120_get", {})
        assert result.get("isError") is True


# ---------------------------------------------------------------------------
# tools/call — base120_list
# ---------------------------------------------------------------------------

class TestCallList:
    def test_no_family_returns_120(self, server: Base120Server):
        result = server.handle_tools_call("base120_list", {})
        ops = json.loads(result["content"][0]["text"])
        assert len(ops) == 120

    def test_family_filter_returns_20(self, server: Base120Server):
        result = server.handle_tools_call("base120_list", {"family": "DE"})
        ops = json.loads(result["content"][0]["text"])
        assert len(ops) == 20
        assert all(op["transformation"] == "DE" for op in ops)

    def test_unknown_family_returns_empty(self, server: Base120Server):
        result = server.handle_tools_call("base120_list", {"family": "ZZ"})
        ops = json.loads(result["content"][0]["text"])
        assert ops == []

    def test_case_insensitive_family(self, server: Base120Server):
        lower = server.handle_tools_call("base120_list", {"family": "de"})
        upper = server.handle_tools_call("base120_list", {"family": "DE"})
        assert lower["content"][0]["text"] == upper["content"][0]["text"]


# ---------------------------------------------------------------------------
# tools/call — base120_families
# ---------------------------------------------------------------------------

class TestCallFamilies:
    def test_returns_six_families(self, server: Base120Server):
        result = server.handle_tools_call("base120_families", {})
        fams = json.loads(result["content"][0]["text"])
        assert len(fams) == 6

    def test_canonical_order(self, server: Base120Server):
        result = server.handle_tools_call("base120_families", {})
        fams = json.loads(result["content"][0]["text"])
        assert fams == ["P", "IN", "CO", "DE", "RE", "SY"]


# ---------------------------------------------------------------------------
# tools/call — base120_prompt
# ---------------------------------------------------------------------------

class TestCallPrompt:
    def test_valid_code_returns_prompt(self, server: Base120Server):
        result = server.handle_tools_call("base120_prompt", {"code": "P6", "problem": "test"})
        assert not result.get("isError")
        text = result["content"][0]["text"]
        assert "P6" in text
        assert "test" in text

    def test_prompt_contains_recommendation_key(self, server: Base120Server):
        result = server.handle_tools_call("base120_prompt", {"code": "DE1", "problem": "what?"})
        text = result["content"][0]["text"]
        assert "recommendation" in text

    def test_invalid_code_returns_error(self, server: Base120Server):
        result = server.handle_tools_call("base120_prompt", {"code": "ZZ9", "problem": "?"})
        assert result.get("isError") is True

    def test_missing_problem_returns_error(self, server: Base120Server):
        result = server.handle_tools_call("base120_prompt", {"code": "P6"})
        assert result.get("isError") is True


# ---------------------------------------------------------------------------
# tools/call — base120_select
# ---------------------------------------------------------------------------

class TestCallSelect:
    def test_returns_list(self, server: Base120Server):
        result = server.handle_tools_call("base120_select", {"problem": "root cause analysis"})
        assert not result.get("isError")
        items = json.loads(result["content"][0]["text"])
        assert isinstance(items, list)

    def test_default_5_results(self, server: Base120Server):
        result = server.handle_tools_call("base120_select", {"problem": "governance"})
        items = json.loads(result["content"][0]["text"])
        assert len(items) == 5

    def test_custom_n(self, server: Base120Server):
        result = server.handle_tools_call("base120_select", {"problem": "risk", "n": 3})
        items = json.loads(result["content"][0]["text"])
        assert len(items) == 3

    def test_each_item_has_code_name_score(self, server: Base120Server):
        result = server.handle_tools_call("base120_select", {"problem": "stakeholder"})
        for item in json.loads(result["content"][0]["text"]):
            assert "code" in item and "name" in item and "score" in item

    def test_missing_problem_returns_error(self, server: Base120Server):
        result = server.handle_tools_call("base120_select", {})
        assert result.get("isError") is True


# ---------------------------------------------------------------------------
# tools/call — base120_record
# ---------------------------------------------------------------------------

class TestCallRecord:
    def test_valid_call_returns_result(self, server: Base120Server):
        result = server.handle_tools_call("base120_record", {
            "code": "P6",
            "problem": "how to price?",
            "recommendation": "anchor to compliance POV",
            "confidence": 0.85,
        })
        assert not result.get("isError")
        obj = json.loads(result["content"][0]["text"])
        assert obj["code"] == "P6"
        assert obj["confidence"] == 0.85
        assert "evidence_id" in obj
        assert "tuple" in obj

    def test_tuple_has_verum_fields(self, server: Base120Server):
        result = server.handle_tools_call("base120_record", {
            "code": "DE1",
            "problem": "root?",
            "recommendation": "5 whys",
            "confidence": 0.9,
        })
        obj = json.loads(result["content"][0]["text"])
        t = obj["tuple"]
        assert set(t.keys()) == {"id", "time", "state", "drift"}
        assert t["id"] == "DE1"
        assert abs(t["drift"] - 0.1) < 1e-5

    def test_invalid_code_returns_error(self, server: Base120Server):
        result = server.handle_tools_call("base120_record", {
            "code": "ZZ9", "problem": "?", "recommendation": "x", "confidence": 0.5,
        })
        assert result.get("isError") is True

    def test_confidence_out_of_range_returns_error(self, server: Base120Server):
        result = server.handle_tools_call("base120_record", {
            "code": "P6", "problem": "?", "recommendation": "x", "confidence": 1.5,
        })
        assert result.get("isError") is True

    def test_missing_required_param_returns_error(self, server: Base120Server):
        result = server.handle_tools_call("base120_record", {"code": "P6"})
        assert result.get("isError") is True


# ---------------------------------------------------------------------------
# Unknown tool
# ---------------------------------------------------------------------------

class TestUnknownTool:
    def test_unknown_tool_returns_error(self, server: Base120Server):
        result = server.handle_tools_call("not_a_tool", {})
        assert result.get("isError") is True


# ---------------------------------------------------------------------------
# dispatch() — JSON-RPC routing
# ---------------------------------------------------------------------------

class TestDispatch:
    def test_initialize_routes_correctly(self, server: Base120Server):
        req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        resp = server.dispatch(req)
        assert resp["id"] == 1
        assert "result" in resp
        assert "serverInfo" in resp["result"]

    def test_tools_list_routes_correctly(self, server: Base120Server):
        req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        resp = server.dispatch(req)
        assert "result" in resp
        assert "tools" in resp["result"]

    def test_tools_call_routes_correctly(self, server: Base120Server):
        req = {
            "jsonrpc": "2.0", "id": 3,
            "method": "tools/call",
            "params": {"name": "base120_families", "arguments": {}},
        }
        resp = server.dispatch(req)
        assert "result" in resp

    def test_notifications_return_none(self, server: Base120Server):
        # Notifications have no id — no response expected
        req = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        resp = server.dispatch(req)
        assert resp is None

    def test_unknown_method_returns_error(self, server: Base120Server):
        req = {"jsonrpc": "2.0", "id": 4, "method": "unknown/method", "params": {}}
        resp = server.dispatch(req)
        assert "error" in resp
        assert resp["error"]["code"] == -32601  # Method not found
