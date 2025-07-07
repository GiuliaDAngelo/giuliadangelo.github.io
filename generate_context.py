#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
import fnmatch # For wildcard matching similar to shell

# --- Configuration ---
# Use Path objects for easier manipulation
PROJECT_ROOT = Path(".").resolve()  # Get absolute path of current dir

# Output files (relative to PROJECT_ROOT, placed in tmp/)
TMP_DIR = PROJECT_ROOT / "tmp"
FULL_OUTPUT_FILE = TMP_DIR / "output_full.txt"
DIFF_OUTPUT_FILE = TMP_DIR / "output_diff.txt"
LAYOUTS_OUTPUT_FILE = TMP_DIR / "output_layouts.txt"

# Directories containing third-party/vendored libraries.
# Files within these dirs will be listed by path but their content won't be included.
PACKAGED_LIB_DIRS = [
    "assets/bootstrap-4.5.2",
    "static/plugins",
]

# Files/Directories to EXCLUDE from all processing
# 'public' is excluded from the general scan, but HTMLs can be added back specifically
EXCLUDED_DIRS = [
    ".git",
    "node_modules",
    "tmp",
    # Images are now handled by the IMAGE_EXTENSIONS check,
    # but you can still exclude large top-level image directories if needed.
    # e.g., "exampleSite/static/images",
    ".idea",
    ".vscode",
    "public", # Excluded from general scan; HTMLs added specifically if flag is set
    "resources", # Hugo's generated resource cache
    "__pycache__",
    ".venv",
    "venv",
]

# Specific file patterns/names to EXCLUDE (matched anywhere)
EXCLUDED_FILES_PATTERNS = [
    ".DS_Store",
    "hugo_stats.json",
    ".hugo_build.lock",
    str(FULL_OUTPUT_FILE.name),
    str(DIFF_OUTPUT_FILE.name),
    str(LAYOUTS_OUTPUT_FILE.name),
    "*.pyc",
    "*~", # Backup files
    "package-lock.json",
    # Exclude minified and map files to reduce noise
    "*.min.js",
    "*.min.css",
    "*.js.map",
    "*.css.map",
]

# Common image file extensions
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico"}

# File patterns/names to INCLUDE (if not excluded above)
INCLUDE_PATTERNS = [
    "*.html",
    "*.md",
    "*.toml",
    "*.json",
    "*.yaml",
    "*.yml",
    "*.scss",
    "*.js",
    "*.py",
    "*.sh",
    ".gitignore",
    "Dockerfile",
    "LICENSE",
    "README.md",
    "go.mod",
    "go.sum",
    "package.json",
    "nginx.conf",
    # Add image patterns explicitly so they can be identified
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.svg", "*.ico",
]
# --- End Configuration ---

def log(message):
    """Prints a formatted log message to stderr."""
    print(f"[CONTEXT GEN] {message}", file=sys.stderr)

def should_ignore(path: Path, root: Path) -> bool:
    """Checks if a given path should be ignored based on config."""
    # Check against excluded directories
    try:
        relative_path = path.relative_to(root)
        # Check if the path or any of its parents match an excluded directory
        for part in relative_path.parts:
            # Reconstruct path parts to check against top-level exclusions
            if part in EXCLUDED_DIRS:
                 # This check is basic; for `foo/bar` vs `bar`, it might misfire.
                 # A more robust check compares full initial path segments.
                 pass
        # A better check for top-level directories
        if any(relative_path.is_relative_to(ex_dir) for ex_dir in EXCLUDED_DIRS):
            return True
    except ValueError: # pragma: no cover
        # This can happen if path is not within root, e.g. a symlink pointing outside
        pass

    # Check against excluded file patterns
    for pattern in EXCLUDED_FILES_PATTERNS:
        if fnmatch.fnmatch(path.name, pattern):
            return True
    return False

def is_packaged_library_file(path: Path, root: Path) -> bool:
    """Checks if a file is part of a packaged library directory."""
    try:
        relative_path_str = str(path.relative_to(root).as_posix())
        for lib_dir in PACKAGED_LIB_DIRS:
            if relative_path_str.startswith(lib_dir):
                return True
    except ValueError:
        pass
    return False

def should_include(filename: str) -> bool:
    """Checks if a filename matches any include pattern."""
    for pattern in INCLUDE_PATTERNS:
        if fnmatch.fnmatch(filename.lower(), pattern.lower()): # Case-insensitive match for patterns
            return True
    return False

def find_relevant_files(root: Path, checkpoint_mtime: float | None = None, mode: str = "full", with_public_html: bool = False) -> list[Path]:
    """
    Walks the directory tree, applying include/exclude rules.
    If checkpoint_mtime is provided, only includes files newer than it.
    If mode is "layouts", filters for files within "layouts" directories.
    If with_public_html is True and mode is "full", also includes HTML files from ./public.
    """
    initial_candidates = set() # Use a set to handle potential overlaps gracefully

    log(f"Scanning directory: {root} for mode '{mode}' (main scan)")
    if checkpoint_mtime:
        log(f"Filtering for files newer than: {datetime.fromtimestamp(checkpoint_mtime)}")

    for current_dir_str, dir_names, file_names in os.walk(root, topdown=True):
        current_path = Path(current_dir_str)

        # Pruning: Modify dir_names IN-PLACE to avoid descending into excluded directories.
        dir_names[:] = [d for d in dir_names if not any( (current_path/d).is_relative_to(root/ex_dir) for ex_dir in EXCLUDED_DIRS )]


        for filename in file_names:
            file_path = current_path / filename

            if should_ignore(file_path, root):
                continue

            if not should_include(filename):
                continue

            if checkpoint_mtime:
                try:
                    if file_path.stat().st_mtime <= checkpoint_mtime:
                        continue
                except OSError as e:
                    log(f"Warning: Could not stat file {file_path}: {e}. Skipping.")
                    continue
            initial_candidates.add(file_path.resolve()) # Store absolute paths

    log(f"Found {len(initial_candidates)} candidate files from main scan.")

    # Targeted scan for public HTML files if requested and in 'full' mode
    if with_public_html and mode == "full":
        log("Scanning 'public' directory for HTML files due to --with-public-html.")
        public_dir = root / "public"
        public_html_added_count = 0
        if public_dir.is_dir():
            for item in public_dir.rglob('*.html'): # rglob for recursive search
                if item.is_file() and not should_ignore(item, root):
                    public_file_path = item.resolve() # Ensure absolute path
                    # Apply mtime filter for public HTML files too, if diff mode were to use this
                    if checkpoint_mtime:
                        try:
                            if public_file_path.stat().st_mtime <= checkpoint_mtime:
                                continue
                        except OSError as e:
                            log(f"Warning: Could not stat file {public_file_path}: {e}. Skipping.")
                            continue

                    if public_file_path not in initial_candidates: # Add if not already picked up
                        initial_candidates.add(public_file_path)
                        public_html_added_count +=1
            log(f"Added {public_html_added_count} HTML files from 'public' directory.")
        else:
            log(f"'public' directory not found at {public_dir}")

    # Filter based on mode
    final_relevant_files_list = []
    if mode == "layouts":
        log("Filtering for files in 'layouts' directories.")
        for file_path in initial_candidates: # Iterate over the set
            # A file is in a layouts directory if "layouts" is any part of its path relative to root
            if "layouts" in file_path.relative_to(root).parts:
                 final_relevant_files_list.append(file_path)
        log(f"Found {len(final_relevant_files_list)} files after 'layouts' filter.")
    else:
        final_relevant_files_list = list(initial_candidates)

    final_relevant_files_list.sort()
    log_message_suffix = ""
    if with_public_html and mode == "full":
        log_message_suffix = " (including public HTML)"
    log(f"Found {len(final_relevant_files_list)} relevant files in total for mode '{mode}'{log_message_suffix}.")
    return final_relevant_files_list


def generate_header(mode: str, checkpoint_file: Path | None = None, with_public_html: bool = False) -> str:
    """Generates the header content for the output file."""
    common_instructions = """
**Instructions for AI:**
1.  **Analyze Structure:** Understand the Hugo project layout (config, content, layouts, assets, static structure).
2.  **Focus on Code/Config:** Pay close attention to Hugo templates (.html), SCSS (.scss), JavaScript (.js), configuration files (.toml, .yaml, .json), Go module files (go.mod, go.sum), and Node config (package.json).
3.  **Understand Content:** Review markdown content files (.md) for site text and structure.
4.  **Identify Customizations:** Note custom logic in layouts, partials, shortcodes, SCSS, and JS compared to standard Hugo/theme practices.
5.  **Note Dependencies:** Identify key dependencies from go.mod/go.sum and package.json.
6.  **Library & Image Files:** Files listed as `=== LIBRARY FILE: ... ===` or `=== IMAGE FILE: ... ===` are pointers to third-party code or binary assets. Their content is NOT included, but their existence and path are important context.
7.  **Ignore Irrelevant Data:** Skip over binary data representations or verbose dependency code if accidentally included. Focus on the content provided below.
8.  **Primary Goal:** Use this information to answer questions about the website's implementation, structure, features, styling, configuration, and potential areas for improvement or troubleshooting.
9.  Provide Code with focus toward with minimal commenting
10. dont include {{{{/* comments */}}}}, every time it confuses hugo and causes errors
11. If we are copying or moving files, provide the bash command to accomplish this
12. We don't need to make backups of files before big edits - there is sufficient rollback capability in dev environment
"""
    if mode == "diff":
        checkpoint_ts_str = "ERROR: Checkpoint file missing!"
        if checkpoint_file and checkpoint_file.exists():
            checkpoint_mtime = checkpoint_file.stat().st_mtime
            checkpoint_ts = datetime.fromtimestamp(checkpoint_mtime)
            checkpoint_ts_str = checkpoint_ts.strftime('%Y-%m-%d %H:%M:%S %Z')

        return f"""--- START OF PROJECT CONTEXT UPDATE  ---

This file contains ONLY the content of key files that have been MODIFIED since the last full context checkpoint was generated. Library and image files are listed by path only.

**Checkpoint File:** {checkpoint_file.relative_to(PROJECT_ROOT) if checkpoint_file else 'N/A'}
**Checkpoint Timestamp:** {checkpoint_ts_str}
{common_instructions.replace("1.  Analyze Structure...", "1.  **Apply Updates:** Use the content below to update your understanding of the project based on the changes since the checkpoint timestamp. Prioritize this information when it conflicts with previous context from the full checkpoint. Remember this is NOT the full project, only the changed files. Refer back to the full checkpoint if needed for unchanged files or broader structure.")}
--- MODIFIED FILE CONTENTS START ---
"""
    elif mode == "layouts":
        return f"""--- START OF PROJECT CONTEXT (Layouts Only) ---

This file contains the content of files found within all 'layouts' directories in the project. Library and image files are listed by path only.

**Project Root:** {PROJECT_ROOT}
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}
{common_instructions.replace("1.  Analyze Structure...", "1.  **Analyze Templates:** Understand the project's templating structure. Focus on HTML/Template Structure and logic. Consider how these layouts would render content from other parts of the project.")}
--- LAYOUT FILE CONTENTS START ---
"""
    else: # mode == "full"
        public_html_note = ""
        if with_public_html: # This flag is only relevant for 'full' mode in terms of output content
            public_html_note = "\n**Note:** HTML files from the 'public' directory are also included in this context if the `--with-public-html` flag was used."

        return f"""--- START OF PROJECT CONTEXT (Full Checkpoint) ---

This file contains the content of key configuration, source code, layout, and content files for the project. Library and image files are listed by path only. This serves as a full checkpoint.{public_html_note}

**Project Root:** {PROJECT_ROOT}
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}
{common_instructions}
--- FILE CONTENTS START ---
"""

def generate_footer(mode: str) -> str:
    """Generates the footer content."""
    if mode == "diff":
        return "\n--- END OF PROJECT CONTEXT UPDATE ---"
    elif mode == "layouts":
        return "\n--- END OF PROJECT LAYOUTS CONTEXT ---"
    else: # mode == "full"
        return "\n--- END OF PROJECT CONTEXT ---"

def create_context_file(mode: str, with_public_html: bool):
    """Main function to generate the context file based on the mode."""
    log(f"Project Root: {PROJECT_ROOT}")
    checkpoint_mtime = None
    target_output_file = None

    if mode == "full":
        target_output_file = FULL_OUTPUT_FILE
        log(f"Mode: Generating FULL context checkpoint -> {target_output_file.relative_to(PROJECT_ROOT)}")
        if with_public_html:
            log("Including HTML files from 'public' directory.")
    elif mode == "diff":
        target_output_file = DIFF_OUTPUT_FILE
        log(f"Mode: Generating DIFF context based on {FULL_OUTPUT_FILE.relative_to(PROJECT_ROOT)} -> {target_output_file.relative_to(PROJECT_ROOT)}")
        if not FULL_OUTPUT_FILE.exists():
            log(f"Error: Checkpoint file '{FULL_OUTPUT_FILE}' not found. Please run with --full first.")
            sys.exit(1)
        try:
            checkpoint_mtime = FULL_OUTPUT_FILE.stat().st_mtime
        except OSError as e:
             log(f"Error: Could not read checkpoint file timestamp {FULL_OUTPUT_FILE}: {e}")
             sys.exit(1)
        if with_public_html:
            log("Note: --with-public-html is typically used with --full. For --diff, it will include public HTML files modified since the checkpoint if any.")
    elif mode == "layouts":
        target_output_file = LAYOUTS_OUTPUT_FILE
        log(f"Mode: Generating LAYOUTS context -> {target_output_file.relative_to(PROJECT_ROOT)}")
        if with_public_html:
            log("Warning: --with-public-html is not typically used with --layouts mode and will have no effect on adding public HTML files.")
    else:
        log(f"Error: Invalid mode '{mode}'")
        sys.exit(1)

    try:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        log(f"Error: Could not create output directory {TMP_DIR}: {e}")
        sys.exit(1)

    files_to_process = find_relevant_files(PROJECT_ROOT, checkpoint_mtime, mode=mode, with_public_html=with_public_html)

    log(f"Generating context file: {target_output_file.relative_to(PROJECT_ROOT)}")
    header = generate_header(mode, FULL_OUTPUT_FILE if mode == "diff" else None, with_public_html if mode == "full" else False)
    footer = generate_footer(mode)

    try:
        with open(target_output_file, "w", encoding="utf-8") as outfile:
            outfile.write(header + "\n")

            for file_path in files_to_process:
                relative_path = file_path.relative_to(PROJECT_ROOT)
                file_extension = file_path.suffix.lower()

                # Check for packaged library files first
                if is_packaged_library_file(file_path, PROJECT_ROOT):
                    log(f"  Listing library file: {relative_path.as_posix()}")
                    outfile.write(f"\n=== LIBRARY FILE: {relative_path.as_posix()} ===\n")
                elif file_extension in IMAGE_EXTENSIONS:
                    log(f"  Listing image: {relative_path.as_posix()}")
                    outfile.write(f"\n=== IMAGE FILE: {relative_path.as_posix()} ===\n")
                else:
                    log(f"  Adding content of: {relative_path.as_posix()}")
                    outfile.write(f"\n=== {relative_path.as_posix()} ===\n")
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        outfile.write(content)
                    except Exception as e:
                        log(f"Warning: Failed to read content from {relative_path}: {e}")
                        outfile.write(f"--- FAILED TO READ/DECODE {relative_path.as_posix()} ---")
                    outfile.write("\n")

            outfile.write(footer + "\n")

    except IOError as e:
        log(f"Error: Could not write to output file {target_output_file}: {e}")
        sys.exit(1)

    file_size = target_output_file.stat().st_size
    log(f"Successfully generated context file: {target_output_file.relative_to(PROJECT_ROOT)} ({file_size} bytes)")

    if not files_to_process:
         log("Warning: No files matched the criteria to be included in the output.")
    elif file_size < 1000 and (mode == 'full' or mode == 'layouts'):
         log(f"Warning: The generated {mode} context is very small. Please verify contents and include/exclude rules.")


def main():
    """Parses command line arguments and runs the script."""
    parser = argparse.ArgumentParser(
        description="Generate a context file with project source code for AI analysis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  Generate a full context checkpoint:
    {sys.argv[0]} --full

  Generate a full context checkpoint and include HTML files from the 'public' directory:
    {sys.argv[0]} --full --with-public-html

  Generate a context file with changes since the last full checkpoint:
    {sys.argv[0]} --diff

  Generate a context file with only content from 'layouts' directories:
    {sys.argv[0]} --layouts
"""
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f", "--full",
        action="store_const",
        const="full",
        dest="mode",
        help=f"Generate the full project context checkpoint ({FULL_OUTPUT_FILE.relative_to(PROJECT_ROOT)})."
    )
    group.add_argument(
        "-d", "--diff",
        action="store_const",
        const="diff",
        dest="mode",
        help=f"Generate context with files modified since the last full checkpoint ({DIFF_OUTPUT_FILE.relative_to(PROJECT_ROOT)})."
    )
    group.add_argument(
        "-l", "--layouts",
        action="store_const",
        const="layouts",
        dest="mode",
        help=f"Generate context with files from 'layouts' directories only ({LAYOUTS_OUTPUT_FILE.relative_to(PROJECT_ROOT)})."
    )
    parser.add_argument(
        "--with-public-html",
        action="store_true",
        help="Additionally include HTML files from the 'public' directory (primarily affects --full mode)."
    )

    args = parser.parse_args()
    create_context_file(args.mode, args.with_public_html)

if __name__ == "__main__":
    main()