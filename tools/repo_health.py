from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".github", "tools", "docs"}
PROJECT_MARKERS = ("README.md", "pyproject.toml", "package.json", "docker-compose.yml", "index.html")


def discover_projects() -> list[Path]:
    projects: list[Path] = []
    for path in ROOT.iterdir():
        if not path.is_dir():
            continue
        if path.name.startswith(".") or path.name in EXCLUDED_DIRS:
            continue
        if any((path / marker).exists() for marker in PROJECT_MARKERS):
            projects.append(path)
    return sorted(projects, key=lambda item: item.name.lower())


def collect_issues(projects: list[Path]) -> list[str]:
    issues: list[str] = []
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for project in projects:
        readme_path = project / "README.md"
        if not readme_path.exists():
            issues.append(f"{project.name}: missing README.md")
        if project.name not in root_readme:
            issues.append(f"{project.name}: missing from root README")

    tracked_artifacts = subprocess.run(
        ["git", "ls-files", "--", "*__pycache__*", "*.pyc"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if tracked_artifacts:
        issues.extend(f"generated artifact committed: {path}" for path in tracked_artifacts)

    nested_workflows = [
        path.relative_to(ROOT)
        for path in ROOT.rglob("*.yml")
        if ".github" in path.parts
        and "workflows" in path.parts
        and path.parent != ROOT / ".github" / "workflows"
    ]
    nested_workflows.extend(
        path.relative_to(ROOT)
        for path in ROOT.rglob("*.yaml")
        if ".github" in path.parts
        and "workflows" in path.parts
        and path.parent != ROOT / ".github" / "workflows"
    )
    if nested_workflows:
        issues.extend(f"workflow must live at repo root: {path}" for path in nested_workflows)

    return issues


def main() -> int:
    projects = discover_projects()
    issues = collect_issues(projects)

    print(f"Discovered {len(projects)} project directories:")
    for project in projects:
        print(f" - {project.name}")

    if issues:
        print("\nRepo health issues:")
        for issue in issues:
            print(f" - {issue}")
        return 1

    print("\nRepo health checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
