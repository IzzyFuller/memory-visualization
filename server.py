"""
Simple Flask server for memory visualization.

Serves static files and provides endpoint to regenerate graph data.
"""

import subprocess
from pathlib import Path

from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent
PUBLIC_DIR = PROJECT_ROOT / "public"
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


@app.route("/")
def index():
    """Serve the main visualization page."""
    return send_from_directory(PUBLIC_DIR, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    """Serve static files from public directory."""
    return send_from_directory(PUBLIC_DIR, path)


@app.route("/data/<path:path>")
def serve_data(path):
    """Serve data files."""
    return send_from_directory(DATA_DIR, path)


@app.route("/api/regenerate", methods=["POST"])
def regenerate():
    """
    Regenerate graph data by running the generation script.

    Returns:
        JSON response with success status and node/edge counts
    """
    try:
        # Run the generation script
        result = subprocess.run(
            ["python", str(SCRIPTS_DIR / "generate_graph_data.py")],
            capture_output=True,
            text=True,
            check=True,
            cwd=PROJECT_ROOT
        )

        # Parse output to extract node/edge counts
        output = result.stdout
        nodes = 0
        edges = 0
        for line in output.split("\n"):
            if "Nodes:" in line:
                nodes = int(line.split("Nodes:")[1].strip())
            elif "Edges:" in line:
                edges = int(line.split("Edges:")[1].strip())

        return jsonify({
            "success": True,
            "nodes": nodes,
            "edges": edges,
            "message": "Graph data regenerated successfully"
        })

    except subprocess.CalledProcessError as e:
        return jsonify({
            "success": False,
            "error": f"Script failed: {e.stderr}"
        }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
