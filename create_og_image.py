#!/usr/bin/env python3
"""
Create Open Graph PNG image from SVG
Purpose: Generate social media preview image (1200x630px)
Last Modified: 2024-12-19
"""

#!/usr/bin/env python3
"""
Create Open Graph PNG image from SVG
Purpose: Generate social media preview image (1200x630px)
Last Modified: 2024-12-19
"""

svg_path = 'static/icons/code-extractor3.svg'
output_path = 'static/icons/code-extractor-og.png'

try:
    from cairosvg import svg2png
    import os
    
    # Create 1200x630 PNG for Open Graph (standard social media size)
    svg2png(
        url=svg_path,
        write_to=output_path,
        output_width=1200,
        output_height=630,
        background_color='white'
    )
    print(f"✅ Created Open Graph image: {output_path}")
except ImportError:
    print("⚠️  cairosvg not installed. Install with: pip install cairosvg")
    print("   Or create the PNG manually using:")
    print("   - Online SVG to PNG converter")
    print("   - Image editing software")
    print("   - Size: 1200x630px")
    print(f"   - Source: {svg_path}")
    print(f"   - Output: {output_path}")
except Exception as e:
    print(f"❌ Error creating PNG: {e}")
