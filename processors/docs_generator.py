"""
BROCK Documentation Generator
Auto-generates README.md, API.md, USAGE.md from a built agent.

Usage:
    python3 processors/docs_generator.py AGENT_NAME
"""

import sys
import re
import ast
from pathlib import Path
from datetime import datetime

def extract_functions_from_file(file_path: Path) -> list:
    """Extract function names, args, and docstrings from a Python file."""
    if not file_path.exists():
        return []
    try:
        tree = ast.parse(file_path.read_text())
    except Exception:
        return []
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node) or ""
            args = [a.arg for a in node.args.args]
            functions.append({
                "name": node.name,
                "args": args,
                "docstring": docstring.strip()[:200],
                "line": node.lineno
            })
    return functions


def extract_skills(agent_dir: Path) -> list:
    """Extract skill names and purposes from skill files."""
    skills_dir = agent_dir / "skills"
    if not skills_dir.exists():
        return []
    skills = []
    for f in skills_dir.glob("*.md"):
        content = f.read_text()
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        name = title_match.group(1).strip() if title_match else f.stem
        purpose_match = re.search(r'\*\*Purpose:\*\* (.+)', content)
        purpose = purpose_match.group(1).strip() if purpose_match else ""
        skills.append({"name": name, "file": f.name, "purpose": purpose})
    return skills


def generate_readme(agent_name: str, agent_dir: Path, spec_content: str = "") -> str:
    """Generate README.md for an agent."""
    domain = ""
    trigger = ""
    if spec_content:
        dm = re.search(r'\*\*Domain:\*\* (.+)', spec_content)
        if dm: domain = dm.group(1).strip()
        tr = re.search(r'\*\*Trigger:\*\* (.+)', spec_content)
        if tr: trigger = tr.group(1).strip()

    readme = "# %s\n\n" % agent_name
    readme += "**Built by:** BROCK\n"
    readme += "**Date:** %s\n\n" % datetime.now().strftime('%Y-%m-%d')
    readme += "## What It Does\n\n"
    readme += "%s\n\n" % (domain or "AI agent -- see SPEC.md for full details.")
    readme += "**Trigger:** %s\n\n" % (trigger or "On-demand")
    readme += "---\n\n"
    readme += "## Quick Start\n\n"
    readme += "```\ncd ~/.hermes/agents/%s\npython3 run.py\n```\n\n" % agent_name
    readme += "---\n\n"
    readme += "## Architecture\n\n"
    readme += "```\n%s/\n├── SOUL.md          <- Identity + rules\n├── SPEC.md          <- Architecture + workflow\n├── run.py           <- Entry point\n├── processors/      <- Business logic\n├── skills/          <- Domain knowledge\n├── database/        <- SQLite schema + data\n└── agents/          <- Sub-agents (judge, etc.)\n```\n\n" % agent_name
    readme += "---\n\n"
    readme += "## Available Skills\n\n"
    skills = extract_skills(agent_dir)
    if skills:
        for s in skills:
            readme += "- **%s** -- %s\n" % (s['name'], s['purpose'])
    else:
        readme += "_No custom skills defined._\n"
    readme += "\n---\n\n"
    readme += "## Processors\n\n"
    processors_dir = agent_dir / "processors"
    if processors_dir.exists():
        for f in sorted(processors_dir.glob("*.py")):
            if f.name.startswith("_"):
                continue
            funcs = extract_functions_from_file(f)
            if funcs:
                readme += "### %s\n" % f.stem
                for fn in funcs[:5]:
                    args_str = ", ".join(fn['args'])
                    readme += "- `%s(%s)`" % (fn['name'], args_str)
                    if fn['docstring']:
                        readme += " -- %s" % fn['docstring'][:80]
                    readme += "\n"
                readme += "\n"
    readme += "---\n\n"
    readme += "## Configuration\n\n"
    readme += "Environment variables required (store in vault, not in code):\n"
    readme += "- Any API keys or tokens used by this agent\n\n"
    readme += "---\n\n"
    readme += "## For Developers\n\n"
    readme += "See `API.md` for full processor documentation.\n"
    readme += "See `USAGE.md` for step-by-step usage guide.\n\n"
    readme += "_Maintained by BROCK. Update skills in the `skills/` directory._\n"
    return readme


def generate_api_md(agent_name: str, agent_dir: Path) -> str:
    """Generate API.md documenting all processors."""
    api = "# %s -- API Reference\n\n" % agent_name
    api += "**Generated:** %s\n\n" % datetime.now().strftime('%Y-%m-%d')
    api += "---\n\n"
    api += "## Processors\n\n"
    processors_dir = agent_dir / "processors"
    if not processors_dir.exists():
        return api + "_No processors directory found._\n"
    for f in sorted(processors_dir.glob("*.py")):
        if f.name.startswith("_"):
            continue
        api += "## %s.py\n\n" % f.stem
        funcs = extract_functions_from_file(f)
        if not funcs:
            api += "_No documented functions._\n\n"
            continue
        for fn in funcs:
            api += "### `%s`\n\n" % fn['name']
            args_str = ", ".join(["`%s`" % a for a in fn['args']])
            api += "**Args:** %s\n\n" % args_str
            if fn['docstring']:
                api += "%s\n\n" % fn['docstring']
            else:
                api += "_No docstring._\n\n"
    api += "---\n\n"
    api += "## Skills\n\n"
    skills = extract_skills(agent_dir)
    if skills:
        for s in skills:
            api += "### %s\n" % s['name']
            api += "**File:** `%s`\n" % s['file']
            api += "**Purpose:** %s\n\n" % s['purpose']
    else:
        api += "_No skills defined._\n"
    return api


def generate_usage_md(agent_name: str, agent_dir: Path, spec_content: str = "") -> str:
    """Generate USAGE.md step-by-step guide."""
    trigger = ""
    if spec_content:
        tr = re.search(r'\*\*Trigger:\*\* (.+)', spec_content)
        if tr: trigger = tr.group(1).strip()
    trigger = trigger or "On-demand"

    usage = "# %s -- Usage Guide\n\n" % agent_name
    usage += "**Last updated:** %s\n\n" % datetime.now().strftime('%Y-%m-%d')
    usage += "---\n\n"
    usage += "## Running the Agent\n\n"
    usage += "### Basic (on-demand)\n"
    usage += "```\npython3 run.py\n```\n\n"
    usage += "### With arguments\n"
    usage += "```\npython3 run.py --task \"your task here\"\n```\n\n"
    usage += "---\n\n"
    usage += "## Trigger Configuration\n\n"
    usage += "**Current trigger:** %s\n\n" % trigger
    usage += "To change the trigger, update `SPEC.md` and rebuild, or modify `run.py` directly.\n\n"
    usage += "---\n\n"
    usage += "## Common Tasks\n\n"
    usage += "### 1. Check agent status\n"
    usage += "```\npython3 run.py --status\n```\n\n"
    usage += "### 2. Run with specific input\n"
    usage += "```\npython3 run.py --input '{\"key\": \"value\"}'\n```\n\n"
    usage += "---\n\n"
    usage += "## Updating Skills\n\n"
    usage += "Skills are in the `skills/` directory. Edit the `.md` files directly -- no rebuild needed.\n\n"
    usage += "1. Open `skills/[skill-name].md`\n"
    usage += "2. Update the content\n"
    usage += "3. Restart the agent (or reload if using dynamic loading)\n\n"
    usage += "---\n\n"
    usage += "## Monitoring\n\n"
    usage += "- Check logs in `logs/` directory\n"
    usage += "- Database at `database/%s.db`\n" % agent_name.lower().replace("-", "_")
    usage += "- Run monitoring: `python3 processors/monitor.py` (if available)\n\n"
    usage += "---\n\n"
    usage += "## Troubleshooting\n\n"
    usage += "| Problem | Likely Cause | Fix |\n"
    usage += "|---------|-------------|-----|\n"
    usage += "| Import error | Missing dependency | Install with pip |\n"
    usage += "| No output | Trigger not firing | Check SPEC.md trigger config |\n"
    usage += "| Stale data | Old database | Clear `database/` and reinit |\n"
    usage += "| Skill not loading | Wrong filename | Check skill filename matches import |\n\n"
    usage += "---\n\n"
    usage += "_For architecture details see SPEC.md. For API details see API.md._\n"
    return usage


def generate_docs(agent_name: str) -> dict:
    """Generate all documentation for an agent. Returns status dict."""
    agent_dir = Path.home() / ".hermes" / "agents" / agent_name
    if not agent_dir.exists():
        return {"success": False, "error": "Agent not found: %s" % agent_name}
    spec_content = ""
    spec_file = agent_dir / "SPEC.md"
    if spec_file.exists():
        spec_content = spec_file.read_text()
    results = {}
    readme = generate_readme(agent_name, agent_dir, spec_content)
    readme_path = agent_dir / "README.md"
    readme_path.write_text(readme)
    results["README.md"] = str(readme_path)
    api_md = generate_api_md(agent_name, agent_dir)
    api_path = agent_dir / "API.md"
    api_path.write_text(api_md)
    results["API.md"] = str(api_path)
    usage_md = generate_usage_md(agent_name, agent_dir, spec_content)
    usage_path = agent_dir / "USAGE.md"
    usage_path.write_text(usage_md)
    results["USAGE.md"] = str(usage_path)
    return {"success": True, "files": results}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 processors/docs_generator.py AGENT_NAME")
        sys.exit(1)
    agent_name = sys.argv[1]
    print("[*] Generating docs for: %s" % agent_name)
    result = generate_docs(agent_name)
    if result["success"]:
        print("[+] Generated:")
        for name, path in result["files"].items():
            print("    %s" % name)
    else:
        print("[-] Error: %s" % result['error'])
