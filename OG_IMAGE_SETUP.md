# Open Graph Image Setup

## ⚠️ Required: Create PNG Image for Social Media

The Open Graph and Twitter Card meta tags require a PNG image (not SVG). 

### Current Status
- Meta tags updated to reference: `static/icons/code-extractor-og.png`
- **This file needs to be created**

### How to Create the Image

#### Option 1: Using Python Script (Recommended)
```bash
pip install cairosvg
python3 create_og_image.py
```

#### Option 2: Manual Creation
1. Use an online SVG to PNG converter:
   - https://cloudconvert.com/svg-to-png
   - https://convertio.co/svg-png/
   - Upload `static/icons/code-extractor3.svg`

2. Set dimensions:
   - **Width**: 1200px
   - **Height**: 630px (Open Graph standard)
   - **Background**: White or transparent

3. Save as: `static/icons/code-extractor-og.png`

#### Option 3: Using Image Editing Software
- Open `code-extractor3.svg` in Photoshop, GIMP, or similar
- Export as PNG at 1200x630px
- Save to `static/icons/code-extractor-og.png`

### Image Specifications
- **Format**: PNG
- **Dimensions**: 1200x630px (1.91:1 aspect ratio)
- **File size**: Keep under 1MB for fast loading
- **Background**: White or transparent
- **Content**: Code extractor icon centered on white background

### Verification
After creating the image, verify it works:
1. Test with Facebook Debugger: https://developers.facebook.com/tools/debug/
2. Test with Twitter Card Validator: https://cards-dev.twitter.com/validator
3. Enter your URL: https://codefrom.chat

### Temporary Fallback
Until the PNG is created, social media previews will show a broken image. The site will still function normally.

---

**Status**: PNG image needs to be created
**Priority**: Medium (affects social media sharing appearance)
