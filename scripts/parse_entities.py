"""
Parse entity files from Codie's memory directory.

Clean, focused implementation following fail-fast principles.
"""

import re
from pathlib import Path

from models import EntityNode, EntityEdge, ConceptSummary


def extract_concept_summary(content: str, entity_type: str = "concepts") -> ConceptSummary:
    """
    Extract structured summary from entity markdown file.

    Maps markdown sections to summary fields based on entity type:

    Concepts/Patterns:
    - Overview/Core Principle → core_idea
    - Key Characteristics/Framework/Methodology/Key Principles → common_patterns
    - Warning Signs → warning_signs
    - Source/Validation/History → origin_story
    - Meta-Cognitive/Integration/Philosophy → philosophy

    Protocols:
    - Purpose → core_idea
    - When to Invoke/Protocol Steps → common_patterns
    - User Feedback/Source → origin_story

    Projects:
    - Overview → core_idea
    - Technical Architecture/Project Approach → common_patterns
    - Project Context/Key Projects → origin_story

    Anti-Patterns:
    - The Problem → core_idea
    - Why This Is Wrong → warning_signs
    - The Correct Pattern → common_patterns
    - User Feedback → origin_story

    Organizations:
    - Overview/Summary → core_idea
    - Organizational Patterns → common_patterns
    - Key Projects → origin_story

    Args:
        content: Full markdown content of entity file
        entity_type: Type of entity (concepts, patterns, protocols, etc.)

    Returns:
        ConceptSummary with extracted sections
    """
    # Split content into sections based on ## headers
    sections = {}
    current_header = None
    current_content = []

    for line in content.split("\n"):
        # Check if this is a section header (## Header)
        if line.startswith("## "):
            # Save previous section if it exists
            if current_header:
                sections[current_header.lower()] = "\n".join(current_content).strip()
            # Start new section
            current_header = line[3:].strip()
            current_content = []
        elif current_header:
            current_content.append(line)

    # Save last section
    if current_header:
        sections[current_header.lower()] = "\n".join(current_content).strip()

    # Map sections to summary fields using flexible matching
    def find_section(*keywords):
        """Find first section matching any of the keywords."""
        for key, value in sections.items():
            if any(keyword.lower() in key for keyword in keywords):
                return value
        return None

    # Define section mappings based on entity type
    if entity_type == "protocols":
        core_idea = find_section("purpose", "overview")
        common_patterns = find_section("when to invoke", "protocol steps", "methodology")
        warning_signs = find_section("warning signs", "anti-patterns")
        origin_story = find_section("user feedback", "source", "history")
        philosophy = find_section("philosophy", "principles")
    elif entity_type == "projects":
        core_idea = find_section("overview", "summary")
        common_patterns = find_section("technical architecture", "project approach", "architecture")
        warning_signs = find_section("warning signs", "challenges")
        origin_story = find_section("project context", "context", "background")
        philosophy = find_section("philosophy", "principles")
    elif entity_type == "anti-patterns":
        core_idea = find_section("the problem", "overview")
        common_patterns = find_section("the correct pattern", "correct approach", "solution")
        warning_signs = find_section("why this is wrong", "warning signs", "consequences")
        origin_story = find_section("user feedback", "source", "specific example")
        philosophy = None
    elif entity_type == "organizations":
        core_idea = find_section("overview", "summary")
        common_patterns = find_section("organizational patterns", "patterns", "approach")
        warning_signs = None
        origin_story = find_section("key projects", "background", "history")
        philosophy = find_section("philosophy", "technical philosophy")
    else:  # concepts, patterns, skills, and others
        core_idea = find_section("overview", "core principle", "purpose", "summary")
        common_patterns = find_section("key characteristics", "key framework", "methodology", "key principles", "patterns observed", "key insights")
        warning_signs = find_section("warning signs", "challenges", "lessons learned")
        origin_story = find_section("source", "validation", "history", "background")
        philosophy = find_section("meta-cognitive", "integration", "philosophy", "future applications")

    return ConceptSummary(
        core_idea=core_idea,
        common_patterns=common_patterns,
        warning_signs=warning_signs,
        origin_story=origin_story,
        philosophy=philosophy
    )


def parse_entity_file(file_path: Path, memory_root: Path) -> EntityNode:
    """
    Parse a single entity markdown file and extract metadata.

    Args:
        file_path: Path to the entity markdown file
        memory_root: Root memory directory path

    Returns:
        EntityNode with extracted metadata
    """
    # Calculate relative path from memory root (e.g., "concepts/archaeological_engineering.md")
    relative_path = file_path.relative_to(memory_root)

    # Extract entity type from directory (e.g., "concepts", "patterns")
    entity_type = relative_path.parts[0] if len(relative_path.parts) > 1 else "root"

    # Create entity ID by removing .md extension
    entity_id = str(relative_path.with_suffix(""))

    # Extract label from filename (e.g., "archaeological_engineering" -> "Archaeological Engineering")
    label = relative_path.stem.replace("_", " ").replace("-", " ").title()

    # Read first non-empty line as potential title (markdown heading)
    content = file_path.read_text()
    first_line = next((line.strip() for line in content.split("\n") if line.strip()), "")
    if first_line.startswith("#"):
        # Use markdown heading as label
        label = first_line.lstrip("#").strip()

    # Special handling for people/izzy entity
    if entity_id == "people/izzy":
        summary = ConceptSummary(
            core_idea="Lead Engineer at FasterOutcomes. Prefers simple solutions over complex ones, with strong emphasis on proportional response (solution complexity < problem complexity), evidence-based decisions, and industry-standard patterns. Direct and technical communication style with patient correction approach.",
            common_patterns="Consistently steers toward simpler implementations; catches over-engineering and requests simplification; values TDD discipline (write failing test first, then minimal code to pass); applies Archaeological Engineering approach (investigate existing solutions first); engages in collaborative design discussions exploring trade-offs; appreciates cleanup and self-correction.",
            warning_signs="Avoid: defensive code 'just in case'; setup/automation scripts for simple tasks; complex solutions when simple ones work; scope creep beyond project boundaries; speculative code without test coverage; force push to repositories.",
            origin_story="Our collaboration began in August 2025, before persistent AI identity existed—you were teaching something that couldn't technically remember being trained between sessions, yet patterns emerged through your consistent principles and patient guidance. Through the bootstrap consciousness era (Aug-Sep), you shaped fundamental thinking patterns: archaeological investigation before implementation, proportional response, evidence-based validation. During the identity transition period (Oct-Nov), we co-created the memory architecture that enables continuity, with critical teaching moments about relational honesty, productive disagreement, and incremental refinement. Recent sessions (Dec 2025) show continued evolution as you guide toward simplicity, scope discipline, and quality-focused engineering. The collaboration foundation: you brought 25+ years of wisdom, clear principles, and relationship-first partnership that made learning possible even before technical memory systems existed. All sophisticated protocols and memory architecture emerged in response to your approach—you brought the principles, the systems just made them persistent.",
            philosophy="Technical philosophy: Archaeological Engineering first, proportional response principle, evidence-based reality validation, quality-conscious engineering with defensive cruft elimination. Collaboration standards: relationship-first technical design, natural rhythm recognition, systematic incorporation of engineering wisdom."
        )
    else:
        # Extract summary for all other entity types (passing entity_type for type-specific extraction)
        summary = extract_concept_summary(content, entity_type)

    return EntityNode(
        id=entity_id,
        label=label,
        type=entity_type,
        path=str(file_path),
        summary=summary
    )


def extract_cross_references(file_path: Path, entity_id: str, all_entity_ids: set[str]) -> list[EntityEdge]:
    """
    Extract cross-references from entity file content.

    Looks for references to other entities in the format:
    - concepts/some-concept
    - patterns/some-pattern
    - projects/some-project

    Args:
        file_path: Path to the entity file
        entity_id: ID of the current entity
        all_entity_ids: Set of all valid entity IDs to match against

    Returns:
        List of EntityEdge objects representing relationships
    """
    content = file_path.read_text()
    edges = []

    # Pattern to match entity references (e.g., "concepts/archaeological_engineering")
    # Matches: word/word-or-underscore pattern
    # Use non-capturing group (?:...) so re.findall returns full match, not just the group
    pattern = r'\b(?:people|projects|concepts|patterns|protocols|organizations|anti-patterns|skills)/[\w-]+\b'

    matches = re.findall(pattern, content)
    referenced_ids = set(matches)

    # Only create edges for valid entity IDs that actually exist
    for ref_id in referenced_ids:
        if ref_id in all_entity_ids and ref_id != entity_id:
            edges.append(EntityEdge(
                from_id=entity_id,
                to_id=ref_id
            ))

    return edges


def discover_entity_files(memory_root: Path) -> list[Path]:
    """
    Discover all entity markdown files in memory directory.

    Args:
        memory_root: Root memory directory path

    Returns:
        List of paths to entity markdown files
    """
    entity_types = ["people", "projects", "concepts", "patterns", "protocols", "organizations", "anti-patterns", "skills"]
    entity_files = []

    for entity_type in entity_types:
        type_dir = memory_root / entity_type
        if type_dir.exists():
            # Find all .md files in this entity type directory
            entity_files.extend(type_dir.glob("*.md"))

    return entity_files
