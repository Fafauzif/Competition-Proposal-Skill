"""Rebuild the single-entry ChatGPT Work upload from the private repository."""
import argparse
from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
ENTRY = "proposal-workflow"
LARGE_MODELS = {
    "Gotong_Sampah.pdf": "https://github.com/Fafauzif/Essay-Studio/blob/8fddfff968f492a1f13dc0bb7f97ca78bd09980a/library/originals/essays/Gotong-Sampah.pdf",
    "ReGenCity_Grid_Indonesia.docx": "https://github.com/Fafauzif/Essay-Studio/tree/8fddfff968f492a1f13dc0bb7f97ca78bd09980a/library/originals/templates",
}


def usable_files(folder):
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder)
        if path.is_file() and not any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
            yield path, relative


def guide_links(text):
    return re.sub(r"(?<=/)SKILL\.md(?=[)#\x60\s])", "GUIDE.md", text)


def reference_links(text):
    for name, url in LARGE_MODELS.items():
        text = re.sub(r"(?<=\()(?:(?:\.\./)*references/)?examples/" + re.escape(name) + r"(?=\))", url, text)
    return text


def build(destination, include_all_models=False):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for path, relative in usable_files(ROOT / "skills"):
            if relative.parts[0] == ENTRY:
                if relative.as_posix() == f"{ENTRY}/SKILL.md":
                    text = (path.read_text(encoding="utf-8")
                            .replace("](../", "](bank/skills/")
                            .replace("](bank/skills/../references/", "](bank/references/"))
                    text = guide_links(text)
                    archive.writestr(f"{ENTRY}/SKILL.md", text)
                else:
                    archive.write(path, f"{ENTRY}/{Path(*relative.parts[1:]).as_posix()}")
                continue
            name = relative.as_posix()
            if path.name == "SKILL.md":
                name = relative.with_name("GUIDE.md").as_posix()
            target = f"{ENTRY}/bank/skills/{name}"
            if path.suffix == ".md":
                text = guide_links(path.read_text(encoding="utf-8"))
                if not include_all_models:
                    text = reference_links(text)
                archive.writestr(target, text)
            else:
                archive.write(path, target)

        for path, relative in usable_files(ROOT / "references"):
            if not include_all_models and path.name in LARGE_MODELS:
                continue
            target = f"{ENTRY}/bank/references/{relative.as_posix()}"
            if not include_all_models and path.suffix == ".md":
                archive.writestr(target, reference_links(path.read_text(encoding="utf-8")))
            else:
                archive.write(path, target)

        for path, relative in usable_files(ROOT / "notices"):
            archive.write(path, f"{ENTRY}/bank/notices/{relative.as_posix()}")

    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "chatgpt-work" / "proposal-workflow.zip")
    parser.add_argument("--include-all-models", action="store_true")
    args = parser.parse_args()
    print(build(args.output, args.include_all_models))


if __name__ == "__main__":
    main()
