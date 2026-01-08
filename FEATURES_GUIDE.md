# Code Extractor - Features Guide

## Overview

The Code Block Extractor now includes advanced features for handling file trees, multiple versions, and code modifications.

## ✨ New Features

### 1. File Tree Parsing

The extractor automatically detects and parses file tree structures in markdown files to organize extracted code properly.

#### Supported File Tree Formats

**Format 1: Tree Characters (├──, └──, │)**
```
myproject/
├── src/
│   ├── components/
│   │   ├── Header.jsx
│   │   └── Footer.jsx
│   └── utils/
│       └── api_client.py
└── tests/
    └── test_api.py
```

**Format 2: Dash-based Indentation**
```
- myproject/
  - src/
    - components/
      - Header.jsx
      - Footer.jsx
    - utils/
      - api_client.py
  - tests/
    - test_api.py
```

**Format 3: Plain Paths**
```
src/utils/helper.py
src/components/Button.jsx
tests/test_suite.py
```

#### How It Works

1. **Automatic Detection**: The extractor scans markdown content for file tree structures
2. **Path Mapping**: Creates a map of filenames to their full paths
3. **Smart Resolution**: When extracting code blocks, uses the tree map to determine correct paths
4. **Folder Preservation**: Files are saved with the exact folder structure from the tree

#### Example

If your markdown has:
```
src/
├── api_client.py
└── validators.py
```

And later contains:
```python
# api_client.py
class APIClient:
    ...
```

The file will be saved to: `output/src/api_client.py` (not just `output/api_client.py`)

---

### 2. Multi-Version File Handling

When markdown contains multiple code blocks for the same file (modifications, replacements, additions), the extractor intelligently tracks and saves all versions.

#### Modification Types Detected

| Comment Pattern | Type | Description |
|----------------|------|-------------|
| `# New file: X` | `new` | Brand new file |
| `# File: X` | `new` | Brand new file (alternative) |
| `# Replace X with:` | `replace` | Complete replacement |
| `# In X` | `modify` | Modification to existing file |
| `# Add to X` | `add_to` | Addition to existing file |
| *(no comment)* | `generated` | Auto-generated filename |

#### Version Strategies

The extractor supports 3 strategies for handling multiple versions:

##### Strategy 1: `all_versions` (Default)

Saves all versions with descriptive naming:

```
agent1_harvest_v1_add_to.py      # First modification
agent1_harvest_v2_modify.py      # Second modification  
agent1_harvest_v3_replace.py     # Replacement version
```

Each file includes a header:
```python
# Version 2/3 - Type: modify
# This modifies the previous version
```

**Best for**: Understanding the evolution of code, keeping all iterations

##### Strategy 2: `latest_only`

Only saves the last version of each file:

```
agent1_harvest.py  # Only the final version
```

**Best for**: Production use, when you only want the end result

##### Strategy 3: `separate_modifications`

Saves first version normally, modifications to `modifications/` folder:

```
agent1_harvest.py                     # Original
modifications/agent1_harvest.py       # First modification
modifications/agent1_harvest_2.py     # Second modification
```

**Best for**: Review workflows, separating original from changes

---

### 3. Path Resolution from Comments

When a code block has a path in its comment, the extractor respects it:

```python
# In src/utils/helper.py
def my_function():
    pass
```

Saved to: `output/src/utils/helper.py`

If a file tree is also present, the extractor:
1. First checks the file tree for the filename
2. Uses the tree path if found
3. Falls back to the comment path otherwise

---

## 📋 Usage Examples

### Example 1: Simple Markdown with File Tree

**Input: `mycode.md`**
```markdown
# My Project

File structure:
```
project/
├── src/
│   └── main.py
└── tests/
    └── test_main.py
```

Code files:

```python
# main.py
def hello():
    print("Hello!")
```

```python
# test_main.py
def test_hello():
    assert True
```
```

**Output:**
```
output/
├── src/
│   └── main.py
└── tests/
    └── test_main.py
```

---

### Example 2: Iterative Modifications

**Input: `iterations.md`**
```markdown
# Code Evolution

Initial version:

```python
# New file: calculator.py
def add(a, b):
    return a + b
```

Add multiplication:

```python
# Add to calculator.py
def multiply(a, b):
    return a * b
```

Replace with better implementation:

```python
# Replace calculator.py with:
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
```
```

**Output (with `all_versions` strategy):**
```
output/
├── calculator.py                    # Version 1: original
├── calculator_v2_add_to.py         # Version 2: with multiply
└── calculator_v3_replace.py        # Version 3: class-based
```

Each file has headers indicating version and type.

---

### Example 3: Complex Project Structure

**Input: `fullstack.md`**
```markdown
# Full Stack App

```
app/
├── backend/
│   ├── api/
│   │   ├── routes.py
│   │   └── models.py
│   └── utils/
│       └── db.py
└── frontend/
    ├── components/
    │   └── App.jsx
    └── styles/
        └── main.css
```

Backend code:

```python
# routes.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello!"
```

```python
# models.py
from sqlalchemy import Column, Integer, String
from db import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
```

Frontend code:

```jsx
# App.jsx
import React from 'react';

export default function App() {
    return <h1>My App</h1>;
}
```
```

**Output:**
```
output/
├── backend/
│   ├── api/
│   │   ├── routes.py
│   │   └── models.py
│   └── utils/
│       └── db.py
└── frontend/
    ├── components/
    │   └── App.jsx
    └── styles/
        └── main.css
```

Perfect folder structure preservation!

---

## 🎛️ Configuration

### Changing Version Strategy

Edit `app.py`:

```python
extractor = CodeBlockExtractor(INPUT_DIR, OUTPUT_DIR)
extractor.modification_strategy = 'latest_only'  # or 'all_versions' or 'separate_modifications'
```

---

## 📊 Statistics Output

After extraction, you'll see detailed statistics:

```
✅ Extraction complete!
   📊 Statistics:
      Total files written: 28
      New files: 17
      Replacements: 3
      Modifications: 5
      Generated names: 3
      Files with multiple versions: 2
```

**Metrics:**
- **Total files written**: All files saved to output
- **New files**: Files marked as new
- **Replacements**: Files marked for replacement
- **Modifications**: Files marked for modification or addition
- **Generated names**: Files with auto-generated names
- **Files with multiple versions**: Unique files that have 2+ versions

---

## 🔍 File Tree Detection Info

When a file tree is found, you'll see:

```
📖 Processing: mycode.md
   Found 8 code block(s)
   📂 File tree detected with 10 file(s)
      • Header.jsx → src/components/Header.jsx
      • api_client.py → src/utils/api_client.py
      • main.py → src/main.py
```

This shows the mapping from simple filenames to full paths.

---

## 💡 Best Practices

### 1. Include File Trees

Always include a file tree in your markdown when working with multi-file projects:

```markdown
# My Project

Structure:
```
src/
├── file1.py
└── file2.py
```

[code blocks follow]
```

### 2. Use Clear Comments

Be explicit about file operations:

```python
# New file: src/api.py         # ✅ Clear
# api.py                         # ⚠️ Ambiguous location
```

### 3. Document Modifications

When modifying code, explain why:

```python
# Replace utils.py with:
# Reason: Added error handling and logging

[improved code]
```

### 4. Consistent Naming

Keep filenames consistent between tree and code blocks:

```
File tree: src/api_client.py
Comment:   # api_client.py      ✅ Matches!
Comment:   # ApiClient.py       ❌ Won't match
```

---

## 🐛 Troubleshooting

### Files Not Using Tree Structure

**Problem**: Code saved to wrong location despite file tree

**Solutions**:
1. Check filename in comment matches tree exactly
2. Ensure tree uses standard format
3. Verify no extra spaces or characters in tree

### Missing Versions

**Problem**: Only seeing one version when expecting multiple

**Solutions**:
1. Check modification strategy (maybe set to `latest_only`)
2. Verify modification comments are in first 5 lines
3. Ensure proper comment syntax (`# In X` not `// In X` for Python)

### Generated Names Instead of Tree Paths

**Problem**: Files saved to `generated/` folder

**Solutions**:
1. Add filename comments to code blocks
2. Check file tree includes the files
3. Verify tree parsing with debug output

---

## 🚀 Advanced Usage

### Custom Strategy Per Project

```python
# For different markdown files
extractor1 = CodeBlockExtractor("input1", "output1")
extractor1.modification_strategy = 'all_versions'

extractor2 = CodeBlockExtractor("input2", "output2")
extractor2.modification_strategy = 'latest_only'
```

### Programmatic Access

```python
from app import CodeBlockExtractor

extractor = CodeBlockExtractor()
blocks = extractor.extract_code_blocks("myfile.md")

for filename, code, language, mod_type in blocks:
    print(f"{filename}: {mod_type}")
```

---

## 📝 Summary

The Code Block Extractor now intelligently handles:

✅ File tree structures (multiple formats)  
✅ Folder path preservation  
✅ Multiple versions of the same file  
✅ Different modification types  
✅ Smart path resolution  
✅ Flexible versioning strategies  

This makes it perfect for extracting code from:
- Tutorial documents with evolving code
- Project documentation with full structure
- Code review documents with before/after
- API documentation with examples
- Architecture docs with file layouts

Enjoy your enhanced code extraction! 🎉


