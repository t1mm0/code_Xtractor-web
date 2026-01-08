import os
import io
import zipfile
import tempfile
import uuid
import socket
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

# Import the existing extractor without modifications
from app import CodeBlockExtractor, OUTPUT_DIR

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Store processing results temporarily
RESULTS_CACHE = {}

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and process markdown files."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.md'):
        return jsonify({'error': 'Only .md files are supported'}), 400
    
    try:
        # Generate unique session ID for this upload
        session_id = str(uuid.uuid4())
        
        # Create temporary directories for this session
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], f'code_extractor_{session_id}')
        input_dir = os.path.join(temp_dir, 'input')
        output_dir = os.path.join(temp_dir, 'output')
        
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        md_path = os.path.join(input_dir, filename)
        file.save(md_path)
        
        # Process the file using the existing extractor
        extractor = CodeBlockExtractor(input_dir, output_dir)
        extracted = extractor.extract_code_blocks(md_path)
        
        if not extracted:
            return jsonify({
                'status': 'warning',
                'message': 'No code blocks found in the uploaded file',
                'stats': {
                    'total': 0,
                    'new_files': 0,
                    'modifications': 0,
                    'generated': 0
                }
            }), 200
        
        # Write extracted files
        stats = extractor.write_code_files(extracted)
        
        # Create zip file of the output
        zip_path = os.path.join(temp_dir, f'extracted_code_{session_id}.zip')
        create_zip_archive(output_dir, zip_path)
        
        # Store result information
        RESULTS_CACHE[session_id] = {
            'zip_path': zip_path,
            'output_dir': output_dir,
            'temp_dir': temp_dir,
            'filename': f'extracted_code_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
            'timestamp': datetime.now(),
            'stats': stats
        }
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully extracted {stats["total"]} code block(s)',
            'session_id': session_id,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error processing file: {str(e)}'
        }), 500

@app.route('/download/<session_id>')
def download_file(session_id):
    """Download the generated zip file."""
    if session_id not in RESULTS_CACHE:
        return jsonify({'error': 'Session not found or expired'}), 404
    
    result = RESULTS_CACHE[session_id]
    zip_path = result['zip_path']
    filename = result['filename']
    
    if not os.path.exists(zip_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        zip_path,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )

def create_zip_archive(source_dir, output_path):
    """Create a zip archive of the output directory."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

def is_port_available(port, host='0.0.0.0'):
    """Check if a port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            result = s.bind((host, port))
            return True
    except OSError:
        return False

def find_available_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        if is_port_available(port):
            return port
    return None  # No available port found

# Cleanup old sessions (optional, can be called periodically)
def cleanup_old_sessions(max_age_hours=24):
    """Remove old session files to prevent disk space issues."""
    from datetime import timedelta
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    
    expired_sessions = []
    for session_id, result in RESULTS_CACHE.items():
        if result['timestamp'] < cutoff_time:
            expired_sessions.append(session_id)
            # Clean up files
            try:
                import shutil
                if os.path.exists(result['temp_dir']):
                    shutil.rmtree(result['temp_dir'])
            except Exception as e:
                print(f"Error cleaning up session {session_id}: {e}")
    
    for session_id in expired_sessions:
        del RESULTS_CACHE[session_id]

if __name__ == '__main__':
    # Create static and templates directories if they don't exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Find an available port
    preferred_port = 5000
    port = find_available_port(preferred_port)
    
    if port is None:
        print("❌ Error: Could not find an available port (tried ports 5000-5009)")
        exit(1)
    
    if port != preferred_port:
        print(f"⚠️  Port {preferred_port} is in use, using port {port} instead")
    
    print("🚀 Starting Code Extractor Web Application")
    print(f"📍 Visit: http://localhost:{port}")
    print("\n✨ Features:")
    print("   • Drag & Drop markdown files")
    print("   • Real-time processing status")
    print("   • Automatic download of extracted code")
    print("   • Manual download link available")
    print("\n" + "="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=port)

