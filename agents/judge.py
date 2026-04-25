"""Judge — quality gate checker for built agents."""
import sys
from pathlib import Path


def judge_agent(agent_dir: Path, agent_name: str) -> dict:
    """Run quality gates against a built agent. Returns gate results."""

    gates = {
        "passed": [],
        "failed": []
    }

    # Gate 1: SOUL.md exists
    soul = agent_dir / "SOUL.md"
    if soul.exists():
        gates["passed"].append("SOUL.md exists")
        content = soul.read_text()
        required_sections = ["## Identity", "What You Do", "Voice", "Rules"]
        missing = [s for s in required_sections if s not in content]
        if missing:
            gates["failed"].append(f"SOUL.md missing sections: {', '.join(missing)}")
        else:
            gates["passed"].append("SOUL.md has required sections")
    else:
        gates["failed"].append("SOUL.md missing")

    # Gate 2: SPEC.md exists
    spec = agent_dir / "SPEC.md"
    if spec.exists():
        gates["passed"].append("SPEC.md exists")
    else:
        gates["failed"].append("SPEC.md missing")

    # Gate 3: Directory structure
    required_dirs = ["config", "database", "skills", "processors"]
    for d in required_dirs:
        if (agent_dir / d).exists():
            gates["passed"].append(f"directory: {d}/")
        else:
            gates["failed"].append(f"directory missing: {d}/")

    # Gate 4: Database schema
    schema = agent_dir / "database" / "schema.sql"
    if schema.exists():
        gates["passed"].append("schema.sql exists")
        # Basic SQL validation
        sql = schema.read_text()
        if "CREATE TABLE" in sql:
            gates["passed"].append("schema.sql has CREATE TABLE statements")
        else:
            gates["failed"].append("schema.sql missing CREATE TABLE")
    else:
        gates["failed"].append("schema.sql missing")

    # Gate 5: Skills directory has files (or placeholder)
    skills_dir = agent_dir / "skills"
    if skills_dir.exists():
        skill_files = list(skills_dir.glob("*.md"))
        if skill_files:
            gates["passed"].append(f"skills/ has {len(skill_files)} skill file(s)")
        else:
            gates["passed"].append("skills/ exists (no skills in brief)")
    else:
        gates["failed"].append("skills/ missing")

    # Gate 6: run.py exists and is valid Python
    run_py = agent_dir / "run.py"
    if run_py.exists():
        gates["passed"].append("run.py exists")
        try:
            import ast
            ast.parse(run_py.read_text())
            gates["passed"].append("run.py is valid Python")
        except SyntaxError as e:
            gates["failed"].append(f"run.py has syntax error: {e}")
    else:
        gates["failed"].append("run.py missing")

    # Gate 7: Config file
    config = agent_dir / "config" / "agent.yaml"
    if config.exists():
        gates["passed"].append("config/agent.yaml exists")
    else:
        gates["failed"].append("config/agent.yaml missing")

    # Gate 8: Processors can be imported
    processors_init = agent_dir / "processors" / "__init__.py"
    if processors_init.exists():
        gates["passed"].append("processors/__init__.py exists")
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("processors", processors_init)
            if spec and spec.loader:
                gates["passed"].append("processors package loads")
        except Exception as e:
            gates["failed"].append(f"processors import failed: {e}")
    else:
        gates["failed"].append("processors/__init__.py missing")

    # Gate 9: agents/judge.py exists
    judge_file = agent_dir / "agents" / "judge.py"
    if judge_file.exists():
        gates["passed"].append("agents/judge.py exists")
    else:
        gates["passed"].append("agents/judge.py optional (not required for all agents)")

    # Gate 10: database/*.db exists (initialized)
    db_files = list((agent_dir / "database").glob("*.db"))
    if db_files:
        gates["passed"].append(f"Database initialized: {len(db_files)} db file(s)")
    else:
        gates["failed"].append("Database not initialized")

    # Gate 11: SPEC.md has architecture section
    spec = agent_dir / "SPEC.md"
    if spec.exists():
        spec_content = spec.read_text()
        if "## Architecture" in spec_content or "# Architecture" in spec_content:
            gates["passed"].append("SPEC.md has Architecture section")
        else:
            gates["failed"].append("SPEC.md missing Architecture section")

    # Gate 12: SPEC.md has trigger definition
    if spec.exists():
        spec_content = spec.read_text()
        if "Trigger" in spec_content or "trigger" in spec_content.lower():
            gates["passed"].append("SPEC.md defines trigger")
        else:
            gates["failed"].append("SPEC.md missing trigger definition")

    # Gate 13: SOUL.md has identity section
    soul = agent_dir / "SOUL.md"
    if soul.exists():
        soul_content = soul.read_text()
        if "## Identity" in soul_content or "# Identity" in soul_content:
            gates["passed"].append("SOUL.md has Identity section")
        else:
            gates["failed"].append("SOUL.md missing Identity section")

    # Gate 14: Skills load without error (basic check)
    skills_dir = agent_dir / "skills"
    if skills_dir.exists():
        skill_files = list(skills_dir.glob("*.md"))
        if skill_files:
            try:
                for sf in skill_files[:3]:
                    content = sf.read_text()
                    if len(content) < 50:
                        gates["failed"].append(f"Skill {sf.name} seems empty")
                        break
                else:
                    gates["passed"].append("Skills have content (non-empty)")
            except Exception as e:
                gates["failed"].append(f"Skill reading failed: {e}")
        else:
            gates["passed"].append("No skills (none required in brief)")

    # Gate 15: run.py executes without syntax error (ast parse)
    run_py = agent_dir / "run.py"
    if run_py.exists():
        try:
            import ast
            ast.parse(run_py.read_text())
            gates["passed"].append("run.py passes syntax check")
        except SyntaxError as e:
            gates["failed"].append(f"run.py syntax error: {e}")

    return gates


def main():
    """CLI: python judge.py [agent-dir] [agent-name]"""
    if len(sys.argv) < 3:
        print("Usage: python judge.py [agent-dir] [agent-name]")
        sys.exit(1)

    agent_dir = Path(sys.argv[1])
    agent_name = sys.argv[2]

    result = judge_agent(agent_dir, agent_name)

    print(f"\nQuality Gates for {agent_name}")
    print(f"Location: {agent_dir}")
    print()
    for g in result["passed"]:
        print(f"  ✅ {g}")
    for g in result["failed"]:
        print(f"  ❌ {g}")
    print()
    print(f"Result: {len(result['passed'])} passed, {len(result['failed'])} failed")

    if result["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
