"""
BROCK Research Processor
Phase 0 of every build: deep research into similar agents.

Usage:
    python3 processors/researcher.py "voice agent"
    python3 processors/researcher.py "content intelligence agent"
"""

import sys
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime

def duckduckgo_search(query: str, max_results: int = 5) -> list[dict]:
    """Search DuckDuckGo via HTML scrape. Returns list of {title, url, snippet}."""
    import urllib.parse
    import urllib.request
    
    encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html",
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return [{"title": f"Search failed: {e}", "url": "", "snippet": ""}]
    
    results = []
    
    # DuckDuckGo uses redirect URLs: //duckduckgo.com/l/?uddg=https%3A%2F%2F...
    # Extract actual URLs from the uddg parameter
    a_tags = re.findall(
        r'<a[^>]+class="[^"]*result[^"]*"[^>]+href="([^"]+)"[^>]*>([^<]+(?:<[^>]+>[^<]*)*)</a>',
        html
    )
    
    for href, title_html in a_tags:
        title = re.sub(r'<[^>]+>', '', title_html).strip()
        title = title.replace('\n', ' ').strip()
        
        # Extract real URL from DuckDuckGo redirect
        real_url = href
        if 'uddg=' in href:
            try:
                import urllib.parse as up
                parsed = up.urlparse(href)
                qs = dict(up.parse_qsl(parsed.query))
                if 'uddg' in qs:
                    real_url = qs['uddg']
            except Exception:
                pass
        
        # Get snippet from nearby text
        snippet = ""
        snippet_match = re.search(
            r'result__snippet[^>]*>([^<]+)',
            html[html.find(href):html.find(href)+500]
        )
        if snippet_match:
            snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()
        
        results.append({"title": title, "url": real_url, "snippet": snippet})
        if len(results) >= max_results:
            break
    
    # Fallback: simpler regex if above misses
    if not results:
        # Match: <a ... href="//duckduckgo.com/l/?uddg=...">Title</a>
        redirect_pattern = re.compile(
            r'<a[^>]+href="//duckduckgo\.com/l/\?uddg=([^"&]+)[^"]*"[^>]*>([^<]+)</a>'
        )
        for match in redirect_pattern.finditer(html):
            import urllib.parse as up
            real_url = up.unquote(match.group(1))
            title = re.sub(r'<[^>]+>', '', match.group(2)).replace('\n', ' ').strip()
            results.append({"title": title, "url": real_url, "snippet": ""})
            if len(results) >= max_results:
                break
    
    return results


def fetch_page_content(url: str) -> str:
    """Fetch a URL and extract readable text."""
    import urllib.request
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""
    
    # Remove scripts, styles, nav
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL)
    html = re.sub(r'<header[^>]*>.*?</header>', '', html, flags=re.DOTALL)
    html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=re.DOTALL)
    
    # Convert to text
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text[:3000]  # Limit to avoid token bloat


def extract_agent_info(title: str, snippet: str, content: str) -> dict:
    """Extract useful agent architecture info from search result."""
    info = {
        "name": title,
        "url": "",
        "type": "",
        "architecture": [],
        "prompts": [],
        "tools": [],
        "failure_modes": [],
        "what_makes_it_work": []
    }
    
    text = (snippet + " " + content[:2000]).lower()
    
    # Detect agent type
    if "github" in title.lower():
        info["type"] = "open source"
    elif any(k in text for k in ["api", "sdk", "platform"]):
        info["type"] = "commercial/saas"
    else:
        info["type"] = "unknown"
    
    # Extract architecture hints
    arch_keywords = ["processor", "agent", "loop", "pipeline", "stage", "phase", "step"]
    for kw in arch_keywords:
        if kw in text:
            info["architecture"].append(kw)
    
    # Extract tool/API hints
    tool_keywords = ["openai", "anthropic", "vapi", "supabase", "gmail", "discord", "telegram", "browser"]
    for kw in tool_keywords:
        if kw in text:
            info["tools"].append(kw)
    
    return info


def generate_research_report(domain: str, results: list[dict], agent_infos: list[dict]) -> str:
    """Generate a markdown research summary."""
    
    report = f"""# Research Summary — {domain}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Sources found:** {len(results)}

---

## Agents Found

"""
    
    for i, r in enumerate(results[:5], 1):
        report += f"""### {i}. {r['title']}
**URL:** {r['url']}
**Snippet:** {r['snippet'][:300]}

"""
    
    report += """---

## Architecture Patterns Found

"""
    
    all_arch = []
    all_tools = []
    for info in agent_infos:
        all_arch.extend(info['architecture'])
        all_tools.extend(info['tools'])
    
    arch_counts = {x: all_arch.count(x) for x in set(all_arch)}
    tool_counts = {x: all_tools.count(x) for x in set(all_tools)}
    
    report += "**Common architectural terms:**\n"
    for term, count in sorted(arch_counts.items(), key=lambda x: -x[1]):
        report += f"- {term} ({count}x)\n"
    
    report += "\n**Tools/APIs used:**\n"
    for tool, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
        report += f"- {tool} ({count}x)\n"
    
    report += """

---

## Key Findings

"""
    
    for i, info in enumerate(agent_infos[:5], 1):
        findings = []
        if info['architecture']:
            findings.append(f"Uses: {', '.join(set(info['architecture']))}")
        if info['tools']:
            findings.append(f"Tools: {', '.join(set(info['tools']))}")
        if findings:
            report += f"- **{info['name']}:** {' | '.join(findings)}\n"
    
    report += """

---

## Recommendations for This Build

Based on research, this """ + domain + """ agent should:

1. **Architecture:** Consider a pipeline/phase structure given common patterns
2. **Tools:** """ + (", ".join([t for t, c in tool_counts.items() if c >= 2]) or "Evaluate based on specific requirements") + """
3. **Key success factors:** Study how similar agents handle failure modes

---

## Sources

"""
    for r in results[:5]:
        report += f"- [{r['title']}]({r['url']})\n"
    
    return report


def run_research(domain: str) -> str:
    """Main research entry point."""
    print(f"[*] Researching: {domain}")
    
    # Build search queries
    queries = [
        f"{domain} AI agent architecture github",
        f"{domain} autonomous agent open source",
        f"best {domain} AI agent 2024 2025",
    ]
    
    all_results = []
    agent_infos = []
    
    for query in queries:
        print(f"    [*] Searching: {query}")
        results = duckduckgo_search(query, max_results=5)
        for r in results:
            if r['url'] and r['title']:
                all_results.append(r)
                content = fetch_page_content(r['url'])
                info = extract_agent_info(r['title'], r['snippet'], content)
                agent_infos.append(info)
        print(f"    [+] Got {len(results)} results")
    
    # Deduplicate by URL
    seen = set()
    unique_results = []
    unique_infos = []
    for r, i in zip(all_results, agent_infos):
        if r['url'] not in seen:
            seen.add(r['url'])
            unique_results.append(r)
            unique_infos.append(i)
    
    print(f"[*] Total unique sources: {len(unique_results)}")
    
    # Generate report
    report = generate_research_report(domain, unique_results, unique_infos)
    
    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 processors/researcher.py \"voice agent\"")
        sys.exit(1)
    
    domain = " ".join(sys.argv[1:])
    report = run_research(domain)
    
    # Save to output
    output_dir = Path.home() / ".hermes" / "agents" / "brock" / "research_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    safe_name = re.sub(r'[^a-z0-9]+', '-', domain.lower())
    output_path = output_dir / f"{safe_name}-research.md"
    output_path.write_text(report)
    
    print(f"\n[+] Research report saved to: {output_path}")
    print("\n" + "="*60)
    print(report)
