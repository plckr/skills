"""Validate this collection without installing or executing any skills."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
import yaml


NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
MARKDOWN = MarkdownIt("commonmark")


def validate_metadata(path: Path, errors: list[str]) -> str | None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        errors.append(f"{path}: expected YAML frontmatter delimited by ---")
        return None
    end = lines.index("---", 1)
    try:
        metadata = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as error:
        errors.append(f"{path}: invalid YAML: {error}")
        return None
    if not isinstance(metadata, dict):
        errors.append(f"{path}: frontmatter must be a mapping")
        return None
    name = metadata.get("name")
    if not isinstance(name, str) or len(name) > 64 or not NAME.fullmatch(name):
        errors.append(f"{path}: name must be lowercase words/numbers with single hyphens, at most 64 characters")
        name = None
    elif name != path.parent.name:
        errors.append(f"{path}: name must match directory {path.parent.name!r}")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        errors.append(f"{path}: description must be a nonempty string of at most 1024 characters")
    if not "\n".join(lines[end + 1:]).strip():
        errors.append(f"{path}: instructions must not be empty")
    return name


def validate_links(path: Path, root: Path, errors: list[str]) -> None:
    # Parsing Markdown avoids treating examples in code blocks as real links.
    for block in MARKDOWN.parse(path.read_text(encoding="utf-8")):
        for token in block.children or []:
            if token.type not in {"link_open", "image"}:
                continue
            target = token.attrGet("href" if token.type == "link_open" else "src") or ""
            try:
                url = urlsplit(target)
            except ValueError:
                errors.append(f"{path}: invalid link {target!r}")
                continue
            if url.scheme or url.netloc or not url.path:
                continue
            local_path = unquote(url.path)
            resolved = (path.parent / local_path).resolve()
            if Path(local_path).is_absolute() or not resolved.is_relative_to(root):
                errors.append(f"{path}: local link must stay inside the repository: {target}")
            elif not resolved.exists():
                errors.append(f"{path}: broken local link: {target}")


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    skills = root / "skills"
    if not skills.is_dir():
        return [f"{skills}: missing skills directory"]
    seen: set[str] = set()
    for directory in sorted(skills.iterdir()):
        if directory.name.startswith("."):
            continue
        if not directory.is_dir():
            errors.append(f"{directory}: skills/ must contain skill directories only")
            continue
        path = directory / "SKILL.md"
        if not path.is_file():
            errors.append(f"{directory}: missing SKILL.md")
            continue
        name = validate_metadata(path, errors)
        if name in seen:
            errors.append(f"{path}: duplicate skill name {name!r}")
        if name is not None:
            seen.add(name)
    for path in sorted(skills.rglob("SKILL.md")):
        if path.parent.parent != skills:
            errors.append(f"{path}: skills must be direct children of skills/")
    markdown_files = sorted(skills.rglob("*.md"))
    if (root / "README.md").is_file():
        markdown_files.append(root / "README.md")
    for path in markdown_files:
        validate_links(path, root, errors)
    return errors


if __name__ == "__main__":
    try:
        errors = validate(Path(__file__).resolve().parents[1])
    except (OSError, UnicodeError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        sys.exit(1)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    print("Skill validation passed.")
