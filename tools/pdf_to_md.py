import argparse
import json
import os
import sys
from pathlib import Path
# pyrefly: ignore [missing-import]
from markitdown import MarkItDown

# Ensure UTF-8 output encoding for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def is_excluded(path: Path, exclude_patterns: list) -> bool:
    for pattern in exclude_patterns:
        if pattern.lower() in [part.lower() for part in path.parts]:
            return True
        if pattern.lower() in str(path).lower():
            return True
    return False


def convert_pdf_file(pdf_path: Path, output_path: Path, overwrite: bool = False, converter: MarkItDown = None) -> dict:
    if output_path.exists() and output_path.stat().st_size > 0 and not overwrite:
        return {
            "input": str(pdf_path),
            "output": str(output_path),
            "status": "skipped",
            "reason": "Target Markdown file already exists"
        }

    if converter is None:
        converter = MarkItDown()

    try:
        res = converter.convert(str(pdf_path))
        content = res.text_content if hasattr(res, "text_content") else ""
        if not content and hasattr(res, "markdown"):
            content = res.markdown or ""

        output_path.write_text(content, encoding="utf-8")
        return {
            "input": str(pdf_path),
            "output": str(output_path),
            "status": "converted",
            "bytes": output_path.stat().st_size
        }
    except Exception as exc:
        return {
            "input": str(pdf_path),
            "output": str(output_path),
            "status": "failed",
            "error": str(exc)
        }


def process_target(target_path: Path, output_dir: Path = None, recursive: bool = True, exclude_patterns: list = None, overwrite: bool = False, extensions: list = None) -> dict:
    if exclude_patterns is None:
        exclude_patterns = ["Contenido complementario"]

    if extensions is None:
        extensions = [".pdf", ".docx", ".xlsx", ".pptx"]
    extensions = [ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in extensions]

    if not target_path.exists():
        return {
            "success": False,
            "error": f"Path does not exist: {target_path}",
            "total": 0,
            "converted": 0,
            "skipped": 0,
            "failed": 0,
            "results": []
        }

    files_to_process = []
    if target_path.is_file():
        if target_path.suffix.lower() in extensions and not is_excluded(target_path, exclude_patterns):
            files_to_process.append(target_path)
    elif target_path.is_dir():
        pattern = "**/*" if recursive else "*"
        for p in target_path.glob(pattern):
            if p.is_file() and p.suffix.lower() in extensions:
                if not is_excluded(p, exclude_patterns):
                    files_to_process.append(p)

    results = []
    converted_count = 0
    skipped_count = 0
    failed_count = 0

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    converter = MarkItDown()

    for doc_file in files_to_process:
        if output_dir:
            out_file = output_dir / doc_file.with_suffix(".md").name
        else:
            out_file = doc_file.with_suffix(".md")

        res = convert_pdf_file(doc_file, out_file, overwrite=overwrite, converter=converter)
        results.append(res)
        if res["status"] == "converted":
            converted_count += 1
        elif res["status"] == "skipped":
            skipped_count += 1
        else:
            failed_count += 1

    return {
        "success": True,
        "total": len(files_to_process),
        "converted": converted_count,
        "skipped": skipped_count,
        "failed": failed_count,
        "results": results
    }


def main():
    parser = argparse.ArgumentParser(description="Convert PDF and Office documents to Markdown using Microsoft MarkItDown.")
    parser.add_argument("path", help="Path to a document file or directory containing documents")
    parser.add_argument("--output-dir", "-o", help="Directory where converted Markdown files will be placed")
    parser.add_argument("--ext", nargs="*", default=None, help="File extensions to convert (default: .pdf, .docx, .xlsx, .pptx)")
    parser.add_argument("--no-recursive", dest="recursive", action="store_false", help="Do not search directories recursively")
    parser.add_argument("--exclude-dir", nargs="*", default=["Contenido complementario"], help="Folder names to exclude")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing Markdown files")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    parser.set_defaults(recursive=True)
    args = parser.parse_args()

    target = Path(args.path).resolve()
    out_dir = Path(args.output_dir).resolve() if args.output_dir else None
    summary = process_target(
        target,
        output_dir=out_dir,
        recursive=args.recursive,
        exclude_patterns=args.exclude_dir,
        overwrite=args.overwrite,
        extensions=args.ext
    )

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(f"Processed: {target}")
        if out_dir:
            print(f"Output Directory: {out_dir}")
        print(f"Total: {summary['total']} | Converted: {summary['converted']} | Skipped: {summary['skipped']} | Failed: {summary['failed']}")
        for item in summary["results"]:
            status = item["status"].upper()
            src_name = Path(item["input"]).name
            if status == "CONVERTED":
                print(f"  [OK] {src_name} -> {Path(item['output']).name} ({item.get('bytes', 0):,} bytes)")
            elif status == "SKIPPED":
                print(f"  [SKIP] {src_name} (already exists)")
            else:
                print(f"  [ERR] {src_name}: {item.get('error')}")

    if summary["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
