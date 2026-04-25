"""Brief parser — converts brief text/file to structured dict."""
import re
import yaml


def parse_brief(text: str) -> dict:
    """Parse brief from text (markdown or plain)."""

    # Try YAML first
    try:
        return yaml.safe_load(text)
    except:
        pass

    # Fall back to simple key-value extraction
    brief = {
        "required_skills": [],
        "required_processors": [],
    }

    # Extract agent_name
    name_match = re.search(r'agent[_-]?name[:\s]+["\']?([^"\'\n]+)', text, re.IGNORECASE)
    if name_match:
        brief["agent_name"] = name_match.group(1).strip()

    # Extract domain
    domain_match = re.search(r'domain[:\s]+["\']?([^"\'\n]+)', text, re.IGNORECASE)
    if domain_match:
        brief["domain"] = domain_match.group(1).strip()

    # Extract voice
    voice_match = re.search(r'voice[:\s]+["\']?([^"\'\n]+)', text, re.IGNORECASE)
    if voice_match:
        brief["voice_direction"] = voice_match.group(1).strip()

    # Extract pipeline position
    pipeline_match = re.search(r'pipeline[:\s]+["\']?([^"\'\n]+)', text, re.IGNORECASE)
    if pipeline_match:
        brief["pipeline_position"] = pipeline_match.group(1).strip()

    # Extract trigger
    trigger_match = re.search(r'trigger[:\s]+["\']?([^"\'\n]+)', text, re.IGNORECASE)
    if trigger_match:
        brief["trigger"] = trigger_match.group(1).strip()

    # Extract skills list
    skills_section = re.search(r'skills?[:\s*\n](.+?)(?:\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if skills_section:
        skill_lines = skills_section.group(1).strip().split('\n')
        for line in skill_lines:
            line = re.sub(r'^[-*•]\s*', '', line.strip())
            if line:
                brief["required_skills"].append(line)

    # Extract processors list
    proc_section = re.search(r'processors?[:\s*\n](.+?)(?:\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if proc_section:
        proc_lines = proc_section.group(1).strip().split('\n')
        for line in proc_lines:
            line = re.sub(r'^[-*•]\s*', '', line.strip())
            if line:
                brief["required_processors"].append(line)

    return brief


if __name__ == "__main__":
    # Test
    test = """
    agent_name: TEST_AGENT
    domain: testing agent builder
    voice: direct and efficient
    skills:
      - x-algo-skill
      - content-hook-skill
    processors:
      - core
      - evaluator
    """
    print(parse_brief(test))
