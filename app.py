import os
import re
import ast
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import hashlib

INPUT_DIR = "input"
OUTPUT_DIR = "output"

class CodeBlockExtractor:
    """
    Intelligently extracts code blocks from markdown files with smart file naming.
    Supports various comment formats and generates meaningful filenames when needed.
    Now includes file tree parsing to map code blocks to correct locations.
    """
    
    # Patterns for extracting filenames from comments
    FILENAME_PATTERNS = [
        # "# New file: src/agent_alerting.py"
        r'#\s*New\s+file\s*:\s*([\w/\.\-]+)',
        # "# In agent1_harvest.py" or "# In agent5_llm.py - add citation"
        r'#\s*In\s+([\w/\.\-]+)',
        # "# Add to agent1_harvest.py"
        r'#\s*Add\s+to\s+([\w/\.\-]+)',
        # "# Replace agent2_filter_dedupe.py with:"
        r'#\s*Replace\s+([\w/\.\-]+)',
        # "# File: src/something.py"
        r'#\s*File\s*:\s*([\w/\.\-]+)',
        # "# agent_something.py"
        r'#\s*([\w/]+\.(?:py|js|ts|tsx|jsx|java|cpp|c|h|go|rs|rb|php|sh))',
    ]
    
    def __init__(self, input_dir: str = INPUT_DIR, output_dir: str = OUTPUT_DIR):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.code_block_counter = {}  # Track unnamed blocks per file
        self.file_tree_map = {}  # Maps filenames to their full paths from file tree
        self.file_versions = {}  # Track multiple versions of the same file
        self.modification_strategy = 'all_versions'  # 'all_versions', 'latest_only', or 'separate_modifications'
        
    def extract_code_blocks(self, md_path: str) -> List[Tuple[str, str, str, str]]:
        """
        Extract code blocks from markdown file.
        Returns: List of (filename, code, language, modification_type) tuples
        modification_type: 'new', 'replace', 'add_to', 'modify', 'generated'
        """
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # First, parse any file trees in the markdown to build a map
        self._parse_file_trees(content)
        
        # Pattern to match code blocks with optional language specifier
        pattern = re.compile(
            r'```([a-zA-Z0-9_#+-]*)\n([\s\S]+?)```',
            re.MULTILINE
        )
        
        results = []
        for match in pattern.finditer(content):
            language = match.group(1).strip() or 'txt'
            code = match.group(2).rstrip()
            
            if not code.strip():
                continue
            
            # Look for section header before this code block
            context_before = content[:match.start()]
            header_filename = self._extract_filename_from_header(context_before)
            
            # Extract filename and modification type from code or generate one
            filename, mod_type = self._extract_or_generate_filename_with_type(code, language, md_path, header_filename)
            
            if filename:
                # Track this version of the file
                self._track_file_version(filename, code, language, mod_type)
                results.append((filename, code, language, mod_type))
        
        return results
    
    def _parse_file_trees(self, content: str):
        """
        Parse file tree structures from markdown content.
        Supports multiple formats:
        - project/
          - src/
            - file.py
        - project/src/file.py
        - ├── src/
        - │   ├── file.py
        """
        lines = content.split('\n')
        current_path_stack = []
        in_tree = False
        
        for line in lines:
            # Skip empty lines but keep tracking tree state
            if not line.strip():
                if in_tree:
                    current_path_stack = []
                    in_tree = False
                continue
            
            # Try tree character patterns (├──, └──, │ etc.)
            # Count leading spaces and tree chars to determine indent
            match = re.match(r'^([\s│]*)(├──|└──)\s*(.+?)/?$', line)
            if match:
                in_tree = True
                prefix = match.group(1)
                name = match.group(3).strip()
                
                # Calculate indent level by counting tree continuation chars (│)
                # Each level adds 4 chars typically: "│   " or "    "
                indent_level = prefix.count('│')
                
                # Adjust stack to current level
                current_path_stack = current_path_stack[:indent_level]
                
                # Determine if directory or file
                is_directory = name.endswith('/') or '.' not in name
                name = name.rstrip('/')
                
                if is_directory:
                    current_path_stack.append(name)
                else:
                    # It's a file - build and store full path
                    full_path = '/'.join(current_path_stack + [name]) if current_path_stack else name
                    self._add_to_file_tree_map(name, full_path)
                continue
            
            # Try dash-based indented list: "  - src/" or "    - file.py"
            match = re.match(r'^(\s*)-\s+(.+?)/?$', line)
            if match:
                in_tree = True
                indent_spaces = len(match.group(1))
                name = match.group(2).strip()
                
                # Calculate indent level (usually 2 spaces per level)
                indent_level = indent_spaces // 2 if indent_spaces > 0 else 0
                
                # Adjust stack to current level
                current_path_stack = current_path_stack[:indent_level]
                
                # Determine if directory or file
                is_directory = name.endswith('/') or '.' not in name
                name = name.rstrip('/')
                
                if is_directory:
                    current_path_stack.append(name)
                else:
                    # It's a file - build and store full path
                    full_path = '/'.join(current_path_stack + [name]) if current_path_stack else name
                    self._add_to_file_tree_map(name, full_path)
                continue
            
            # Try to detect paths in plain text: "src/utils/helper.py"
            # Only if not currently in a tree structure
            if not in_tree and '/' in line and '.' in line:
                # Looks like a path
                path = line.strip()
                # Remove common prefixes
                path = path.lstrip('- ')
                if re.match(r'^[\w\-_]+/[\w\-_/.]+\.\w+$', path):
                    filename = path.split('/')[-1]
                    self._add_to_file_tree_map(filename, path)
                continue
            
            # If line doesn't match any pattern and we were in a tree, reset
            if in_tree and not re.match(r'^[\s│├└─]+', line):
                current_path_stack = []
                in_tree = False
    
    def _add_to_file_tree_map(self, filename: str, full_path: str):
        """
        Add a file to the tree map, handling duplicates intelligently.
        """
        if filename not in self.file_tree_map:
            self.file_tree_map[filename] = full_path
        elif isinstance(self.file_tree_map[filename], list):
            # Multiple paths for same filename
            if full_path not in self.file_tree_map[filename]:
                self.file_tree_map[filename].append(full_path)
        else:
            # Convert to list for multiple paths
            existing = self.file_tree_map[filename]
            if existing != full_path:
                self.file_tree_map[filename] = [existing, full_path]
    
    def _extract_filename_from_header(self, text_before_codeblock: str) -> Optional[str]:
        """
        Extract filename from markdown section headers before a code block.
        Looks for patterns like:
        - ### 3. brand_agent/util.py (Helpers)
        - ## src/main.py - Main Entry Point
        - ### File: config/settings.yaml
        """
        # Get the last few lines before the code block (look back max 5 lines)
        lines = text_before_codeblock.split('\n')
        relevant_lines = lines[-5:] if len(lines) > 5 else lines
        
        for line in reversed(relevant_lines):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Pattern 1: "### 3. path/to/file.py (Description)" or "### path/to/file.py"
            match = re.match(r'^#{1,6}\s*(?:\d+\.\s*)?([a-zA-Z0-9_/\.\-]+\.(?:py|js|jsx|ts|tsx|java|cpp|c|h|go|rs|rb|php|sh|yaml|yml|toml|json|md|txt|dockerfile))\s*(?:\(.*\))?(?:\s*[-:–].*)?$', line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            # Pattern 2: "### File: path/to/file.py"
            match = re.match(r'^#{1,6}\s*File\s*:\s*([a-zA-Z0-9_/\.\-]+)', line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            # Pattern 3: "## path/to/file.py - Description"
            match = re.match(r'^#{1,6}\s*([a-zA-Z0-9_/\.\-]+\.(?:py|js|jsx|ts|tsx|java|cpp|c|h|go|rs|rb|php|sh|yaml|yml|toml|json|md|txt|dockerfile))\s*[-:–]', line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            # If we hit a header without a filename, stop looking
            if line.startswith('#'):
                break
        
        return None
    
    def _extract_or_generate_filename_with_type(self, code: str, language: str, source_file: str, header_filename: Optional[str] = None) -> Tuple[Optional[str], str]:
        """
        Extract filename and modification type from first comment or generate based on code analysis.
        Uses file tree map to determine full paths when available.
        Returns: (filename, modification_type) where mod_type is 'new', 'replace', 'add_to', 'modify', or 'generated'
        """
        lines = code.split('\n')
        
        # Try to extract filename from first few lines of comments
        for i, line in enumerate(lines[:5]):  # Check first 5 lines
            line = line.strip()
            if not line or (language == 'python' and not line.startswith('#')):
                continue
                
            # Try all filename patterns and detect modification type
            # Check for "New file:"
            if re.search(r'#\s*New\s+file\s*:', line, re.IGNORECASE):
                match = re.search(r'#\s*New\s+file\s*:\s*([\w/\.\-]+)', line, re.IGNORECASE)
                if match:
                    filename = match.group(1).strip()
                    filename = self._resolve_with_file_tree(filename)
                    return (filename, 'new')
            
            # Check for "Replace X with:"
            if re.search(r'#\s*Replace\s+', line, re.IGNORECASE):
                match = re.search(r'#\s*Replace\s+([\w/\.\-]+)', line, re.IGNORECASE)
                if match:
                    filename = match.group(1).strip()
                    filename = self._resolve_with_file_tree(filename)
                    return (filename, 'replace')
            
            # Check for "Add to X"
            if re.search(r'#\s*Add\s+to\s+', line, re.IGNORECASE):
                match = re.search(r'#\s*Add\s+to\s+([\w/\.\-]+)', line, re.IGNORECASE)
                if match:
                    filename = match.group(1).strip()
                    filename = self._resolve_with_file_tree(filename)
                    return (filename, 'add_to')
            
            # Check for "In X" (modify existing)
            if re.search(r'#\s*In\s+', line, re.IGNORECASE):
                match = re.search(r'#\s*In\s+([\w/\.\-]+)', line, re.IGNORECASE)
                if match:
                    filename = match.group(1).strip()
                    filename = self._resolve_with_file_tree(filename)
                    return (filename, 'modify')
            
            # Check for "File: X"
            if re.search(r'#\s*File\s*:', line, re.IGNORECASE):
                match = re.search(r'#\s*File\s*:\s*([\w/\.\-]+)', line, re.IGNORECASE)
                if match:
                    filename = match.group(1).strip()
                    filename = self._resolve_with_file_tree(filename)
                    return (filename, 'new')
            
            # Check for simple filename comment
            match = re.search(r'#\s*([\w/]+\.(?:py|js|ts|tsx|jsx|java|cpp|c|h|go|rs|rb|php|sh))', line, re.IGNORECASE)
            if match:
                filename = match.group(1).strip()
                filename = self._resolve_with_file_tree(filename)
                return (filename, 'new')
        
        # No filename found in comments - check if we found one in section header
        if header_filename:
            # Resolve with file tree if available
            resolved_filename = self._resolve_with_file_tree(header_filename)
            return (resolved_filename, 'new')
        
        # No filename found anywhere - generate one based on code analysis
        generated_filename = self._generate_filename_from_code(code, language, source_file)
        return (generated_filename, 'generated')
    
    def _track_file_version(self, filename: str, code: str, language: str, mod_type: str):
        """Track versions of files for later consolidation."""
        # Normalize filename (remove modifications/ prefix for tracking)
        base_filename = filename.replace('modifications/', '')
        
        if base_filename not in self.file_versions:
            self.file_versions[base_filename] = []
        
        self.file_versions[base_filename].append({
            'code': code,
            'language': language,
            'mod_type': mod_type,
            'version': len(self.file_versions[base_filename]) + 1
        })
    
    def _resolve_with_file_tree(self, filename: str) -> str:
        """
        Resolve filename using file tree map if available.
        Handles both simple filenames and paths with folders.
        """
        # If already has a folder structure, check if full path is in tree
        if '/' in filename:
            # Full path provided like "src/agent.py"
            simple_name = filename.split('/')[-1]
            
            # Check if this exact path is in our tree map
            if simple_name in self.file_tree_map:
                tree_path = self.file_tree_map[simple_name]
                if isinstance(tree_path, list):
                    # Multiple matches - try to find exact match
                    for path in tree_path:
                        if path == filename or path.endswith(filename):
                            return path
                    # No exact match, use first one
                    return tree_path[0]
                else:
                    # Single match - use it
                    return tree_path
            # Not in tree, return as-is
            return filename
        else:
            # Simple filename like "agent.py"
            if filename in self.file_tree_map:
                tree_path = self.file_tree_map[filename]
                if isinstance(tree_path, list):
                    # Multiple matches - use first one
                    return tree_path[0]
                else:
                    return tree_path
            # Not in tree, return as-is
            return filename
    
    def _generate_filename_from_code(self, code: str, language: str, source_file: str) -> str:
        """
        Generate meaningful filename by analyzing the code content.
        """
        # Try language-specific analysis
        if language == 'python':
            return self._generate_python_filename(code, source_file)
        elif language in ['javascript', 'js', 'typescript', 'ts']:
            return self._generate_js_filename(code, source_file)
        else:
            return self._generate_generic_filename(code, language, source_file)
    
    def _generate_python_filename(self, code: str, source_file: str) -> str:
        """Generate filename for Python code by analyzing AST."""
        try:
            tree = ast.parse(code)
            
            # Extract class names
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            # Extract function names (top-level only)
            functions = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
            
            # Use first class or function name
            if classes:
                name = classes[0]
                # Convert CamelCase to snake_case
                name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
                return f"generated/{name}.py"
            elif functions:
                name = functions[0]
                return f"generated/{name}.py"
            
            # Look for common patterns in code
            if 'def test_' in code or 'import pytest' in code or 'import unittest' in code:
                return self._generate_unique_filename('test_code', 'py', source_file)
            elif 'import dash' in code or 'import streamlit' in code:
                return self._generate_unique_filename('dashboard', 'py', source_file)
            elif 'class Agent' in code or 'def agent_' in code:
                return self._generate_unique_filename('agent', 'py', source_file)
            elif 'import flask' in code or 'import fastapi' in code:
                return self._generate_unique_filename('api', 'py', source_file)
                
        except SyntaxError:
            # If code is not valid Python (e.g., snippet), analyze as text
            pass
        
        return self._generate_generic_filename(code, 'python', source_file)
    
    def _generate_js_filename(self, code: str, source_file: str) -> str:
        """Generate filename for JavaScript/TypeScript code."""
        # Look for React components
        component_match = re.search(r'(?:export\s+(?:default\s+)?)?(?:function|const|class)\s+(\w+)', code)
        if component_match and component_match.group(1)[0].isupper():
            return f"generated/{component_match.group(1)}.jsx"
        
        # Look for common patterns
        if 'import React' in code or 'import { useState' in code:
            return self._generate_unique_filename('component', 'jsx', source_file)
        elif 'import express' in code:
            return self._generate_unique_filename('server', 'js', source_file)
        elif 'export default' in code or 'module.exports' in code:
            return self._generate_unique_filename('module', 'js', source_file)
        
        return self._generate_generic_filename(code, 'javascript', source_file)
    
    def _generate_generic_filename(self, code: str, language: str, source_file: str) -> str:
        """Generate filename based on code content analysis."""
        code_lower = code.lower()
        
        # Pattern-based naming
        patterns = {
            'test': ['test', 'assert', 'expect', 'describe', r'it\('],
            'config': ['config', 'settings', 'options', 'parameters'],
            'utils': ['utility', 'helper', 'util'],
            'model': [r'class.*model', 'schema', 'entity'],
            'controller': ['controller', 'handler', 'route'],
            'service': ['service', 'manager', 'provider'],
            'database': ['database', 'db', 'sql', 'query'],
            'api': ['api', 'endpoint', 'request', 'response'],
        }
        
        for name, keywords in patterns.items():
            for keyword in keywords:
                if re.search(keyword, code_lower):
                    return self._generate_unique_filename(name, language, source_file)
        
        # Fallback: use content hash for uniqueness
        return self._generate_unique_filename('code', language, source_file)
    
    def _generate_unique_filename(self, base_name: str, extension: str, source_file: str) -> str:
        """Generate unique filename with counter."""
        # Normalize extension
        if extension in ['javascript', 'js']:
            ext = 'js'
        elif extension in ['typescript', 'ts']:
            ext = 'ts'
        elif extension in ['python', 'py']:
            ext = 'py'
        else:
            ext = extension
        
        # Get source file base name for context
        source_base = Path(source_file).stem
        
        # Create counter key
        key = f"{source_base}_{base_name}"
        if key not in self.code_block_counter:
            self.code_block_counter[key] = 0
        
        self.code_block_counter[key] += 1
        count = self.code_block_counter[key]
        
        if count == 1:
            return f"generated/{base_name}.{ext}"
        else:
            return f"generated/{base_name}_{count}.{ext}"
    
    def write_code_files(self, extracted_blocks: List[Tuple[str, str, str, str]]) -> Dict[str, int]:
        """
        Write extracted code blocks to files, handling multiple versions intelligently.
        Returns: Dictionary with statistics
        """
        os.makedirs(self.output_dir, exist_ok=True)
        
        stats = {
            'total': 0,
            'new_files': 0,
            'replacements': 0,
            'modifications': 0,
            'generated': 0,
            'versioned_files': 0
        }
        
        # Process files with multiple versions
        for base_filename, versions in self.file_versions.items():
            if len(versions) == 1:
                # Single version - write normally
                self._write_single_file(base_filename, versions[0], stats)
            else:
                # Multiple versions - write according to strategy
                self._write_multiple_versions(base_filename, versions, stats)
        
        return stats
    
    def _write_single_file(self, filename: str, version_info: dict, stats: dict):
        """Write a single version of a file."""
        code = version_info['code']
        language = version_info['language']
        mod_type = version_info['mod_type']
        
        target_path = os.path.join(self.output_dir, filename)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        with open(target_path, "w", encoding="utf-8") as out_f:
            # Add header comment indicating source
            if language == 'python':
                out_f.write(f"# Extracted from code block (type: {mod_type})\n")
            elif language in ['javascript', 'js', 'typescript', 'ts', 'jsx', 'tsx']:
                out_f.write(f"// Extracted from code block (type: {mod_type})\n")
            out_f.write(code)
            if not code.endswith('\n'):
                out_f.write("\n")
        
        stats['total'] += 1
        if mod_type == 'generated':
            stats['generated'] += 1
        else:
            stats['new_files'] += 1
        
        print(f"  ✓ {filename}")
    
    def _write_multiple_versions(self, filename: str, versions: list, stats: dict):
        """Write multiple versions of the same file based on strategy."""
        if self.modification_strategy == 'latest_only':
            # Only write the last version
            last_version = versions[-1]
            self._write_single_file(filename, last_version, stats)
            print(f"    ℹ️  Kept latest of {len(versions)} versions")
            
        elif self.modification_strategy == 'all_versions':
            # Write all versions with version numbers
            for i, version_info in enumerate(versions, 1):
                if i == 1 and version_info['mod_type'] in ['new', 'generated']:
                    # First version without number
                    versioned_filename = filename
                else:
                    # Subsequent versions with numbers and labels
                    base, ext = os.path.splitext(filename)
                    mod_label = version_info['mod_type']
                    versioned_filename = f"{base}_v{i}_{mod_label}{ext}"
                
                code = version_info['code']
                language = version_info['language']
                mod_type = version_info['mod_type']
                
                target_path = os.path.join(self.output_dir, versioned_filename)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                with open(target_path, "w", encoding="utf-8") as out_f:
                    if language == 'python':
                        out_f.write(f"# Version {i}/{len(versions)} - Type: {mod_type}\n")
                        if i > 1:
                            out_f.write(f"# This {'replaces' if mod_type == 'replace' else 'modifies'} the previous version\n")
                    elif language in ['javascript', 'js', 'typescript', 'ts', 'jsx', 'tsx']:
                        out_f.write(f"// Version {i}/{len(versions)} - Type: {mod_type}\n")
                        if i > 1:
                            out_f.write(f"// This {'replaces' if mod_type == 'replace' else 'modifies'} the previous version\n")
                    out_f.write(code)
                    if not code.endswith('\n'):
                        out_f.write("\n")
                
                stats['total'] += 1
                if mod_type == 'replace':
                    stats['replacements'] += 1
                elif mod_type in ['modify', 'add_to']:
                    stats['modifications'] += 1
                elif mod_type == 'generated':
                    stats['generated'] += 1
                else:
                    stats['new_files'] += 1
                
                print(f"  ✓ {versioned_filename} (v{i}/{len(versions)}: {mod_type})")
            
            stats['versioned_files'] += 1
            
        else:  # 'separate_modifications'
            # Write first version normally, modifications to modifications/ folder
            first_version = versions[0]
            self._write_single_file(filename, first_version, stats)
            
            # Write subsequent versions to modifications folder
            for i, version_info in enumerate(versions[1:], 2):
                mod_filename = f"modifications/{filename}"
                base, ext = os.path.splitext(mod_filename)
                if i > 2:
                    mod_filename = f"{base}_{i-1}{ext}"
                
                code = version_info['code']
                language = version_info['language']
                mod_type = version_info['mod_type']
                
                target_path = os.path.join(self.output_dir, mod_filename)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                with open(target_path, "w", encoding="utf-8") as out_f:
                    if language == 'python':
                        out_f.write(f"# Modification #{i-1} - Type: {mod_type}\n")
                    elif language in ['javascript', 'js', 'typescript', 'ts', 'jsx', 'tsx']:
                        out_f.write(f"// Modification #{i-1} - Type: {mod_type}\n")
                    out_f.write(code)
                    if not code.endswith('\n'):
                        out_f.write("\n")
                
                stats['total'] += 1
                stats['modifications'] += 1
                print(f"  ✓ {mod_filename} ({mod_type})")


def main():
    """Main execution function."""
    print("🔍 Code Block Extractor\n")
    
    extractor = CodeBlockExtractor(INPUT_DIR, OUTPUT_DIR)
    
    # Find all .md files in INPUT_DIR
    input_path = Path(INPUT_DIR)
    if not input_path.exists():
        print(f"❌ Input directory '{INPUT_DIR}' not found!")
        return
    
    md_files = list(input_path.glob('*.md'))
    
    if not md_files:
        print(f"❌ No .md files found in '{INPUT_DIR}'")
        return
    
    print(f"📄 Found {len(md_files)} markdown file(s)")
    
    all_extracted = []
    for md_file in md_files:
        print(f"\n📖 Processing: {md_file.name}")
        extracted = extractor.extract_code_blocks(str(md_file))
        all_extracted.extend(extracted)
        print(f"   Found {len(extracted)} code block(s)")
        
        # Display file tree info if found
        if extractor.file_tree_map:
            print(f"   📂 File tree detected with {len(extractor.file_tree_map)} file(s)")
            if len(extractor.file_tree_map) <= 10:
                for filename, path in extractor.file_tree_map.items():
                    if isinstance(path, list):
                        print(f"      • {filename} → {path[0]} (+{len(path)-1} more)")
                    else:
                        print(f"      • {filename} → {path}")
    
    if not all_extracted:
        print("\n⚠️  No extractable code blocks found")
        return
    
    print(f"\n💾 Writing extracted code to '{OUTPUT_DIR}':\n")
    stats = extractor.write_code_files(all_extracted)
    
    print(f"\n✅ Extraction complete!")
    print(f"   📊 Statistics:")
    print(f"      Total files written: {stats['total']}")
    print(f"      New files: {stats['new_files']}")
    print(f"      Replacements: {stats['replacements']}")
    print(f"      Modifications: {stats['modifications']}")
    print(f"      Generated names: {stats['generated']}")
    if stats['versioned_files'] > 0:
        print(f"      Files with multiple versions: {stats['versioned_files']}")


if __name__ == "__main__":
    main()
