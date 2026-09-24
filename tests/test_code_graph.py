"""
tests/test_code_graph.py

Unit tests for CodeGraph — Step 3 of the CLI pipeline.

Covers:
- Graph initialization
- Building nodes and edges from changed files data (Level 1 and Level 2)
- Testing get_related_functions retrieval
"""

import pytest
from unittest.mock import patch
from understanding_agent.code_graph import CodeGraph

def test_initialization():
    graph = CodeGraph()
    assert graph.nodes == {}
    assert graph.edges == []

@patch("understanding_agent.code_graph.CodeGraph._find_definition")
@patch("understanding_agent.code_graph.CodeGraph._get_calls_in_function")
def test_build_nodes_and_edges(mock_get_calls, mock_find_def):
    # Mock finding definition
    def fake_find_def(func_name):
        if func_name == "calculate_total":
            return "app/pricing_calculator.py"
        if func_name == "is_fraudulent_transaction":
            return "app/fraud_detector.py"
        if func_name == "apply_discount":
            return "app/discount_applicator.py"
        return None
    mock_find_def.side_effect = fake_find_def
    
    # Mock finding sub-calls (Level 2)
    def fake_get_calls(filepath, func_name):
        if func_name == "calculate_total":
            return ["apply_discount"]
        return []
    mock_get_calls.side_effect = fake_get_calls

    graph = CodeGraph()
    changed_files = [
        {
            "path": "app/cart_service.py",
            "changed_functions": [
                {
                    "name": "checkout",
                    "added_calls": ["calculate_total", "is_fraudulent_transaction"]
                }
            ]
        }
    ]
    
    graph.build(changed_files)
    
    # Check if nodes exist (Level 1)
    assert "file:app/cart_service.py" in graph.nodes
    assert "func:checkout" in graph.nodes
    assert "func:calculate_total" in graph.nodes
    assert "func:is_fraudulent_transaction" in graph.nodes
    
    # Check if Level 2 nodes were added
    assert "func:apply_discount" in graph.nodes
    assert "file:app/discount_applicator.py" in graph.nodes
    
    # Check edges
    edges = graph.edges
    assert {"source": "file:app/cart_service.py", "target": "func:checkout", "relation": "contains"} in edges
    assert {"source": "func:checkout", "target": "file:app/cart_service.py", "relation": "defined_in"} in edges
    assert {"source": "func:checkout", "target": "func:calculate_total", "relation": "calls"} in edges
    
    # Check Level 2 edges
    assert {"source": "func:calculate_total", "target": "func:apply_discount", "relation": "calls"} in edges
    assert {"source": "file:app/discount_applicator.py", "target": "func:apply_discount", "relation": "contains"} in edges

def test_get_related_functions():
    graph = CodeGraph()
    graph._add_node("func:main_func", "function", "main_func")
    graph._add_node("func:helper_1", "function", "helper_1")
    graph._add_edge("func:main_func", "func:helper_1", "calls")
    graph._add_edge("func:main_func", "func:helper_2", "calls")
    
    main_related = graph.get_related_functions("main_func")
    assert sorted(main_related) == ["helper_1", "helper_2"]
    
    nonexistent = graph.get_related_functions("fake_func")
    assert nonexistent == []
