#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deterministic Living Code Graph & Interactive Visualizer Generator
Parses Python (AST), Go, PHP, and TypeScript to generate:
  1. documents/architecture/CODE_GRAPH_REGISTRY.md (for AI Agent)
  2. documents/architecture/CODE_GRAPH_VISUALIZER.html (for Human interactive review)
"""

import os
import ast
import re
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def get_elastic_mode():
    state_file = PROJECT_ROOT / ".agents" / "elastic_state.json"
    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("mode", "BALANCED"), data.get("max_parallel_workers", 4)
        except Exception:
            pass
    return "BALANCED", 4

class CodebaseScanner:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.controllers = {}
        self.services = {}
        self.repositories = {}
        self.enums = {}
        self.mode, self.workers = get_elastic_mode()

    def scan_all(self):
        ignore_dirs = {'.git', '.vscode', '.agents', 'venv', '.venv', 'node_modules', '__pycache__', 'dist', 'build', 'brain', 'storage'}
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                if ext == '.py':
                    self.scan_python(file_path)
                elif ext == '.go':
                    self.scan_go(file_path)
                elif ext in ['.php', '.ts', '.js']:
                    self.scan_generic(file_path, ext)

    def scan_python(self, file_path: Path):
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
        except Exception:
            return

        rel_path = file_path.relative_to(self.root_dir).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append(item.name)

                # Check if Enum
                is_enum = any(
                    (isinstance(base, ast.Name) and base.id in ['Enum', 'IntEnum', 'StrEnum']) or
                    (isinstance(base, ast.Attribute) and base.attr in ['Enum', 'IntEnum', 'StrEnum'])
                    for base in node.bases
                )

                if is_enum or 'Enum' in class_name or 'Status' in class_name or 'Type' in class_name:
                    enum_values = []
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    enum_values.append(target.id)
                    if enum_values:
                        self.enums[class_name] = enum_values
                elif 'Controller' in class_name or 'Router' in class_name or 'router' in rel_path:
                    self.controllers[class_name] = methods
                elif 'Service' in class_name:
                    self.services[class_name] = methods
                elif 'Repository' in class_name or 'Repo' in class_name or 'Dao' in class_name:
                    self.repositories[class_name] = methods

            # Standalone functions in routers/services
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_name = node.name
                if 'router' in rel_path or 'controller' in rel_path:
                    self.controllers.setdefault('RouterFunctions', []).append(fn_name)
                elif 'service' in rel_path:
                    self.services.setdefault('ServiceFunctions', []).append(fn_name)
                elif 'repo' in rel_path:
                    self.repositories.setdefault('RepoFunctions', []).append(fn_name)

    def scan_go(self, file_path: Path):
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return

        # Methods
        method_pattern = re.compile(r'func\s+\(\w+\s+\*?([A-Za-z0-9_]+)\)\s+([A-Za-z0-9_]+)\s*\(')
        for struct_name, method_name in method_pattern.findall(content):
            if 'Handler' in struct_name or 'Controller' in struct_name:
                self.controllers.setdefault(struct_name, []).append(method_name)
            elif 'Service' in struct_name:
                self.services.setdefault(struct_name, []).append(method_name)
            elif 'Repository' in struct_name or 'Repo' in struct_name:
                self.repositories.setdefault(struct_name, []).append(method_name)

        # Enums / Constants
        const_pattern = re.compile(r'const\s+\(\s*([\s\S]*?)\)')
        for const_block in const_pattern.findall(content):
            for line in const_block.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('//'):
                    parts = line.split()
                    if parts:
                        self.enums.setdefault('GoConstants', []).append(parts[0])

    def scan_generic(self, file_path: Path, ext: str):
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return

        class_pattern = re.compile(r'class\s+([A-Za-z0-9_]+)')
        fn_pattern = re.compile(r'(?:public|private|protected|async|function|\s)\s+([A-Za-z0-9_]+)\s*\(')

        classes = class_pattern.findall(content)
        for class_name in classes:
            fns = [f for f in fn_pattern.findall(content) if f not in ['__construct', 'function', 'if', 'for', 'while', 'switch']]
            if 'Controller' in class_name:
                self.controllers[class_name] = fns
            elif 'Service' in class_name:
                self.services[class_name] = fns
            elif 'Repository' in class_name or 'Repo' in class_name:
                self.repositories[class_name] = fns
            elif 'Enum' in class_name or 'Status' in class_name:
                self.enums[class_name] = fns

    def deduplicate(self):
        for d in [self.controllers, self.services, self.repositories, self.enums]:
            for k in d:
                d[k] = sorted(list(set(d[k])))

    def generate_markdown(self) -> str:
        md = ["# 🗺️ Living Code Graph & Inventory Registry\n"]
        md.append("> **Auto-generated via AST Scanner (`scripts/generate_code_graph.py`)**")
        md.append("> **Rules:** Always inspect existing Lego blocks here before creating new functions. Reuse 100% when possible.\n")

        md.append("## 🎮 Controllers & Routers")
        if not self.controllers:
            md.append("- *(No controllers scanned yet)*")
        for k, v in sorted(self.controllers.items()):
            md.append(f"- `{k}`: {', '.join(f'`{m}`' for m in v)}")
        md.append("")

        md.append("## 🧠 Services & Business Predicates")
        if not self.services:
            md.append("- *(No services scanned yet)*")
        for k, v in sorted(self.services.items()):
            md.append(f"- `{k}`: {', '.join(f'`{m}`' for m in v)}")
        md.append("")

        md.append("## 🗄️ Repositories & Data Access")
        if not self.repositories:
            md.append("- *(No repositories scanned yet)*")
        for k, v in sorted(self.repositories.items()):
            md.append(f"- `{k}`: {', '.join(f'`{m}`' for m in v)}")
        md.append("")

        md.append("## 🏷️ Enums & Domain Statuses")
        if not self.enums:
            md.append("- *(No enums scanned yet)*")
        for k, v in sorted(self.enums.items()):
            md.append(f"- `{k}`: {', '.join(f'`{m}`' for m in v)}")
        md.append("")

        return "\n".join(md)

    def generate_html_visualizer(self) -> str:
        mermaid_nodes = []
        mermaid_nodes.append("graph LR")
        mermaid_nodes.append("    classDef ctrl fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff;")
        mermaid_nodes.append("    classDef srv fill:#0f172a,stroke:#34d399,stroke-width:2px,color:#fff;")
        mermaid_nodes.append("    classDef repo fill:#1e1b4b,stroke:#a855f7,stroke-width:2px,color:#fff;")
        mermaid_nodes.append("    classDef enum fill:#312e81,stroke:#f43f5e,stroke-width:2px,color:#fff;")

        # Subgraphs
        if self.controllers:
            mermaid_nodes.append("    subgraph Controllers [🎮 Controllers]")
            for k, v in self.controllers.items():
                methods_str = "<br/>• " + "<br/>• ".join(v[:6]) if v else ""
                mermaid_nodes.append(f'        C_{abs(hash(k)) % 10000}["<b>{k}</b>{methods_str}"]:::ctrl')
            mermaid_nodes.append("    end")

        if self.services:
            mermaid_nodes.append("    subgraph Services [🧠 Services & Predicates]")
            for k, v in self.services.items():
                methods_str = "<br/>• " + "<br/>• ".join(v[:6]) if v else ""
                mermaid_nodes.append(f'        S_{abs(hash(k)) % 10000}["<b>{k}</b>{methods_str}"]:::srv')
            mermaid_nodes.append("    end")

        if self.repositories:
            mermaid_nodes.append("    subgraph Repositories [🗄️ Repositories]")
            for k, v in self.repositories.items():
                methods_str = "<br/>• " + "<br/>• ".join(v[:6]) if v else ""
                mermaid_nodes.append(f'        R_{abs(hash(k)) % 10000}["<b>{k}</b>{methods_str}"]:::repo')
            mermaid_nodes.append("    end")

        if self.enums:
            mermaid_nodes.append("    subgraph Enums [🏷️ Domain Enums]")
            for k, v in self.enums.items():
                vals_str = "<br/>• " + "<br/>• ".join(v[:6]) if v else ""
                mermaid_nodes.append(f'        E_{abs(hash(k)) % 10000}["<b>{k}</b>{vals_str}"]:::enum')
            mermaid_nodes.append("    end")

        # Visual connector flow
        mermaid_nodes.append("    Controllers -. calls .-> Services")
        mermaid_nodes.append("    Services -. mutates .-> Repositories")
        mermaid_nodes.append("    Repositories -. types .-> Enums")

        mermaid_str = "\n".join(mermaid_nodes)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏛️ Living Architecture Code Graph Visualizer</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #0b0f19;
            color: #e2e8f0;
            margin: 0;
            padding: 24px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        h1 {{
            margin: 0;
            font-size: 24px;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .badge {{
            background: #1e293b;
            color: #38bdf8;
            padding: 6px 12px;
            border-radius: 9999px;
            font-size: 13px;
            border: 1px solid #334155;
        }}
        .container {{
            background: #111827;
            border-radius: 12px;
            border: 1px solid #1f2937;
            padding: 24px;
            overflow: auto;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: #1e293b;
            padding: 16px;
            border-radius: 8px;
            border-left: 4px solid #38bdf8;
        }}
        .stat-card.srv {{ border-left-color: #34d399; }}
        .stat-card.repo {{ border-left-color: #a855f7; }}
        .stat-card.enum {{ border-left-color: #f43f5e; }}
        .stat-title {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; }}
        .stat-val {{ font-size: 24px; font-weight: bold; margin-top: 4px; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🏛️ Living Architecture Code Graph Visualizer</h1>
            <p style="color: #64748b; margin: 4px 0 0 0; font-size: 14px;">Automated AST Clean Architecture Visualization</p>
        </div>
        <div class="badge">Antigravity IDE 360° Studio</div>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-title">Controllers</div>
            <div class="stat-val">{len(self.controllers)}</div>
        </div>
        <div class="stat-card srv">
            <div class="stat-title">Services & Predicates</div>
            <div class="stat-val">{len(self.services)}</div>
        </div>
        <div class="stat-card repo">
            <div class="stat-title">Repositories</div>
            <div class="stat-val">{len(self.repositories)}</div>
        </div>
        <div class="stat-card enum">
            <div class="stat-title">Domain Enums</div>
            <div class="stat-val">{len(self.enums)}</div>
        </div>
    </div>

    <div class="container">
        <pre class="mermaid">
{mermaid_str}
        </pre>
    </div>

    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
    </script>
</body>
</html>
"""
        return html


def main():
    scanner = CodebaseScanner(PROJECT_ROOT)
    scanner.scan_all()
    scanner.deduplicate()

    # Create directories if not exist
    docs_arch = PROJECT_ROOT / "documents" / "architecture"
    docs_arch.mkdir(parents=True, exist_ok=True)

    # 1. Output Markdown
    md_file = docs_arch / "CODE_GRAPH_REGISTRY.md"
    md_content = scanner.generate_markdown()
    md_file.write_text(md_content, encoding='utf-8')
    print(f"✅ Generated: {md_file.as_posix()}")

    # 2. Output HTML Visualizer
    html_file = docs_arch / "CODE_GRAPH_VISUALIZER.html"
    html_content = scanner.generate_html_visualizer()
    html_file.write_text(html_content, encoding='utf-8')
    print(f"✅ Generated: {html_file.as_posix()}")

if __name__ == "__main__":
    main()
