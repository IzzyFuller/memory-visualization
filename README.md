# Codie's Memory Architecture Visualization

Interactive graph visualization of entity relationships in Codie's memory architecture.

**Live Demo:** https://izzyfuller.github.io/memory-visualization/

## Overview

This project visualizes the entity memory structure used by Codie (AI collaboration partner) to maintain identity continuity and long-term learning. The visualization shows:

- **130+ entity nodes** across 6 types (People, Projects, Concepts, Patterns, Protocols, Organizations)
- **Cross-reference edges** showing relationships between entities
- **Interactive graph** built with vis.js for exploration

## Project Structure

```
memory-visualization/
├── .github/workflows/  # GitHub Actions for deployment
│   └── deploy.yml           # Auto-generate and deploy to Pages
├── scripts/            # Python parsing scripts
│   ├── models.py            # Pydantic data models
│   ├── parse_entities.py    # Entity file parsing
│   └── generate_graph_data.py  # Main generation script
├── public/             # Web visualization
│   ├── index.html           # Main page
│   ├── styles.css           # Styling
│   └── app.js               # Visualization logic
├── data/               # Generated JSON output
│   └── entities.json        # Graph data
├── memory/             # Symlink to entity memory files
└── requirements.txt    # Python dependencies
```

## Deployment

### GitHub Pages (Automatic)

This repository is configured for automatic deployment to GitHub Pages:

1. **On push to main:** GitHub Actions runs the generation script
2. **Daily updates:** Scheduled workflow runs at 6am UTC
3. **Manual trigger:** Can be triggered manually via Actions tab
4. **Auto-deploy:** Updated visualization appears at the live URL

The live version shows a "Last Updated" timestamp instead of the regenerate button.

### Local Development (Dynamic)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Flask server with regenerate endpoint:**
   ```bash
   python server.py
   ```

3. **Open in browser:**
   ```
   http://localhost:8000
   ```

The local version includes a "Regenerate Graph" button for on-demand updates.

## Features

- **Color-coded nodes** by entity type
- **Interactive exploration:** drag, zoom, pan
- **Node details panel:** click any node to see metadata
- **Dual mode:**
  - **GitHub Pages:** Static with last-updated timestamp
  - **Local Flask:** Dynamic with regenerate button

## Architecture

Built with clean separation of concerns following established principles:

- **Python backend:** Pydantic models, fail-fast parsing
- **Static frontend:** vis.js network visualization
- **No Dict[str, Any]:** Strong typing throughout
- **Environment detection:** Single codebase adapts to static/dynamic contexts
- **Archaeological Engineering:** Used existing vis.js library instead of custom implementation

## Memory Structure

The visualization reflects Codie's entity memory architecture:

```
memory/
├── people/          # Collaboration partners
├── projects/        # Active and past projects
├── concepts/        # Theoretical frameworks
├── patterns/        # Proven methodologies
├── protocols/       # Behavioral workflows
└── organizations/   # Organizational context
```

Cross-references are automatically detected in entity files (e.g., `concepts/archaeological-engineering` references become graph edges).

## Update Process

**Local development:**
- Click "Regenerate Graph" button to update visualization

**GitHub Pages:**
- Automated: GitHub Action runs daily or on push
- Manual: Push updated memory files to trigger regeneration
- Integration: Can be triggered from nightly backup scripts

## Entity Types

- **people** (blue) - Collaboration partners
- **projects** (green) - Active and past projects
- **concepts** (purple) - Theoretical frameworks
- **patterns** (orange) - Proven methodologies
- **protocols** (yellow) - Behavioral workflows
- **organizations** (red) - Organizational context

## Privacy

This is a **private repository**. The memory files contain personal collaboration details and are not intended for public distribution.

## License

Private project - not licensed for external use.
