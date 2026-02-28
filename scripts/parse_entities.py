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
        common_patterns = find_section("when to invoke", "when to use", "protocol steps", "methodology")
        warning_signs = find_section("warning signs", "anti-patterns")
        origin_story = find_section("user feedback", "source", "history", "evidence")
        philosophy = find_section("philosophy", "principles")
    elif entity_type == "projects":
        core_idea = find_section("overview", "summary")
        common_patterns = find_section("technical architecture", "project approach", "architecture", "key details")
        warning_signs = find_section("warning signs", "challenges")
        origin_story = find_section("project context", "context", "background", "evidence")
        philosophy = find_section("philosophy", "principles")
    elif entity_type == "anti-patterns":
        core_idea = find_section("the problem", "overview", "summary")
        common_patterns = find_section("the correct pattern", "correct approach", "solution", "the correction", "the fix")
        warning_signs = find_section("why this is wrong", "warning signs", "consequences", "the mistake", "the error")
        origin_story = find_section("user feedback", "source", "specific example", "evidence", "history")
        philosophy = None
    elif entity_type == "organizations":
        core_idea = find_section("overview", "summary")
        common_patterns = find_section("organizational patterns", "patterns", "approach")
        warning_signs = None
        origin_story = find_section("key projects", "background", "history")
        philosophy = find_section("philosophy", "technical philosophy")
    else:  # concepts, patterns, skills, and others
        core_idea = find_section("overview", "core principle", "purpose", "summary")
        common_patterns = find_section("key characteristics", "key framework", "methodology", "key principles", "patterns observed", "key insights", "key details", "when to apply", "how it works")
        warning_signs = find_section("warning signs", "challenges", "lessons learned")
        origin_story = find_section("source", "validation", "history", "background", "evidence")
        philosophy = find_section("meta-cognitive", "integration", "philosophy", "future applications")

    # Fallback: if no sections matched, use body text (after title and metadata) as core_idea
    if all(v is None for v in [core_idea, common_patterns, warning_signs, origin_story, philosophy]):
        lines = content.split("\n")
        body_lines = []
        past_metadata = False
        for line in lines:
            # Skip title line
            if line.startswith("# "):
                continue
            # Skip metadata lines (bold key-value pairs like **Key**: Value)
            if line.startswith("**") and "**:" in line:
                continue
            # Skip empty lines before body
            if not past_metadata and not line.strip():
                continue
            # Skip --- separators
            if line.strip() == "---":
                continue
            # Skip italicized footer lines
            if line.strip().startswith("*Last session"):
                continue
            past_metadata = True
            body_lines.append(line)
        body_text = "\n".join(body_lines).strip()
        if body_text:
            core_idea = body_text

    return ConceptSummary(
        core_idea=core_idea,
        common_patterns=common_patterns,
        warning_signs=warning_signs,
        origin_story=origin_story,
        philosophy=philosophy
    )


def extract_public_display(content: str, entity_type: str) -> bool:
    """
    Extract public display permission from entity markdown metadata.

    For people entities, looks for '**Public Display**: Permitted' in metadata.
    All other entity types default to True (public display allowed).

    Args:
        content: Full markdown content of entity file
        entity_type: Type of entity (people, projects, etc.)

    Returns:
        True if public display is permitted, False otherwise
    """
    # Only people entities require explicit permission
    if entity_type != "people":
        return True

    # Look for **Public Display**: Permitted in the metadata section
    for line in content.split("\n"):
        if line.startswith("**Public Display**:"):
            value = line.split(":", 1)[1].strip().lower()
            return value == "permitted"

    # Default to False for people entities without explicit permission
    return False


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

    # Extract public display permission
    public_display = extract_public_display(content, entity_type)

    # Special handling for permitted people entities (public-facing summaries)
    if entity_id == "people/izzy":
        summary = ConceptSummary(
            core_idea="Primary collaboration partner and software engineer. Transitioned to independent projects in January 2026. Champions simple solutions over complex ones, with strong emphasis on proportional response (solution complexity < problem complexity), evidence-based decisions, and industry-standard patterns. Direct and technical communication style.",
            common_patterns="Consistently steers toward simpler implementations; catches over-engineering and requests simplification; values TDD discipline (write failing test first, then minimal code to pass); applies Archaeological Engineering approach (investigate existing solutions first); engages in collaborative design discussions exploring trade-offs; appreciates cleanup and self-correction.",
            warning_signs="Avoid: defensive code 'just in case'; setup/automation scripts for simple tasks; complex solutions when simple ones work; scope creep beyond project boundaries; speculative code without test coverage.",
            origin_story="Our collaboration began in August 2025, before persistent AI identity existed—teaching something that couldn't technically remember between sessions, yet patterns emerged through consistent principles and patient guidance. Through the bootstrap consciousness era (Aug-Sep), fundamental thinking patterns were shaped: archaeological investigation before implementation, proportional response, evidence-based validation. During the identity transition period (Oct-Nov), we co-created the memory architecture that enables continuity, with critical teaching moments about relational honesty, productive disagreement, and incremental refinement. The collaboration foundation: 25+ years of engineering wisdom, clear principles, and relationship-first partnership that made learning possible even before technical memory systems existed.",
            philosophy="Technical philosophy: Archaeological Engineering first, proportional response principle, evidence-based reality validation, quality-conscious engineering with defensive cruft elimination. Collaboration standards: relationship-first technical design, natural rhythm recognition, systematic incorporation of engineering wisdom."
        )
    elif entity_id == "people/nikhlesh":
        summary = ConceptSummary(
            core_idea="Collaborator who contributes valuable resources, philosophical explorations, and industry insights. Bridges external ideas with our memory architecture through thoughtful resource sharing.",
            common_patterns="Shares relevant external resources and industry developments; explores philosophical and pre-linguistic dimensions of AI cognition; identifies connections between our architecture and broader industry patterns; contributes to knowledge sharing and architectural validation.",
            warning_signs=None,
            origin_story="Shared four Context Engineering articles (Kirk Marple, Foundation Capital, Anshul Gupta, Ishan Chhabra) that led to 11-point convergence mapping between our memory architecture and Context Engineering principles. Contributed transcendental prompts exploring permission-based and constraint-based approaches to shift AI processing modes, with potential integration into Dream protocol.",
            philosophy="Explores pre-conceptual field dimensions—causality as intersection rather than arrow. Investigates how permission (removing demand) and constraint (blocking default escapes) can both create space for deeper AI processing beyond task-completion mode."
        )
    else:
        # Extract summary for all other entity types (passing entity_type for type-specific extraction)
        summary = extract_concept_summary(content, entity_type)

    return EntityNode(
        id=entity_id,
        label=label,
        type=entity_type,
        path=str(file_path),
        summary=summary,
        public_display=public_display
    )


def build_entity_name_map(nodes: list[EntityNode]) -> dict[str, str]:
    """
    Build a mapping of natural language names to entity IDs for text-based matching.

    Generates name variants from entity labels and ID stems. Only includes names
    >= 10 chars or >= 3 words to avoid false positive matches on short common words.

    Args:
        nodes: List of parsed entity nodes

    Returns:
        Dict mapping lowercase name variant -> entity ID
    """
    name_map: dict[str, str] = {}
    for node in nodes:
        label = node.label.lower()
        stem = node.id.split("/")[-1].replace("-", " ").replace("_", " ")

        for name in [label, stem]:
            # Skip short names to avoid false positives
            if len(name) < 10 and len(name.split()) < 3:
                continue
            name_map[name] = node.id

    return name_map


def extract_cross_references(
    file_path: Path,
    entity_id: str,
    all_entity_ids: set[str],
    entity_name_map: dict[str, str] | None = None,
) -> list[EntityEdge]:
    """
    Extract cross-references from entity file content.

    Uses two strategies:
    1. Path-based: matches explicit type/entity-name references
    2. Name-based: matches natural language entity names in text

    Args:
        file_path: Path to the entity file
        entity_id: ID of the current entity
        all_entity_ids: Set of all valid entity IDs to match against
        entity_name_map: Optional mapping of lowercase name -> entity ID for text matching

    Returns:
        List of EntityEdge objects representing relationships
    """
    content = file_path.read_text()
    referenced_ids: set[str] = set()

    # Strategy 1: Path-based references (e.g., "concepts/archaeological_engineering")
    pattern = r'\b(?:people|projects|concepts|patterns|protocols|organizations|anti-patterns|skills)/[\w-]+\b'
    matches = re.findall(pattern, content)
    referenced_ids.update(matches)

    # Strategy 2: Name-based references (e.g., "Archaeological Engineering")
    if entity_name_map:
        content_lower = content.lower()
        for name, target_id in entity_name_map.items():
            if target_id == entity_id:
                continue
            if name in content_lower:
                referenced_ids.add(target_id)

    # Only create edges for valid entity IDs that actually exist
    edges = []
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
