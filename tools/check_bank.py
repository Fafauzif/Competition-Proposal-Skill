"""Check the private bank's module structure and portable local hyperlinks."""
import argparse
from pathlib import Path
import re
import tempfile
from urllib.parse import unquote
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'\]\(([^\s)]+)\)')
NAME = re.compile(r"^[a-z][a-z0-9-]{0,62}$")


def local_links(where):
    errors = []
    for path in sorted(where.rglob("*.md")):
        for raw in LINK.findall(path.read_text(encoding="utf-8")):
            if raw.startswith(("#", "http:", "https:", "mailto:")):
                continue
            target = unquote(raw.split("#", 1)[0])
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(where.resolve()) or not resolved.exists():
                errors.append(f"{path.relative_to(where)}: {raw}")
    return errors


def check():
    errors = []
    modules = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if len(modules) != 15:
        errors.append(f"Expected 15 modules, found {len(modules)}")
    for path in modules:
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.S)
        if not NAME.fullmatch(path.parent.name) or not match:
            errors.append(f"Invalid module metadata: {path.parent.name}")
            continue
        metadata = match.group(1)
        if not re.search(rf"(?m)^name: +[\"']?{re.escape(path.parent.name)}[\"']?\s*$", metadata):
            errors.append(f"Module name mismatch: {path.parent.name}")
        if not re.search(r"(?m)^description: +\S", metadata):
            errors.append(f"Missing description: {path.parent.name}")
    errors.extend(local_links(ROOT))
    return errors


def check_bundle(path):
    with ZipFile(path) as bundle, tempfile.TemporaryDirectory() as directory:
        names = bundle.namelist()
        if len(names) != len(set(names)) or bundle.testzip():
            return ["Work bundle contains duplicate paths or corrupt data"]
        roots = [name for name in names if name.endswith("/SKILL.md")]
        guides = [name for name in names if name.endswith("/GUIDE.md")]
        if roots != ["proposal-workflow/SKILL.md"] or len(guides) != 14:
            return [f"Work upload should have one entry point and 14 guides. Found {roots}, {len(guides)}"]
        bundle.extractall(directory)
        return local_links(Path(directory))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path)
    args = parser.parse_args()
    errors = check()
    if args.bundle:
        errors.extend(check_bundle(args.bundle))
    if errors:
        raise SystemExit("\n".join(errors))
    print("15 repository modules and local links checked.")
    if args.bundle:
        print("Work archive checked for integrity, one entry point, 14 companion guides, and local links.")


if __name__ == "__main__":
    main()
