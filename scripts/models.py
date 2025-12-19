"""
Pydantic models for entity memory representation.

No Dict[str, Any] - all types explicitly defined.
"""

from pydantic import BaseModel, Field


class ConceptSummary(BaseModel):
    """Structured summary for concept entities."""

    core_idea: str | None = Field(None, description="Main concept overview/principle")
    common_patterns: str | None = Field(None, description="Key characteristics or patterns")
    warning_signs: str | None = Field(None, description="Warning signs or indicators")
    origin_story: str | None = Field(None, description="Source, history, or validation examples")
    philosophy: str | None = Field(None, description="Meta-cognitive insights or integrations")


class EntityNode(BaseModel):
    """Represents a single entity in the memory graph."""

    id: str = Field(..., description="Unique entity identifier (e.g., 'concepts/archaeological_engineering')")
    label: str = Field(..., description="Display name for the node")
    type: str = Field(..., description="Entity type: people, projects, concepts, patterns, protocols, organizations")
    path: str = Field(..., description="File path to the entity markdown file")
    summary: ConceptSummary | None = Field(None, description="Structured summary (concepts only)")

    def get_color(self) -> str:
        """Returns color code based on entity type."""
        color_map = {
            "people": "#4A90E2",      # blue
            "projects": "#7ED321",    # green
            "concepts": "#9013FE",    # purple
            "patterns": "#F5A623",    # orange
            "protocols": "#F8E71C",   # yellow
            "organizations": "#D0021B" # red
        }
        return color_map.get(self.type, "#CCCCCC")


class EntityEdge(BaseModel):
    """Represents a relationship between two entities."""

    from_id: str = Field(..., description="Source entity ID")
    to_id: str = Field(..., description="Target entity ID")
    relationship_type: str = Field(default="references", description="Type of relationship")


class GraphData(BaseModel):
    """Complete graph data for visualization."""

    nodes: list[EntityNode] = Field(default_factory=list, description="All entity nodes")
    edges: list[EntityEdge] = Field(default_factory=list, description="All entity relationships")
