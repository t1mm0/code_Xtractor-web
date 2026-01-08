// ============================================================================
// Code Block Extractor - Frontend JavaScript
// Purpose: Handle file uploads, drag & drop, paste text, and UI interactions
// Last Modified: 2024-12-19
// Completeness: 100%
// ============================================================================

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const statusContainer = document.getElementById('statusContainer');
const statusTitle = document.getElementById('statusTitle');
const statusMessage = document.getElementById('statusMessage');
const resultsContainer = document.getElementById('resultsContainer');
const resultsMessage = document.getElementById('resultsMessage');
const statsGrid = document.getElementById('statsGrid');
const downloadBtn = document.getElementById('downloadBtn');
const resetBtn = document.getElementById('resetBtn');
const errorContainer = document.getElementById('errorContainer');
const errorMessage = document.getElementById('errorMessage');
const errorResetBtn = document.getElementById('errorResetBtn');

let currentSessionId = null;

// Initialize
function init() {
    setupDropZone();
    setupButtons();
    setupGlobalPaste();
}

// Setup Drop Zone
function setupDropZone() {
    // Click to upload
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFile(file);
        }
    });

    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // Paste text support on dropzone
    dropZone.addEventListener('paste', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const clipboardData = e.clipboardData || window.clipboardData;
        const pastedText = clipboardData.getData('text');
        
        if (pastedText && pastedText.trim().length > 0) {
            handlePastedText(pastedText);
        }
    });

    // Make dropzone focusable for paste events
    dropZone.setAttribute('tabindex', '0');
    dropZone.setAttribute('role', 'button');
    dropZone.setAttribute('aria-label', 'Drop zone for markdown files or paste text');
    
    // Focus dropzone on click to enable paste
    dropZone.addEventListener('click', (e) => {
        if (e.target === dropZone || e.target.closest('.drop-zone-content')) {
            dropZone.focus();
        }
    });

    // Visual feedback when dropzone is focused (ready for paste)
    dropZone.addEventListener('focus', () => {
        dropZone.classList.add('paste-ready');
    });

    dropZone.addEventListener('blur', () => {
        dropZone.classList.remove('paste-ready');
    });
}

// Setup Global Paste Handler
function setupGlobalPaste() {
    // Listen for paste events anywhere on the page when dropzone is visible
    document.addEventListener('paste', (e) => {
        // Only handle paste if dropzone is visible and not processing
        if (dropZone.style.display !== 'none' && 
            statusContainer.style.display === 'none' &&
            resultsContainer.style.display === 'none' &&
            errorContainer.style.display === 'none') {
            
            // Don't interfere with paste in input fields or textareas
            const target = e.target;
            if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
                return;
            }
            
            e.preventDefault();
            e.stopPropagation();
            
            const clipboardData = e.clipboardData || window.clipboardData;
            const pastedText = clipboardData.getData('text');
            
            if (pastedText && pastedText.trim().length > 0) {
                // Visual feedback
                dropZone.classList.add('paste-detected');
                setTimeout(() => {
                    dropZone.classList.remove('paste-detected');
                }, 300);
                
                handlePastedText(pastedText);
            }
        }
    });
}

// Setup Buttons
function setupButtons() {
    downloadBtn.addEventListener('click', () => {
        if (currentSessionId) {
            window.location.href = `/download/${currentSessionId}`;
        }
    });

    resetBtn.addEventListener('click', resetUI);
    errorResetBtn.addEventListener('click', resetUI);
}

// Handle Pasted Text
function handlePastedText(text) {
    // Create a File object from the pasted text
    const blob = new Blob([text], { type: 'text/markdown' });
    const file = new File([blob], 'pasted_content.md', { type: 'text/markdown' });
    
    // Process it like a regular file upload
    handleFile(file);
}

// Handle File Upload
async function handleFile(file) {
    // Validate file
    if (!file.name.endsWith('.md')) {
        showError('Please upload a .md (markdown) file');
        return;
    }

    if (file.size > 16 * 1024 * 1024) {
        showError('File size must be less than 16MB');
        return;
    }

    // Show processing status
    showProcessing();

    // Create form data
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Upload and process
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }

        // Handle response
        if (data.status === 'success') {
            currentSessionId = data.session_id;
            showResults(data);
            // Trigger automatic download after a short delay to ensure session is ready
            // Increased delay to ensure server has processed and stored the session
            setTimeout(() => {
                triggerAutoDownload();
            }, 1000);
        } else if (data.status === 'warning') {
            showError(data.message);
        } else {
            showError(data.message || 'Unknown error occurred');
        }

    } catch (error) {
        console.error('Upload error:', error);
        showError(error.message || 'Failed to upload file. Please try again.');
    }
}

// Show Processing Status
function showProcessing() {
    dropZone.style.display = 'none';
    resultsContainer.style.display = 'none';
    errorContainer.style.display = 'none';
    statusContainer.style.display = 'block';
    
    statusTitle.textContent = 'Processing...';
    statusMessage.textContent = 'Extracting and organizing code blocks';
}

// Show Results
function showResults(data) {
    statusContainer.style.display = 'none';
    resultsContainer.style.display = 'block';
    
    const stats = data.stats || {};
    
    // Update message
    resultsMessage.textContent = `Successfully extracted ${stats.total || 0} code block(s) from your markdown file`;
    
    // Build stats grid
    statsGrid.innerHTML = `
        <div class="stat-card">
            <span class="stat-number">${stats.total || 0}</span>
            <span class="stat-label">Total Files</span>
        </div>
        <div class="stat-card">
            <span class="stat-number">${stats.new_files || 0}</span>
            <span class="stat-label">New Files</span>
        </div>
        <div class="stat-card">
            <span class="stat-number">${stats.modifications || 0}</span>
            <span class="stat-label">Modifications</span>
        </div>
        <div class="stat-card">
            <span class="stat-number">${stats.generated || 0}</span>
            <span class="stat-label">Generated Names</span>
        </div>
    `;
}

// Show Error
function showError(message) {
    dropZone.style.display = 'none';
    statusContainer.style.display = 'none';
    resultsContainer.style.display = 'none';
    errorContainer.style.display = 'block';
    
    errorMessage.textContent = message;
}

// Reset UI
function resetUI() {
    dropZone.style.display = 'block';
    statusContainer.style.display = 'none';
    resultsContainer.style.display = 'none';
    errorContainer.style.display = 'none';
    
    fileInput.value = '';
    currentSessionId = null;
}

// Trigger Automatic Download
function triggerAutoDownload() {
    if (currentSessionId) {
        // Create hidden iframe for automatic download
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = `/download/${currentSessionId}`;
        document.body.appendChild(iframe);
        
        // Remove iframe after download starts
        setTimeout(() => {
            document.body.removeChild(iframe);
        }, 2000);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

