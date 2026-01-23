from pathlib import Path

def parse_log_file(file_path, max_lines=50):
    """
    Parses a log file and extracts lines containing specific keywords.
    
    Args:
        file_path (str): The path to the log file.
        max_lines (int): The maximum number of relevant lines to return.
        
    Returns:
        list: A list of strings containing the matching log lines.
    """
    path = Path(file_path)
    
    if not path.exists() or not path.is_file():
        return []
        
    keywords = ["ERROR", "WARN", "CRITICAL"]
    results = []
    
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if any(keyword in line for keyword in keywords):
                    results.append(line.strip())
                    if len(results) >= max_lines:
                        break
    except Exception:
        # In case of any read error, return what we have so far or empty
        return results
        
    return results
