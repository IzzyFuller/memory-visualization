/**
 * Codie's Memory Visualization
 *
 * Loads entity graph data and renders interactive network visualization.
 */

// Load and render graph data
async function initializeVisualization() {
    try {
        // Load graph data
        const response = await fetch('../data/entities.json');
        const graphData = await response.json();

        // Transform data for vis.js
        const nodes = graphData.nodes.map(node => ({
            id: node.id,
            label: node.label,
            color: getColorForType(node.type),
            title: `${node.label}\n(${node.type})`,
            shape: 'dot',
            size: 20,
            font: { size: 14, color: '#333' }
        }));

        const edges = graphData.edges.map(edge => ({
            from: edge.from_id,
            to: edge.to_id,
            arrows: 'to',
            color: { color: '#95a5a6', opacity: 0.6 },
            width: 1
        }));

        // Create network
        const container = document.getElementById('network');
        const data = { nodes, edges };
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

        const network = new vis.Network(container, data, options);

        // Handle node clicks
        network.on('click', (params) => {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const node = graphData.nodes.find(n => n.id === nodeId);
                showEntityDetails(node);
            }
        });

        console.log(`✓ Loaded ${nodes.length} nodes and ${edges.length} edges`);

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
 * Get color for entity type.
 */
function getColorForType(type) {
    const colors = {
        people: '#4A90E2',
        projects: '#7ED321',
        concepts: '#9013FE',
        patterns: '#F5A623',
        protocols: '#F8E71C',
        organizations: '#D0021B'
    };
    return colors[type] || '#CCCCCC';
}

/**
 * Show entity details in info panel.
 */
function showEntityDetails(node) {
    const detailsDiv = document.getElementById('entityDetails');

    detailsDiv.innerHTML = `
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
}

/**
 * Handle regenerate button click.
 */
async function handleRegenerate() {
    const btn = document.getElementById('regenerateBtn');
    const statusMsg = document.getElementById('statusMessage');

    // Disable button and show loading state
    btn.disabled = true;
    btn.textContent = 'Regenerating...';
    statusMsg.textContent = '';
    statusMsg.className = 'status-message';

    try {
        const response = await fetch('/api/regenerate', {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            // Show success message
            statusMsg.textContent = `✓ Updated: ${result.nodes} nodes, ${result.edges} edges`;
            statusMsg.className = 'status-message success';

            // Reload visualization
            await initializeVisualization();

            // Clear message after 3 seconds
            setTimeout(() => {
                statusMsg.textContent = '';
            }, 3000);
        } else {
            throw new Error(result.error || 'Unknown error');
        }

    } catch (error) {
        console.error('Regeneration error:', error);
        statusMsg.textContent = `✗ Error: ${error.message}`;
        statusMsg.className = 'status-message error';
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.textContent = 'Regenerate Graph';
    }
}

/**
 * Check if running on GitHub Pages (static mode).
 */
function isGitHubPages() {
    return window.location.hostname.includes('github.io');
}

/**
 * Load and display last updated timestamp.
 */
async function loadLastUpdated() {
    try {
        const response = await fetch('/last-updated.json');
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
        // Static mode: hide regenerate button, show last updated
        regenerateBtn.style.display = 'none';
        loadLastUpdated();
    } else {
        // Local mode: show regenerate button, hide last updated
        lastUpdatedSpan.style.display = 'none';
        regenerateBtn.addEventListener('click', handleRegenerate);
    }
});
