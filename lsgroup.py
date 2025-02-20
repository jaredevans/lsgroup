import os
import argparse
import mimetypes
from termcolor import colored
from collections import defaultdict

def format_size(size_in_bytes):
    """Format file size to human-readable format (B, K, M, G, T)."""
    for unit in ['B', 'K', 'M', 'G']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.1f}{unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.1f}T"

def list_directories(directory):
    """List directories in alphabetical order, with hidden directories shown first."""
    hidden_dirs = []
    visible_dirs = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_dir():
                if entry.name.startswith('.'):
                    hidden_dirs.append(entry.name)
                else:
                    visible_dirs.append(entry.name)
    return sorted(hidden_dirs, key=str.casefold), sorted(visible_dirs, key=str.casefold)

def categorize_files(directory):
    """Categorize and group files by type and extension."""
    categories = {
        "Image/Video": defaultdict(list),
        "Document": defaultdict(list),
        "Executable": defaultdict(list),
        "Programming": defaultdict(list),
        "Other": []
    }

    image_video_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".mp4", ".mkv", ".avi", ".mov", ".heic", 
                              ".webp", ".mpg", ".tiff", ".tif", ".svg", ".ico", ".raw", ".mp3", ".wav", ".flac", 
                              ".ogg", ".aac", ".m4a", ".wmv", ".flv", ".3gp", ".m4v", ".vob", ".rm", ".ts"}
    
    document_extensions = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".txt", ".epub", ".csv", ".pcap", 
                           ".pcapng", ".rtf", ".odt", ".ods", ".odp", ".log", ".md", ".ini", ".yaml", ".yml", 
                           ".tex", ".db"}
    
    executable_extensions = {".exe", ".bat", ".sh", ".py", ".pl", ".jar", ".bin", ".cmd", ".php", ".msi", ".deb", 
                             ".rpm", ".apk", ".dmg", ".app", ".run", ".vbs", ".ps1"}
    
    programming_extensions = {".html", ".json", ".pickle", ".sql", ".xml", ".cpp", ".c", ".h", ".hpp", ".java", 
                              ".js", ".jsx", ".ts", ".tsx", ".rb", ".go", ".swift", ".rs", ".kt", ".cs", ".jsp"}

    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_file():
                filepath = entry.path
                file = entry.name
                ext = os.path.splitext(file)[1].lower() or "(no extension)"
                size = entry.stat().st_size
                file_info = (file, size)

                # Categorize based on known extensions
                if ext in image_video_extensions:
                    categories["Image/Video"][ext].append(file_info)
                elif ext in document_extensions:
                    categories["Document"][ext].append(file_info)
                elif ext in executable_extensions or os.access(filepath, os.X_OK):
                    categories["Executable"][ext].append(file_info)
                elif ext in programming_extensions:
                    categories["Programming"][ext].append(file_info)
                else:
                    # Fallback: Guess MIME type
                    mime_type, _ = mimetypes.guess_type(filepath)
                    if mime_type:
                        if mime_type.startswith('image') or mime_type.startswith('video'):
                            categories["Image/Video"][ext].append(file_info)
                        elif mime_type.startswith('application') or mime_type.startswith('text'):
                            categories["Document"][ext].append(file_info)
                        elif mime_type.startswith('application/x-executable'):
                            categories["Executable"][ext].append(file_info)
                        else:
                            categories["Other"].append(file_info)
                    else:
                        categories["Other"].append(file_info)

    # Sort filenames alphabetically within each category
    for category, group in categories.items():
        if category == "Other":
            group.sort(key=lambda x: x[0].casefold())
        else:
            for ext in sorted(group):
                group[ext].sort(key=lambda x: x[0].casefold())

    return categories

def display_directories(hidden_dirs, visible_dirs):
    """Display directories in separate groups: hidden and visible."""
    print("\nDirectories:")
    print("-" * 40)
    if hidden_dirs:
        print("Hidden Directories:")
        for d in hidden_dirs:
            print(f"  {colored(d, 'cyan')}")
    if visible_dirs:
        print("\nVisible Directories:")
        for d in visible_dirs:
            print(f"  {colored(d, 'yellow')}")

def display_summary(categories):
    """Display a summary of categorized files."""
    print("\nSummary:")
    print(f"{'Category':<15}{'Count':<10}{'Total Size':<15}")
    print("-" * 40)
    for category, group in categories.items():
        count = sum(len(files) for files in group.values()) if category != "Other" else len(group)
        total_size = sum(size for ext in group for _, size in group[ext]) if category != "Other" else sum(size for _, size in group)
        if count > 0:
            print(f"{category:<15}{count:<10}{format_size(total_size):<15}")

def display_files(categories):
    """Display files grouped by type, sorted by extension and filename."""
    print("-" * 40)
    for category, group in categories.items():
        if category == "Other" and not group:
            continue
        if category != "Other" and not any(group.values()):
            continue

        print(f"\n{category} Files:")
        if category == "Other":
            for file, size in group:
                print(f"  {format_size(size):<10} {colored(file, 'blue'):<50}")
        elif category == "Image/Video":
            for ext in sorted(group, key=str.casefold):
                if group[ext]:
                    print(f"  Files with extension {ext}:")
                    for file, size in group[ext]:
                        print(f"    {format_size(size):<10} {colored(file, 'magenta'):<50}")
        else:
            for ext in sorted(group, key=str.casefold):
                if group[ext]:
                    print(f"  Files with extension {ext}:")
                    for file, size in group[ext]:
                        print(f"    {format_size(size):<10} {colored(file, 'green'):<50}")

# Argument parsing
parser = argparse.ArgumentParser(description="Categorize files in a directory.")
parser.add_argument("directory", nargs="?", default=os.getcwd(), help="Directory to scan")
args = parser.parse_args()

# Main Execution
current_directory = args.directory
print(f"\nScanning Directory: {current_directory}")

hidden_dirs, visible_dirs = list_directories(current_directory)
display_directories(hidden_dirs, visible_dirs)

categories = categorize_files(current_directory)
display_files(categories)
display_summary(categories)
