"""File builder — creates directory structure for new agent."""
from pathlib import Path


def create_directory_structure(agent_name: str, output_dir: Path) -> list:
    """Create standard directory structure. Returns list of created paths."""

    paths = []

    dirs = [
        output_dir,
        output_dir / "config",
        output_dir / "database",
        output_dir / "skills",
        output_dir / "processors",
        output_dir / "agents",
        output_dir / "engine",
        output_dir / "templates",
        output_dir / "logs",
        output_dir / "memory",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        paths.append(str(d))

    # Create __init__.py files
    for subdir in ["processors", "agents", "engine"]:
        init_file = output_dir / subdir / "__init__.py"
        init_file.write_text(f'""" {agent_name} {subdir}. """\n')
        paths.append(str(init_file))

    # Create placeholder files
    (output_dir / "config" / "agent.yaml").write_text(
        f"# {agent_name} config\nagent_name: {agent_name}\n"
    )
    paths.append(str(output_dir / "config" / "agent.yaml"))

    return paths


if __name__ == "__main__":
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as tmpdir:
        result = create_directory_structure("TEST_AGENT", Path(tmpdir) / "test_agent")
        print(f"Created {len(result)} paths")
        for p in result:
            print(f"  {p}")
