# Code Extractor Web UI Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server

**Option A: Using the start script (Unix/Mac/Linux)**
```bash
./start_web.sh
```

**Option B: Direct Python command**
```bash
python web_app.py
```

### 3. Open Your Browser
Navigate to: **http://localhost:5000**

## 📖 How to Use

### Step 1: Upload Your Markdown File
- **Drag & Drop**: Simply drag your `.md` file onto the drop zone
- **Click to Browse**: Click the drop zone to select a file from your computer

### Step 2: Processing
- Watch the real-time status indicator as your file is processed
- The extractor analyzes code blocks and generates intelligent filenames
- Status appears dynamically only while processing

### Step 3: Download Results
- **Automatic Download**: A ZIP file is automatically pushed to your browser
- **Manual Download**: A download button is also provided for re-downloading
- **Statistics**: View detailed stats about extracted files

### Step 4: Process Another File
- Click "Extract Another File" to reset and process a new markdown file

## ✨ Features

### 🎯 Drag & Drop Interface
- Modern, intuitive UI
- Visual feedback during drag operations
- Mobile-responsive design

### ⚡ Real-Time Status
- Processing status appears only when actively processing
- Dynamic progress messages
- No clutter when idle

### 📦 Automatic Download
- Extracted code is immediately saved to a temporary output folder
- Automatically zipped on completion
- Pushed back to browser as immediate download
- No manual download needed (but option available)

### 📊 Statistics Dashboard
After extraction, you'll see:
- **Total Files**: Number of code blocks extracted
- **New Files**: Explicitly named files
- **Modifications**: Code marked for modification
- **Generated Names**: Auto-generated filenames

### 🔗 Manual Download Link
- After automatic download, a "Download ZIP" button is available
- Click to re-download if needed
- Files remain available until browser refresh

## 🏗️ Architecture

### Core Components

1. **web_app.py**: Flask backend
   - Handles file uploads
   - Processes markdown using the original `CodeBlockExtractor`
   - Creates ZIP archives
   - Manages download endpoints

2. **templates/index.html**: Frontend HTML
   - Drag & drop zone
   - Dynamic status displays
   - Results and error handling

3. **static/style.css**: Styling
   - Modern, clean design
   - Responsive layout
   - Smooth animations

4. **static/script.js**: Frontend logic
   - File handling
   - AJAX requests
   - UI state management
   - Automatic download trigger

### Data Flow

```
1. User drops .md file
   ↓
2. JavaScript captures file, shows processing status
   ↓
3. AJAX POST to /upload endpoint
   ↓
4. Flask creates temp directories
   ↓
5. CodeBlockExtractor processes file (original functionality preserved)
   ↓
6. Extracted files saved to temp output folder
   ↓
7. Output folder zipped
   ↓
8. Server returns session_id and stats
   ↓
9. JavaScript triggers automatic download via hidden iframe
   ↓
10. Results displayed with manual download link
```

## 🔧 Configuration

### Port Configuration
Edit `web_app.py` to change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port here
```

### File Size Limit
Default: 16MB. Modify in `web_app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # In bytes
```

### Session Cleanup
Old temporary files can be cleaned up:
```python
cleanup_old_sessions(max_age_hours=24)  # Adjust hours
```

## 🔍 How Original Functionality is Preserved

The web interface **wraps** the original `CodeBlockExtractor` class without any modifications:

```python
# Original extractor is imported and used as-is
from app import CodeBlockExtractor

# In the upload handler
extractor = CodeBlockExtractor(input_dir, output_dir)
extracted = extractor.extract_code_blocks(md_path)
stats = extractor.write_code_files(extracted)
```

**No changes to:**
- Code block detection logic
- Filename extraction patterns
- AST parsing
- Pattern matching
- File organization
- Statistics calculation

The CLI version (`app.py`) continues to work independently.

## 🛡️ Security Features

- File type validation (only `.md` files accepted)
- File size limits (16MB default)
- Secure filename handling with `secure_filename()`
- Temporary directories with unique session IDs
- No persistent storage of uploaded files

## 📱 Browser Compatibility

Tested and working on:
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process or change port in web_app.py
```

### Flask Not Found
```bash
pip install -r requirements.txt
```

### Download Not Working
- Check browser download settings
- Ensure pop-ups are not blocked
- Try the manual download button

### File Not Processing
- Ensure file is `.md` format
- Check file size (< 16MB)
- Verify file contains code blocks in markdown format

## 🎨 Customization

### Styling
Edit `static/style.css` to customize:
- Colors (CSS variables in `:root`)
- Animations
- Layout
- Typography

### UI Text
Edit `templates/index.html` to modify:
- Headers and descriptions
- Button labels
- Status messages

### Processing Logic
The original `app.py` can be enhanced with new features, and they'll automatically work in the web UI.

## 🔄 Workflow Examples

### Example 1: Quick Extraction
1. Start server: `./start_web.sh`
2. Drag `code.md` onto page
3. Watch status (2-3 seconds)
4. ZIP downloads automatically
5. Extract and use files

### Example 2: Multiple Files
1. Process first file
2. Click "Extract Another File"
3. Drop second file
4. Repeat as needed
5. Each gets its own timestamped ZIP

### Example 3: Re-download
1. Process file
2. Close download dialog accidentally
3. Click "Download ZIP" button
4. File downloads again

## 📊 Performance

- **Small files** (< 100KB): ~1-2 seconds
- **Medium files** (100KB - 1MB): ~2-5 seconds
- **Large files** (1-16MB): ~5-10 seconds

Processing time depends on:
- Number of code blocks
- Complexity of AST parsing
- System performance

## 🚦 Production Deployment

For production use:

1. **Disable Debug Mode**
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

2. **Use Production Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
   ```

3. **Add HTTPS**
   - Use nginx or Apache as reverse proxy
   - Add SSL certificates

4. **Implement Cleanup**
   - Schedule periodic cleanup of temp files
   - Add monitoring

## 📝 License

Same as original project - use freely.

## 🙏 Credits

Built on top of the original Code Block Extractor, preserving all its intelligent extraction capabilities.

