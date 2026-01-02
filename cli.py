import os
import subprocess
from pathlib import Path

def get_git_url():
  
    try:
        res = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], 
            stderr=subprocess.STDOUT, 
            timeout=2
        )
        return res.decode().strip().replace(".git", "")
    except Exception:
        return "https://github.com/yourusername/project"

def get_directory_tree(path, prefix="", depth=0):
    """Generates a visual tree of the project structure."""
    if depth > 2:  # Limit depth to keep README clean
        return []
    
    ignore = {'.git', '__pycache__', 'node_modules', 'dist', 'build', '.venv', '.vscode'}
    tree = []
    
    try:
        items = sorted([p for p in path.iterdir() if p.name not in ignore])
        for i, item in enumerate(items):
            connector = "└── " if i == len(items) - 1 else "├── "
            tree.append(f"{prefix}{connector}{item.name}")
            if item.is_dir():
                extension = "    " if i == len(items) - 1 else "│   "
                tree.extend(get_directory_tree(item, prefix + extension, depth + 1))
    except PermissionError:
        pass
    return tree

def discover_context():
    """Identifies the project type and setup commands."""
    cwd = Path.cwd()
    files = [f.name for f in cwd.iterdir()]
    
    context = {
        "name": cwd.name,
        "tags": [],
        "install": "Standard setup",
        "type": "General Project",
        "test": None,
        "repo_url": get_git_url()
    }

    # DevOps Discovery
    if "Dockerfile" in files or "docker-compose.yml" in files:
        context["tags"].append("Docker")
        context["install"] = "docker-compose up --build"
    if any(f.endswith('.tf') for f in files):
        context["tags"].append("Terraform")
        context["type"] = "Infrastructure as Code"
        context["install"] = "terraform init && terraform apply"

    # AI / ML / LLM Discovery
    if any(f.endswith('.ipynb') for f in files):
        context["tags"].append("Jupyter")
        context["type"] = "Data Science / ML"
    
    # Programming Language & Dependencies
    if "package.json" in files:
        context["tags"].append("Node.js")
        context["install"] = "npm install"
        context["test"] = "npm test"
    elif "pyproject.toml" in files or "requirements.txt" in files:
        context["tags"].append("Python")
        context["install"] = "pip install -r requirements.txt"
        context["test"] = "pytest"
        
        # Check for Deep Learning / LLM libraries
        if "requirements.txt" in files:
            reqs = Path("requirements.txt").read_text(errors='ignore')
            if any(lib in reqs for lib in ["torch", "tensorflow", "keras"]):
                context["tags"].append("Deep-Learning")
            if any(lib in reqs for lib in ["langchain", "openai", "transformers"]):
                context["tags"].append("LLM/AI")

    return context

def generate():
    """Assembles the components and writes the README with UTF-8 encoding."""
    ctx = discover_context()
    tree_lines = get_directory_tree(Path.cwd())
    tree_str = "\n".join(tree_lines[:20])
    
    filename = "README.md"
    is_safe = True
    if Path(filename).exists():
        filename = "README_QUICK.md"
        is_safe = False

    tags_html = " ".join([f"![{t}](https://img.shields.io/badge/-{t}-blue)" for t in ctx['tags']])
    
    test_block = ""
    if ctx['test']:
        test_block = f"### 🧪 Testing\n```bash\n{ctx['test']}\n```"

    template = f"""
# {ctx['name']}
{tags_html}

## 📋 Project Type: {ctx['type']}

## 🚀 Quick Start
```bash
{ctx['install']}
```

{test_block}

## 📁 Project Structure
```
{tree_str}
```

## 🔗 Repository
[View on GitHub]({ctx['repo_url']})
"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template)
    
    if not is_safe:
        print(f"README.md already exists, created {filename} instead")
    else:
        print(f"Generated {filename}")

if __name__ == "__main__":
    generate()