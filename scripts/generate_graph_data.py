"""
Generate graph visualization data from Codie's entity memory.

Main orchestration script that:
1. Discovers all entity files
2. Parses each entity
3. Extracts cross-references
4. Generates JSON output

Run: python scripts/generate_graph_data.py
"""

import json
from pathlib import Path

from models import GraphData
from parse_entities import discover_entity_files, parse_entity_file, extract_cross_references


def main():
    """Generate graph data JSON from entity memory."""

    # Memory root directory (relative to project root via symlink)
    project_root = Path(__file__).parent.parent
    memory_root = project_root / "memory"

    # Output path
    output_path = project_root / "data" / "entities.json"

    print(f"Parsing entities from: {memory_root}")

    # Step 1: Discover all entity files
    entity_files = discover_entity_files(memory_root)
    print(f"Found {len(entity_files)} entity files")

    # Step 2: Parse all entities
    nodes = []
    for entity_file in entity_files:
        try:
            node = parse_entity_file(entity_file, memory_root)
            nodes.append(node)
        except Exception as e:
            # Fail-fast: Let errors surface rather than silently skipping
            print(f"Error parsing {entity_file}: {e}")
            raise

    print(f"Parsed {len(nodes)} entities")

    # Create entity ID set for cross-reference validation
    entity_ids = {node.id for node in nodes}

    # Step 3: Extract cross-references
    edges = []
    for entity_file in entity_files:
        try:
            # Get corresponding node for this file
            relative_path = entity_file.relative_to(memory_root)
            entity_id = str(relative_path.with_suffix(""))

            # Extract edges
            entity_edges = extract_cross_references(entity_file, entity_id, entity_ids)
            edges.extend(entity_edges)
        except Exception as e:
            print(f"Error extracting references from {entity_file}: {e}")
            raise

    print(f"Extracted {len(edges)} cross-references")

    # Step 4: Generate graph data
    graph_data = GraphData(nodes=nodes, edges=edges)

    # Step 5: Write JSON output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(graph_data.model_dump_json(indent=2))

    print(f"✓ Graph data written to: {output_path}")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Edges: {len(edges)}")


if __name__ == "__main__":
    main()
