"""BROCK Processors — all available."""
from .brief_parser import parse_brief
from .soul_writer import write_soul
from .spec_writer import write_spec
from .file_builder import create_directory_structure
from .db_builder import create_database_schema
from .skill_builder import create_skills
# Available extras:
# from .researcher import run_research
# from .self_improver import SelfImprover
# from .docs_generator import generate_docs
# from .version_control import record_version, list_versions, diff_versions, rollback
# from .monitor import get_stats, format_dashboard

__all__ = [
    "parse_brief",
    "write_soul",
    "write_spec",
    "create_directory_structure",
    "create_database_schema",
    "create_skills",
]
