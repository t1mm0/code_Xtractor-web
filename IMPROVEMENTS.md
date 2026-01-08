# Code Extractor Improvements Summary

## 🎯 What Was Improved

The `code_extractor/app.py` has been completely rewritten to provide intelligent, extensible, and accurate code block extraction from markdown files.

## ✨ Key Features Added

### 1. **Multiple Filename Pattern Recognition**
The extractor now recognizes various comment patterns for specifying filenames:

| Pattern | Example | Output |
|---------|---------|--------|
| New file | `# New file: src/agent.py` | `src/agent.py` |
| Modification | `# In agent1_harvest.py` | `modifications/agent1_harvest.py` |
| Add to | `# Add to utils.py` | `modifications/utils.py` |
| Replace | `# Replace config.py with:` | `modifications/config.py` |
| File | `# File: src/helper.py` | `src/helper.py` |
| Direct | `# my_script.py` | `my_script.py` |

### 2. **Smart Code Analysis & Auto-Naming**

When no filename is specified in comments, the extractor analyzes the code:

#### Python Analysis (AST-based)
```python
class DynamicSourceAdjustment:
    def process(self):
        pass
```
→ **Generated filename:** `generated/dynamic_source_adjustment.py`

- Extracts class names and converts CamelCase to snake_case
- Extracts function names for function-only files
- Detects common patterns (tests, dashboards, agents, APIs)

#### JavaScript/TypeScript Analysis
```javascript
export default function UserProfile() {
  return <div>Profile</div>;
}
```
→ **Generated filename:** `generated/UserProfile.jsx`

- Detects React components
- Identifies Express servers
- Recognizes module exports

#### Pattern-Based Detection
The extractor recognizes code purpose from keywords:

| Category | Keywords | Example Output |
|----------|----------|----------------|
| Test | test, assert, expect, unittest | `test_code.py` |
| Config | config, settings, options | `config.py` |
| Utils | utility, helper, util | `utils.py` |
| Model | class, schema, entity | `model.py` |
| Controller | controller, handler, route | `controller.py` |
| Service | service, manager, provider | `service.py` |
| Database | database, db, sql, query | `database.py` |
| API | api, endpoint, request | `api.py` |

### 3. **Organized Output Structure**

Files are automatically organized into logical directories:

```
output/
├── src/                      # Explicit "New file:" declarations
│   ├── agent_alerting.py
│   ├── agent_forecast.py
│   └── dashboard.py
├── modifications/            # Files marked for modification
│   ├── agent1_harvest.py
│   ├── agent5_llm.py
│   └── run_weekly.py
└── generated/                # Auto-generated filenames
    ├── user_authentication_service.py
    ├── calculate_metrics.py
    └── test_data_processor.py
```

### 4. **Comprehensive Statistics**

```
✅ Extraction complete!
   📊 Statistics:
      Total files: 30
      New files: 10          # Files with explicit names
      Modifications: 10      # Files marked for modification
      Generated names: 10    # Auto-generated filenames
```

### 5. **Better Code Organization**

The new implementation uses object-oriented design:

```python
class CodeBlockExtractor:
    """
    Intelligently extracts code blocks from markdown files 
    with smart file naming.
    """
    - extract_code_blocks()          # Main extraction
    - _extract_or_generate_filename() # Filename logic
    - _generate_python_filename()    # Python-specific
    - _generate_js_filename()        # JS/TS-specific
    - _generate_generic_filename()   # Pattern matching
    - write_code_files()             # Output generation
```

### 6. **Extensibility**

Easy to extend with new patterns and languages:

**Add a new filename pattern:**
```python
FILENAME_PATTERNS = [
    r'#\s*Custom\s+pattern\s*:\s*([\w/\.\-]+)',
    # ... existing patterns
]
```

**Add new language support:**
```python
def _generate_filename_from_code(self, code, language, source):
    if language == 'rust':
        return self._generate_rust_filename(code, source)
    # ... existing logic
```

**Add new pattern keywords:**
```python
patterns = {
    'migration': ['migration', 'schema', 'alter table'],
    # ... existing patterns
}
```

## 📊 Before vs After

### Before (Original)
- ❌ Limited pattern recognition (only 1 regex pattern)
- ❌ No intelligent naming for unnamed blocks
- ❌ No code analysis
- ❌ All files in flat output directory
- ❌ No statistics or feedback
- ❌ Hard to extend

### After (Improved)
- ✅ 6+ filename pattern recognitions
- ✅ AST-based code analysis for Python
- ✅ Pattern detection for JS/TS/React
- ✅ Generic keyword-based naming
- ✅ Organized output structure (src/, modifications/, generated/)
- ✅ Detailed statistics and progress feedback
- ✅ Object-oriented, extensible design
- ✅ CamelCase to snake_case conversion
- ✅ Duplicate handling with counters
- ✅ Language-specific file extensions

## 🧪 Testing

Run with the provided test file:
```bash
cd code_extractor
mv test_sample.md input/
python app.py
```

This will demonstrate:
- Explicit filename extraction
- Auto-generated class-based names
- Pattern detection (tests, APIs)
- Multi-language support (Python, JS, Shell, JSON)

## 📖 Documentation

- **README.md** - Complete user guide with examples
- **IMPROVEMENTS.md** - This file, summarizing changes
- **test_sample.md** - Test cases demonstrating all features

## 🚀 Usage Example

```bash
cd code_extractor
python app.py
```

Output:
```
🔍 Code Block Extractor

📄 Found 2 markdown file(s)

📖 Processing: sample.md
   Found 20 code block(s)

💾 Writing 20 file(s) to 'output':
  ✓ src/agent_alerting.py
  ✓ modifications/agent1_harvest.py
  ✓ generated/user_authentication_service.py
  ...

✅ Extraction complete!
```

## 🎓 Key Algorithms

### AST Parsing for Python
```python
tree = ast.parse(code)
classes = [node.name for node in ast.walk(tree) 
           if isinstance(node, ast.ClassDef)]
# Convert CamelCase → snake_case
```

### Regex Pattern Matching
```python
for pattern in FILENAME_PATTERNS:
    match = re.search(pattern, line, re.IGNORECASE)
    if match:
        return match.group(1)
```

### Keyword-Based Classification
```python
patterns = {
    'test': ['test', 'assert', 'unittest'],
    'api': ['api', 'endpoint', 'flask']
}
for name, keywords in patterns.items():
    if any(kw in code.lower() for kw in keywords):
        return f"generated/{name}.py"
```

## 🔮 Future Enhancements

Potential additions for even more intelligence:
- [ ] LLM integration for ambiguous cases
- [ ] Support for more languages (Go, Rust, Java, C++)
- [ ] Merge mode (combine modifications into existing files)
- [ ] Interactive mode for user confirmation
- [ ] Configuration file for custom rules
- [ ] Duplicate detection across runs
- [ ] GitHub Action integration

## 💡 Design Principles

1. **Smart Defaults**: Works out of the box with zero configuration
2. **Progressive Enhancement**: Tries specific → falls back to generic
3. **Clear Feedback**: Shows what was extracted and how
4. **Extensible**: Easy to add new patterns and languages
5. **Organized**: Logical directory structure for outputs
6. **Accurate**: Multiple strategies ensure correct naming

---

**Result:** A production-ready, intelligent code extractor that handles real-world markdown files with complex code blocks! 🎉

