from pathlib import Path

from graphiti_cli.commands import project as project_module


def test_create_entity_set_enforces_extra_forbid(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    monkeypatch.setenv("MCP_GRAPHITI_REPO_PATH", str(repo_root))

    project_dir = tmp_path / "proj"
    graph_dir = project_dir / "ai" / "graph"
    graph_dir.mkdir(parents=True)
    config_path = graph_dir / "mcp-config.yaml"
    config_path.write_text(
        "services:\n"
        "  - id: test\n"
        "    group_id: test\n"
        "    entities_dir: entities\n"
    )

    project_module.create_entity_set("widget", project_dir)
    widget_file = graph_dir / "entities" / "Widget.py"
    content = widget_file.read_text()
    assert "ConfigDict" in content
    assert 'extra="forbid"' in content

    monkeypatch.setattr(project_module, "FILE_ENTITY_EXAMPLE", "missing_template.py")
    project_module.create_entity_set("gadget", project_dir)
    gadget_file = graph_dir / "entities" / "Gadget.py"
    content2 = gadget_file.read_text()
    assert "ConfigDict" in content2
    assert 'extra="forbid"' in content2
