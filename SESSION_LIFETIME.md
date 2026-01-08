# Download Link Availability

## ⏰ Session Lifetime: **24 Hours**

Download links are available for **24 hours** from the time the file was uploaded and processed.

## 🔄 How It Works

### Session Storage
- Each upload creates a unique session ID (UUID)
- Session data is stored in memory (`RESULTS_CACHE`)
- ZIP files are stored in temporary directories
- Each session has a timestamp when it was created

### Automatic Cleanup
The application automatically cleans up old sessions in two ways:

1. **Background Cleanup Thread**
   - Runs every hour automatically
   - Removes sessions older than 24 hours
   - Deletes temporary files and ZIP archives
   - Cleans up memory cache

2. **On-Demand Cleanup**
   - Triggered on each download request
   - Ensures expired sessions are cleaned up immediately
   - Prevents accumulation of old files

### What Gets Cleaned Up
- Session data from `RESULTS_CACHE`
- Temporary directories (`/tmp/code_extractor_{session_id}/`)
- ZIP files (`extracted_code_{session_id}.zip`)
- All extracted code files

## ⚠️ Important Notes

### Server Restart
- **If the server restarts**, all sessions are lost immediately
- This is because sessions are stored in memory
- Users will need to re-upload their files

### Production vs Development
- Same 24-hour lifetime applies to both
- Cleanup runs automatically in both environments
- No manual intervention needed

## 📊 Timeline Example

```
Time 0:00 - User uploads file → Session created
Time 0:01 - ZIP file ready → Download link available
Time 1:00 - Background cleanup runs (session still valid)
Time 2:00 - Background cleanup runs (session still valid)
...
Time 24:00 - Session expires → Cleanup removes session
Time 24:01 - Download link returns "Session not found or expired"
```

## 🔧 Configuration

The cleanup interval can be adjusted in `web_app.py`:

```python
# Change from 24 hours to different duration
cleanup_old_sessions(max_age_hours=48)  # 48 hours
```

Background cleanup runs every hour (3600 seconds). To change:

```python
time.sleep(7200)  # Run every 2 hours instead
```

## 💡 Best Practices

1. **Download Immediately**: Download your ZIP file right after processing
2. **Save the File**: Once downloaded, save it locally - don't rely on the link
3. **Re-upload if Needed**: If the link expires, simply re-upload the markdown file

## 🚨 Error Messages

If a download link expires, users will see:
```
Download Error
Session not found or expired. Please upload your file again.
[Return to Home]
```

This is a user-friendly HTML error page (not JSON) that guides users to re-upload.

---

**Last Updated**: 2024-12-19
**Default Session Lifetime**: 24 hours
**Cleanup Frequency**: Every hour
