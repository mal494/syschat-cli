import os
import time
import mimetypes
from pathlib import Path

from log_parser import parse_log_file

# --- Configuration ---
MAX_FILE_READ_SIZE = 5_000    # 5KB per file
MAX_TOTAL_DIR_SIZE = 12_000   # 12KB total context limit for directories
ALLOWED_EXTENSIONS = {
    '.txt', '.md', '.py', '.js', '.json', '.csv',
    '.log', '.yml', '.yaml', '.html', '.css', '.sh', '.env'
}
IGNORED_DIRS = {'.git', '.venv', '__pycache__', '.vscode', 'node_modules', '.idea'}


def get_file_metadata(file_path):
    """Retrieves technical stats for a single file."""
    path = Path(file_path)

    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    try:
        stats = path.stat()
        created = time.ctime(stats.st_ctime)
        modified = time.ctime(stats.st_mtime)
        perms = oct(stats.st_mode)[-3:]
        mime_type, _ = mimetypes.guess_type(path)

        return {
            "filename": path.name,
            "path": str(path.resolve()),
            "size_bytes": stats.st_size,
            "size_readable": f"{stats.st_size / 1024:.2f} KB",
            "created": created,
            "modified": modified,
            "permissions": perms,
            "type": mime_type or "unknown",
            "is_log_file": path.suffix.lower() == '.log'
        }
    except Exception as e:
        return {"error": str(e)}


def read_file_safe(file_path, file_size=None):
    """
    Safely reads text content with a size limit.

    Args:
        file_path: Path to the file to read.
        file_size: Optional pre-computed size in bytes. If omitted, the file's
                   actual size is used for the limit check.
    """
    path = Path(file_path)

    # 1. Check size limit first (using passed size if available, else stat the file)
    try:
        size_to_check = file_size if file_size is not None else path.stat().st_size
    except OSError:
        size_to_check = 0

    if size_to_check > MAX_FILE_READ_SIZE:
        return False, "[Skipped: File too large]"

    # 2. Skip unsupported / likely-binary extensions
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False, "[Skipped: File type likely binary]"

    # 3. For log files, return only the relevant filtered entries
    if path.suffix.lower() == '.log':
        entries = parse_log_file(str(path))
        if entries:
            return True, "Relevant log entries found:\n" + "\n".join(entries)
        return True, "[No relevant log entries found]"

    # 4. Read normally
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return True, f.read()
    except Exception as e:
        return False, f"[Error reading file: {str(e)}]"


def scan_directory(dir_path):
    """
    Recursively scans a directory.
    Returns:
        tree_str: A visual text representation of the folder structure.
        content_agg: A single string containing code/text from all files (up to limit).
    """
    root_path = Path(dir_path)

    if not root_path.exists() or not root_path.is_dir():
        return "Error: Path is not a directory", ""

    tree_lines = []
    aggregated_content = []
    total_content_size = 0

    for root, dirs, files in os.walk(root_path):
        # Filter out ignored directories (modify dirs in-place to stop recursion)
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        level = root.replace(str(root_path), '').count(os.sep)
        indent = ' ' * 4 * level
        sub_dir = os.path.basename(root)

        tree_lines.append(f"{indent}{sub_dir}/")

        for f in files:
            file_path = Path(root) / f
            tree_lines.append(f"{indent}    {f}")

            if total_content_size >= MAX_TOTAL_DIR_SIZE:
                continue

            is_text, content = read_file_safe(file_path)
            if is_text:
                header = f"\n--- START FILE: {f} ---\n"
                footer = f"\n--- END FILE: {f} ---\n"
                chunk = header + content + footer

                if total_content_size + len(chunk) < MAX_TOTAL_DIR_SIZE:
                    aggregated_content.append(chunk)
                    total_content_size += len(chunk)
                else:
                    aggregated_content.append(f"\n[...Global Context Limit Reached... Skipping {f}]\n")
                    total_content_size = MAX_TOTAL_DIR_SIZE

    return "\n".join(tree_lines), "".join(aggregated_content)
