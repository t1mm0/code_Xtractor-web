# Code Block Extractor

An intelligent tool to extract code blocks from markdown files with smart file naming capabilities.

## 🌐 Web Interface (New!)

The extractor now includes a modern web interface with drag-and-drop functionality:

### Features
- **🎯 Drag & Drop**: Simply drag your markdown file onto the page
- **⚡ Real-time Processing**: Dynamic status updates during extraction
- **📦 Automatic Download**: Extracted code is automatically zipped and downloaded
- **🔗 Manual Download Link**: Download link available after automatic download
- **📊 Statistics Dashboard**: See detailed extraction statistics

### Quick Start (Web UI)

```bash
# Install dependencies
pip install -r requirements.txt

# Start the web server
python web_app.py

# Open your browser to http://localhost:5000
```

Then simply drag and drop your markdown file onto the page!

## Features

### 🌳 File Tree Parsing (New!)
Automatically detects and uses file tree structures in markdown to organize extracted files:

```
myproject/
├── src/
│   ├── components/
│   │   └── Header.jsx
│   └── utils/
│       └── api_client.py
└── tests/
    └── test_api.py
```

Files are extracted with the **exact folder structure** from the tree!

### 🔄 Multi-Version Handling (New!)
Intelligently tracks and saves multiple versions when markdown contains:
- **Replace**: `# Replace utils.py with:` → saves both original and replacement
- **Modify**: `# In utils.py` → tracks modifications
- **Add to**: `# Add to utils.py` → versions additions

Files are saved with clear versioning: `utils_v1_new.py`, `utils_v2_modify.py`, `utils_v3_replace.py`

**See [FEATURES_GUIDE.md](FEATURES_GUIDE.md) for detailed documentation!**

### 🎯 Smart Filename Detection
Automatically detects filenames from various comment patterns:

```python
# New file: src/agent_alerting.py
# In agent1_harvest.py
# Add to agent1_harvest.py  
# Replace agent2_filter_dedupe.py with:
# File: src/something.py
```

### 🧠 Intelligent Name Generation
When no filename is specified in comments, the extractor analyzes the code to generate meaningful names:

#### Python Code Analysis
- **AST Parsing**: Extracts class and function names
  - `class DynamicSourceAdjustment` → `dynamic_source_adjustment.py`
- **Pattern Detection**: Identifies code purpose
  - Test code → `test_code.py`
  - Dashboard code → `dashboard.py`
  - Agent code → `agent.py`
  - API code → `api.py`

#### JavaScript/TypeScript Analysis
- React components → `ComponentName.jsx`
- Express servers → `server.js`
- Modules → `module.js`

#### Generic Pattern Matching
For any language, detects patterns like:
- Tests (test, assert, expect, describe)
- Config (config, settings, options)
- Utils (utility, helper)
- Models (class, schema, entity)
- Controllers (controller, handler, route)
- Services (service, manager, provider)
- Database (database, db, sql, query)
- APIs (api, endpoint, request, response)

### 📁 Organized Output Structure

The extractor organizes files into logical directories:

```
output/
├── src/                    # New files explicitly named
│   ├── agent_alerting.py
│   ├── agent_forecast.py
│   └── dashboard.py
├── modifications/          # Code marked as modifications
│   ├── agent1_harvest.py
│   ├── agent5_llm.py
│   └── run_weekly.py
└── generated/              # Auto-generated filenames
    ├── code.py
    ├── database.txt
    └── model.txt
```

## Usage

### Web Interface (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Start the web server
python web_app.py

# Open browser to http://localhost:5000
```

**How to use:**
1. Visit http://localhost:5000 in your browser
2. Drag and drop your `.md` file onto the page (or click to browse)
3. Watch real-time processing status
4. Your extracted code is automatically downloaded as a ZIP file
5. A manual download link is also provided

### Command Line Interface

```bash
cd code_extractor
python app.py
```

### Directory Structure

```
code_extractor/
├── app.py              # Core extractor (CLI)
├── web_app.py          # Web interface (Flask)
├── requirements.txt    # Dependencies for web UI
├── templates/          # HTML templates
│   └── index.html
├── static/             # CSS and JavaScript
│   ├── style.css
│   └── script.js
├── input/              # Place .md files here (CLI mode)
│   └── sample.md
└── output/             # Extracted code (CLI mode)
```

### Configuration

You can modify the constants in `app.py`:

```python
INPUT_DIR = "input"   # Directory containing .md files
OUTPUT_DIR = "output" # Where to save extracted code
```

## How It Works

### 1. Code Block Detection
Matches markdown code blocks with any language specifier:
````markdown
```python
# Your code here
```
````

### 2. Filename Extraction
Scans the first 5 lines for filename patterns using regex:
- `# New file: path/to/file.py`
- `# In existing_file.py`
- `# Add to some_file.py`
- etc.

### 3. Code Analysis (Fallback)
If no filename is found:
1. **Parse AST** (for Python/JS) to extract class/function names
2. **Pattern Match** common keywords (test, config, api, etc.)
3. **Generate Unique Name** with counter to avoid conflicts

### 4. File Organization
- Files with explicit names → saved to specified path
- Modification patterns → saved to `modifications/` directory
- Generated names → saved to `generated/` directory

## Examples

### Example 1: Explicit Filename
**Input:**
````markdown
```python
# New file: src/agent_alerting.py
def check_high_priority_signals(kg_data):
    # ... code
```
````

**Output:** `output/src/agent_alerting.py`

### Example 2: Modification
**Input:**
````markdown
```python
# In agent1_harvest.py
def auto_tune_sources(metrics):
    # ... code
```
````

**Output:** `output/modifications/agent1_harvest.py`

### Example 3: Auto-Generated Name
**Input:**
````markdown
```python
class DynamicSourceAdjustment:
    def __init__(self):
        # ... code
```
````

**Output:** `output/generated/dynamic_source_adjustment.py`

### Example 4: Pattern-Based Name
**Input:**
````markdown
```python
def test_extraction():
    assert extractor.extract() == expected
```
````

**Output:** `output/generated/test_code.py`

## Extensibility

### Adding New Filename Patterns

Add patterns to the `FILENAME_PATTERNS` list:

```python
FILENAME_PATTERNS = [
    # Your custom pattern
    r'#\s*Custom\s+pattern\s*:\s*([\w/\.\-]+)',
    # ... existing patterns
]
```

### Adding New Language Support

Extend the `_generate_filename_from_code` method:

```python
def _generate_filename_from_code(self, code: str, language: str, source_file: str) -> str:
    if language == 'rust':
        return self._generate_rust_filename(code, source_file)
    # ... existing logic
```

### Adding New Pattern Keywords

Update the patterns dictionary in `_generate_generic_filename`:

```python
patterns = {
    'your_pattern': ['keyword1', 'keyword2', r'regex\s+pattern'],
    # ... existing patterns
}
```

## Statistics Output

The tool provides detailed statistics:

```
✅ Extraction complete!
   📊 Statistics:
      Total files: 20
      New files: 8          # Explicitly named files
      Modifications: 9      # Code marked for modification
      Generated names: 3    # Auto-generated filenames
```

## Requirements

### Command Line Interface
- Python 3.7+
- No external dependencies (uses only standard library)

### Web Interface
- Python 3.7+
- Flask 3.0.0+
- Werkzeug 3.0.1+

Install web dependencies:
```bash
pip install -r requirements.txt
```

## Limitations

- AST parsing only works for syntactically valid code
- Some edge cases in filename detection may require manual adjustment
- Non-Python/JS languages use pattern matching only

## Future Enhancements

- [ ] Support for more languages (Go, Rust, Java, etc.)
- [ ] Better handling of code snippets vs. complete files
- [ ] Option to merge modifications into existing files
- [ ] Configuration file for custom patterns
- [ ] Interactive mode for ambiguous cases
- [ ] Duplicate detection across runs

## Contributing

To improve the extractor:
1. Add new patterns to `FILENAME_PATTERNS`
2. Implement language-specific analyzers
3. Enhance pattern matching in `_generate_generic_filename`
4. Add tests for edge cases

## License

Use freely in your projects.

