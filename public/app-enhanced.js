/**
 * Codie's Memory Visualization - Enhanced with Filtering
 *
 * Loads entity graph data and renders interactive network visualization
 * with relationship type filtering and entity type filtering.
 */

// Global state
let networkInstance = null;
let allNodes = [];
let allEdges = [];
let activeEntityTypes = new Set();
let activeRelationshipTypes = new Set();

/**
 * Color palettes
 */
const ENTITY_COLORS = {
    people: '#4A90E2',
    projects: '#7ED321',
    concepts: '#9013FE',
    patterns: '#F5A623',
    protocols: '#F8E71C',
    organizations: '#D0021B'
};

const RELATIONSHIP_COLORS = {
    references: '#95a5a6',
    'depends-on': '#e74c3c',
    'used-by': '#3498db',
    'related-to': '#2ecc71',
    'derived-from': '#f39c12',
    'co-echo': '#9b59b6'
};

/**
 * Aggregate edges to calculate relationship strength
 */
function aggregateEdges(edges) {
    const aggregated = new Map();

    for (const edge of edges) {
        const key = `${edge.from_id}|${edge.to_id}|${edge.relationship_type}`;

        if (aggregated.has(key)) {
            aggregated.get(key).strength++;
        } else {
            aggregated.set(key, {
                from_id: edge.from_id,
                to_id: edge.to_id,
                relationship_type: edge.relationship_type,
                strength: 1
            });
        }
    }

    return Array.from(aggregated.values());
}

/**
 * Transform edges for vis.js with relationship colors and strength-based width
 */
function transformEdges(edges) {
    return edges.map(edge => ({
        from: edge.from_id,
        to: edge.to_id,
        arrows: 'to',
        color: {
            color: RELATIONSHIP_COLORS[edge.relationship_type] || '#95a5a6',
            opacity: 0.6
        },
        width: Math.min(1 + (edge.strength - 1) * 0.5, 5), // Width 1-5 based on strength
        title: `${edge.relationship_type} (strength: ${edge.strength})`,
        relationshipType: edge.relationship_type,
        strength: edge.strength
    }));
}

/**
 * Transform nodes for vis.js
 */
function transformNodes(nodes) {
    return nodes.map(node => ({
        id: node.id,
        label: node.label,
        color: ENTITY_COLORS[node.type] || '#CCCCCC',
        title: `${node.label}\n(${node.type})`,
        shape: 'dot',
        size: 20,
        font: { size: 14, color: '#333' },
        entityType: node.type,
        originalNode: node
    }));
}

/**
 * Filter nodes and edges based on active filters
 */
function applyFilters() {
    if (!networkInstance) return;

    // If no entity types selected, show all
    const showAllEntities = activeEntityTypes.size === 0;
    const showAllRelationships = activeRelationshipTypes.size === 0;

    // Filter nodes
    const visibleNodes = allNodes.filter(node =>
        showAllEntities || activeEntityTypes.has(node.entityType)
    );

    const visibleNodeIds = new Set(visibleNodes.map(n => n.id));

    // Filter edges (only show if both nodes are visible and relationship type is active)
    const visibleEdges = allEdges.filter(edge =>
        visibleNodeIds.has(edge.from) &&
        visibleNodeIds.has(edge.to) &&
        (showAllRelationships || activeRelationshipTypes.has(edge.relationshipType))
    );

    // Update network
    networkInstance.setData({
        nodes: visibleNodes,
        edges: visibleEdges
    });
}

/**
 * Create filter legend UI
 */
function createFilterLegend(nodes, edges) {
    const container = document.getElementById('filterLegend');
    if (!container) return;

    // Entity type filters
    const entityTypes = [...new Set(nodes.map(n => n.entityType))].sort();
    const relationshipTypes = [...new Set(edges.map(e => e.relationshipType))].sort();

    let html = '<div class="filter-section">';
    html += '<h3>Entity Types</h3>';
    html += '<div class="filter-buttons">';

    for (const type of entityTypes) {
        const color = ENTITY_COLORS[type] || '#CCCCCC';
        const count = nodes.filter(n => n.entityType === type).length;
        html += `
            <button class="filter-btn entity-filter active"
                    data-type="${type}"
                    style="border-color: ${color};">
                <span class="filter-dot" style="background-color: ${color};"></span>
                ${type} (${count})
            </button>
        `;
    }

    html += '</div></div>';

    // Relationship type filters
    html += '<div class="filter-section">';
    html += '<h3>Relationship Types</h3>';
    html += '<div class="filter-buttons">';

    for (const type of relationshipTypes) {
        const color = RELATIONSHIP_COLORS[type] || '#95a5a6';
        const count = edges.filter(e => e.relationshipType === type).length;
        html += `
            <button class="filter-btn relationship-filter active"
                    data-type="${type}"
                    style="border-color: ${color};">
                <span class="filter-line" style="background-color: ${color};"></span>
                ${type} (${count})
            </button>
        `;
    }

    html += '</div></div>';

    container.innerHTML = html;

    // Add event listeners
    document.querySelectorAll('.entity-filter').forEach(btn => {
        btn.addEventListener('click', () => toggleEntityFilter(btn));
    });

    document.querySelectorAll('.relationship-filter').forEach(btn => {
        btn.addEventListener('click', () => toggleRelationshipFilter(btn));
    });
}

/**
 * Toggle entity type filter
 */
function toggleEntityFilter(button) {
    const type = button.dataset.type;

    if (button.classList.contains('active')) {
        button.classList.remove('active');
        activeEntityTypes.delete(type);
    } else {
        button.classList.add('active');
        activeEntityTypes.add(type);
    }

    applyFilters();
}

/**
 * Toggle relationship type filter
 */
function toggleRelationshipFilter(button) {
    const type = button.dataset.type;

    if (button.classList.contains('active')) {
        button.classList.remove('active');
        activeRelationshipTypes.delete(type);
    } else {
        button.classList.add('active');
        activeRelationshipTypes.add(type);
    }

    applyFilters();
}

/**
 * Load and render graph data
 */
async function initializeVisualization() {
    try {
        // Load graph data
        const response = await fetch('data/entities.json');
        const graphData = await response.json();

        // Aggregate edges for strength calculation
        const aggregatedEdges = aggregateEdges(graphData.edges);

        // Transform data
        allNodes = transformNodes(graphData.nodes);
        allEdges = transformEdges(aggregatedEdges);

        // Initialize all filters as active (show everything initially)
        const entityTypes = [...new Set(allNodes.map(n => n.entityType))];
        const relationshipTypes = [...new Set(allEdges.map(e => e.relationshipType))];

        activeEntityTypes = new Set(entityTypes);
        activeRelationshipTypes = new Set(relationshipTypes);

        // Create network
        const container = document.getElementById('network');
        const data = { nodes: allNodes, edges: allEdges };
        const options = {
            physics: {
                stabilization: { iterations: 200 },
                barnesHut: {
                    gravitationalConstant: -8000,
                    springConstant: 0.04,
                    springLength: 150
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 100
            }
        };

        networkInstance = new vis.Network(container, data, options);

        // Create filter legend
        createFilterLegend(allNodes, allEdges);

        // Handle node clicks
        networkInstance.on('click', (params) => {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const node = allNodes.find(n => n.id === nodeId);
                if (node && node.originalNode) {
                    showEntityDetails(node.originalNode);
                }
            }
        });

        console.log(`✓ Loaded ${allNodes.length} nodes and ${allEdges.length} edges`);

    } catch (error) {
        console.error('Error loading visualization:', error);
        document.getElementById('network').innerHTML =
            `<div style="padding: 2rem; text-align: center; color: #e74c3c;">
                <h3>Error Loading Visualization</h3>
                <p>Failed to load graph data. Make sure to run:</p>
                <code>python scripts/generate_graph_data.py</code>
            </div>`;
    }
}

/**
 * Show entity details in info panel
 */
function showEntityDetails(node) {
    const detailsDiv = document.getElementById('entityDetails');

    let html = `
        <div class="detail-row">
            <div class="detail-label">Name</div>
            <div class="detail-value">${node.label}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Type</div>
            <div class="detail-value">${node.type}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">ID</div>
            <div class="detail-value"><code>${node.id}</code></div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Path</div>
            <div class="detail-value"><code>${node.path}</code></div>
        </div>
    `;

    // Add concept summary if available
    if (node.summary) {
        html += '<div class="concept-summary">';

        if (node.summary.core_idea) {
            html += `
                <div class="summary-section">
                    <h3>Core Idea</h3>
                    <p>${node.summary.core_idea}</p>
                </div>
            `;
        }

        if (node.summary.common_patterns) {
            html += `
                <div class="summary-section">
                    <h3>Common Patterns</h3>
                    <div class="summary-content">${formatMarkdown(node.summary.common_patterns)}</div>
                </div>
            `;
        }

        if (node.summary.warning_signs) {
            html += `
                <div class="summary-section">
                    <h3>Warning Signs</h3>
                    <div class="summary-content">${formatMarkdown(node.summary.warning_signs)}</div>
                </div>
            `;
        }

        if (node.summary.origin_story) {
            html += `
                <div class="summary-section">
                    <h3>Origin Story</h3>
                    <div class="summary-content">${formatMarkdown(node.summary.origin_story)}</div>
                </div>
            `;
        }

        if (node.summary.philosophy) {
            html += `
                <div class="summary-section">
                    <h3>Philosophy</h3>
                    <div class="summary-content">${formatMarkdown(node.summary.philosophy)}</div>
                </div>
            `;
        }

        html += '</div>';
    }

    detailsDiv.innerHTML = html;
}

/**
 * Simple markdown formatter for summary content
 */
function formatMarkdown(text) {
    if (!text) return '';

    // Remove code blocks
    text = text.replace(/```[\s\S]*?```/g, '');
    text = text.replace(/^    .+$/gm, '');

    // Truncate to ~750 characters at sentence boundary
    if (text.length > 750) {
        let truncated = text.substring(0, 750);
        let lastPeriod = truncated.lastIndexOf('.');
        if (lastPeriod > 400) {
            text = truncated.substring(0, lastPeriod + 1) + ' [...]';
        } else {
            text = truncated.substring(0, truncated.lastIndexOf(' ')) + '... [...]';
        }
    }

    return text
        .replace(/### (.*?)$/gm, '<h4>$1</h4>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
}

/**
 * Handle regenerate button click
 */
async function handleRegenerate() {
    const btn = document.getElementById('regenerateBtn');
    const statusMsg = document.getElementById('statusMessage');

    btn.disabled = true;
    btn.textContent = 'Regenerating...';
    statusMsg.textContent = '';
    statusMsg.className = 'status-message';

    try {
        const response = await fetch('/api/regenerate', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            statusMsg.textContent = `✓ Updated: ${result.nodes} nodes, ${result.edges} edges`;
            statusMsg.className = 'status-message success';
            await initializeVisualization();
            setTimeout(() => { statusMsg.textContent = ''; }, 3000);
        } else {
            throw new Error(result.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Regeneration error:', error);
        statusMsg.textContent = `✗ Error: ${error.message}`;
        statusMsg.className = 'status-message error';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Regenerate Graph';
    }
}

/**
 * Check if running on GitHub Pages
 */
function isGitHubPages() {
    return window.location.hostname.includes('github.io');
}

/**
 * Load and display last updated timestamp
 */
async function loadLastUpdated() {
    try {
        const response = await fetch('last-updated.json');
        const data = await response.json();
        const date = new Date(data.lastUpdated);
        const formatted = date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            timeZoneName: 'short'
        });
        document.getElementById('lastUpdated').textContent = `Last updated: ${formatted}`;
    } catch (error) {
        console.log('Could not load last updated timestamp');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeVisualization();

    const regenerateBtn = document.getElementById('regenerateBtn');
    const lastUpdatedSpan = document.getElementById('lastUpdated');

    if (isGitHubPages()) {
        regenerateBtn.style.display = 'none';
        loadLastUpdated();
    } else {
        lastUpdatedSpan.style.display = 'none';
        regenerateBtn.addEventListener('click', handleRegenerate);
    }
});
