"""
Parse entity files from Codie's memory directory.

Clean, focused implementation following fail-fast principles.
"""

import re
from pathlib import Path

from models import EntityNode, EntityEdge, ConceptSummary


def extract_concept_summary(content: str) -> ConceptSummary:
    """
    Extract structured summary from concept markdown file.

    Maps markdown sections to summary fields:
    - Overview/Core Principle → core_idea
    - Key Characteristics/Framework → common_patterns
    - Warning Signs → warning_signs
    - Source/Validation/History → origin_story
    - Meta-Cognitive/Integration/Philosophy → philosophy

    Args:
        content: Full markdown content of concept file

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

    return ConceptSummary(
        core_idea=find_section("overview", "core principle"),
        common_patterns=find_section("key characteristics", "key framework", "methodology", "key principles"),
        warning_signs=find_section("warning signs"),
        origin_story=find_section("source", "validation", "history"),
        philosophy=find_section("meta-cognitive", "integration", "philosophy")
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

    # Extract summary for all entity types (they all use similar markdown structure)
    summary = extract_concept_summary(content)

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
    pattern = r'\b(?:people|projects|concepts|patterns|protocols|organizations)/[\w-]+\b'

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
    entity_types = ["people", "projects", "concepts", "patterns", "protocols", "organizations"]
    entity_files = []

    for entity_type in entity_types:
        type_dir = memory_root / entity_type
        if type_dir.exists():
            # Find all .md files in this entity type directory
            entity_files.extend(type_dir.glob("*.md"))

    return entity_files
