"""
Parse entity files from Codie's memory directory.

Clean, focused implementation following fail-fast principles.
"""

import re
from pathlib import Path

from models import EntityNode, EntityEdge


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

    return EntityNode(
        id=entity_id,
        label=label,
        type=entity_type,
        path=str(file_path)
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
