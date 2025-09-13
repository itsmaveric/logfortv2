#!/usr/bin/env python3
"""
Vendor static assets for offline desktop use
Downloads Bootstrap, Chart.js, Font Awesome, and DataTables from CDNs
"""
import os
import requests
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Asset URLs to download
ASSETS = {
    # CSS files
    'css/bootstrap.min.css': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'css/font-awesome.min.css': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    'css/dataTables.bootstrap5.min.css': 'https://cdn.datatables.net/1.13.7/css/dataTables.bootstrap5.min.css',
    
    # JavaScript files
    'js/bootstrap.bundle.min.js': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'js/jquery.min.js': 'https://code.jquery.com/jquery-3.7.1.min.js',
    'js/chart.min.js': 'https://cdn.jsdelivr.net/npm/chart.js',
    'js/jquery.dataTables.min.js': 'https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js',
    'js/dataTables.bootstrap5.min.js': 'https://cdn.datatables.net/1.13.7/js/dataTables.bootstrap5.min.js',
}

# Font Awesome font files (additional downloads needed for icons)
FONT_AWESOME_FONTS = {
    'fonts/fa-solid-900.woff2': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.woff2',
    'fonts/fa-regular-400.woff2': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.woff2',
    'fonts/fa-brands-400.woff2': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.woff2',
}

def download_file(url, local_path):
    """Download a file from URL to local path"""
    try:
        logger.info(f"Downloading {url} -> {local_path}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"✅ Downloaded {local_path} ({len(response.content)} bytes)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download {url}: {str(e)}")
        return False

def fix_font_awesome_css(css_path):
    """Fix Font Awesome CSS to reference local font files"""
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace CDN font URLs with local paths
        content = content.replace(
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/',
            '{{ url_for("static", filename="fonts/") }}'
        )
        
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✅ Fixed Font Awesome CSS paths in {css_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix Font Awesome CSS: {str(e)}")
        return False

def vendor_assets():
    """Download all vendor assets"""
    static_dir = Path('static')
    static_dir.mkdir(exist_ok=True)
    
    success_count = 0
    total_count = len(ASSETS) + len(FONT_AWESOME_FONTS)
    
    # Download main assets
    for local_path, url in ASSETS.items():
        local_file = static_dir / local_path
        if download_file(url, local_file):
            success_count += 1
    
    # Download Font Awesome fonts
    for local_path, url in FONT_AWESOME_FONTS.items():
        local_file = static_dir / local_path
        if download_file(url, local_file):
            success_count += 1
    
    # Fix Font Awesome CSS to reference local fonts
    fa_css_path = static_dir / 'css' / 'font-awesome.min.css'
    if fa_css_path.exists():
        fix_font_awesome_css(fa_css_path)
    
    logger.info(f"\n🎉 Vendor complete: {success_count}/{total_count} assets downloaded")
    
    if success_count == total_count:
        logger.info("✅ All assets downloaded successfully!")
        return True
    else:
        logger.warning(f"⚠️  {total_count - success_count} assets failed to download")
        return False

def main():
    """Main entry point"""
    logger.info("Starting asset vendoring process...")
    success = vendor_assets()
    
    if success:
        logger.info("\n📁 Asset structure created:")
        static_dir = Path('static')
        for item in sorted(static_dir.rglob('*')):
            if item.is_file():
                size_kb = item.stat().st_size / 1024
                logger.info(f"   {item.relative_to(static_dir)} ({size_kb:.1f} KB)")
        
        logger.info("\n🔧 Next step: Update templates to use local assets")
    else:
        logger.error("❌ Asset vendoring failed. Check network connection and try again.")

if __name__ == '__main__':
    main()