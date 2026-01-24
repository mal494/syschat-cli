import os
import time
import mimetypes
from pathlib import Path

# --- Configuration ---
MAX_FILE_READ_SIZE = 5_000   # 5KB per file
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
            "type": mime_type or "unknown"
        }
    except Exception as e:
        return {"error": str(e)}

def read_file_safe(file_path):
    """Safely reads text content with a size limit."""
    path = Path(file_path)
    
    # 1. Skip if extension not allowed (Basic binary check)
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False, "[Skipped: Unsupported extension]"

    # 2. Skip if individual file is huge
    try:
        if path.stat().st_size > MAX_FILE_READ_SIZE:
             return False, "[Skipped: File too large]"
             
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return True, f.read()
            
    except Exception as e:
        return False, f"[Error reading file: {str(e)}]"

def scan_directory(dir_path):
    """
    Recursively scans a directory.
    Returns: 
    1. tree_str: A visual text representation of the folder structure.
    2. content_agg: A single string containing code/text from all files (up to limit).
    """
    root_path = Path(dir_path)
    
    if not root_path.exists() or not root_path.is_dir():
        return "Error: Path is not a directory", ""

    tree_lines = []
    aggregated_content = []
    total_content_size = 0
    
    # Walk the directory
    for root, dirs, files in os.walk(root_path):
        # Filter out ignored directories (modify dirs in-place to stop recursion)
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        
        level = root.replace(str(root_path), '').count(os.sep)
        indent = ' ' * 4 * level
        sub_dir = os.path.basename(root)
        
        # Add folder to tree
        tree_lines.append(f"{indent}{sub_dir}/")
        
        for f in files:
            file_path = Path(root) / f
            
            # Add file to tree
            tree_lines.append(f"{indent}    {f}")
            
            # Stop reading content if we hit the global limit
            if total_content_size >= MAX_TOTAL_DIR_SIZE:
                continue

            # Read content
            is_text, content = read_file_safe(file_path)
            if is_text:
                header = f"\n--- START FILE: {f} ---\n"
                footer = f"\n--- END FILE: {f} ---\n"
                chunk = header + content + footer
                
                # Check if adding this chunk exceeds limit
                if total_content_size + len(chunk) < MAX_TOTAL_DIR_SIZE:
                    aggregated_content.append(chunk)
                    total_content_size += len(chunk)
                else:
                    aggregated_content.append(f"\n[...Global Context Limit Reached... Skipping {f}]\n")
                    total_content_size = MAX_TOTAL_DIR_SIZE # Force stop

    return "\n".join(tree_lines), "".join(aggregated_content)