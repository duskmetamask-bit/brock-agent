"""Skill builder — creates skill files from skill name list."""

from pathlib import Path
from datetime import datetime

SKILL_TEMPLATE = """# {skill_name}
**For:** {agent_name}
**Purpose:** {purpose}
**Last updated:** {date}

---

_Replace this with actual skill content._

**TODO:** Define the domain knowledge this skill encodes.

---

_Rules, patterns, or process specific to this skill._

---

*Update this skill when {domain} changes.*
"""


SKILL_PURPOSES = {
    "x-algo-skill": "X/Twitter algorithm rules and posting best practices",
    "linkedin-algo-skill": "LinkedIn algorithm rules and content best practices",
    "youtube-algo-skill": "YouTube algorithm rules and video best practices",
    "cold-email-skill": "Cold email templates, angles, and best practices",
    "audit-framework-skill": "The 3-phase audit framework (Discovery → Mapping → Presentation)",
    "discovery-question-skill": "Discovery call question flow and techniques",
    "voice-integration-skill": "Voice AI integration patterns and VAPI setup",
    "supabase-skill": "Supabase database patterns and schema design",
    "content-hook-skill": "20 proven content hook formulas",
    "outreach-sequence-skill": "Multi-step outreach sequence patterns",
    "client-onboarding-skill": "Client onboarding process and templates",
    "webhook-skill": "Webhook handling patterns and security",
}


def create_skills(agent_name: str, skill_names: list, output_dir: Path) -> list:
    """Create skill files. Returns list of created file paths."""

    created = []
    skills_dir = output_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    for skill_name in skill_names:
        purpose = SKILL_PURPOSES.get(
            skill_name,
            f"{skill_name} — domain knowledge for {agent_name}"
        )
        domain = skill_name.replace("-skill", "").replace("-", " ")

        content = SKILL_TEMPLATE.format(
            skill_name=skill_name.replace(".md", ""),
            agent_name=agent_name,
            purpose=purpose,
            domain=domain,
            date=datetime.now().strftime("%Y-%m-%d")
        )

        # Add .md if not present
        if not skill_name.endswith(".md"):
            skill_name += ".md"

        skill_path = skills_dir / skill_name
        skill_path.write_text(content)
        created.append(str(skill_path))

    return created


def create_skill(skill_name: str, agent_name: str, content: str, output_dir: Path) -> Path:
    """Create a skill file with custom content."""

    if not skill_name.endswith(".md"):
        skill_name += ".md"

    skill_path = output_dir / "skills" / skill_name
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(content)
    return skill_path


if __name__ == "__main__":
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as tmpdir:
        result = create_skills("TEST_AGENT", ["x-algo-skill", "cold-email-skill"], Path(tmpdir))
        print(f"Created {len(result)} skill files:")
        for f in result:
            print(f"  {f}")
