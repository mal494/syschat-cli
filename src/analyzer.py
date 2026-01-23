import os
import time
import mimetypes
from pathlib import Path
from log_parser import parse_log_file

# Safety Configuration
MAX_READ_SIZE = 10_000  # Read only the first 10KB
ALLOWED_EXTENSIONS = {
    '.txt', '.md', '.py', '.js', '.json', '.csv', 
    '.log', '.yml', '.yaml', '.html', '.css', '.sh'
}

def get_file_metadata(file_path):
    """
    Retrieves technical stats for a file.
    Returns a dictionary of metadata or an error dict.
    """
    path = Path(file_path)
    
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    if not path.is_file():
        return {"error": f"Path is not a file: {file_path}"}

    try:
        stats = path.stat()
        
        # Convert timestamps to readable format
        created = time.ctime(stats.st_ctime)
        modified = time.ctime(stats.st_mtime)
        
        # Get permissions in octal (e.g., '644')
        perms = oct(stats.st_mode)[-3:]
        
        # Guess MIME type (e.g., 'text/plain', 'image/png')
        mime_type, _ = mimetypes.guess_type(path)

        is_log = path.suffix.lower() == '.log'

        return {
            "filename": path.name,
            "absolute_path": str(path.resolve()),
            "size_bytes": stats.st_size,
            "size_readable": f"{stats.st_size / 1024:.2f} KB",
            "created_at": created,
            "last_modified": modified,
            "permissions_octal": perms,
            "mime_type": mime_type or "unknown",
            "is_log_file": is_log
        }
    except PermissionError:
        return {"error": "Permission denied: Cannot access file stats."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def read_file_safe(file_path, file_size):
    """
    Safely reads text content. 
    Returns: (success_boolean, content_string_or_reason)
    """
    path = Path(file_path)
    
    # Safety Check 1: Size Limit
    if file_size > MAX_READ_SIZE:
        return False, "(Content omitted: File is too large for context window)"

    # Safety Check 2: Extension Whitelist
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False, "(Content omitted: File type likely binary or unsupported)"

    try:
        # Special handling for log files
        if path.suffix.lower() == '.log':
            parsed_lines = parse_log_file(str(path))
            if parsed_lines:
                content = "Relevant log entries found:\n" + "\n".join(parsed_lines)
                return True, content
            else:
                return True, "(Log file analyzed: No critical errors or warnings found.)"

        # 'errors=replace' ensures we don't crash on a stray weird character
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            return True, content
    except Exception as e:
        return False, f"(Content omitted: Read error - {str(e)})"
