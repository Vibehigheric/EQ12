# EQ12 Cross-Browser Extension Example

This is a sample extension demonstrating cross-browser compatibility patterns.

## Files Structure
```
example_extension/
├── manifest.json          # Base manifest template
├── background.js          # Background script
├── content.js            # Content script  
├── popup.html            # Extension popup
├── popup.js              # Popup logic
├── polyfill.js           # Cross-browser compatibility
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## Usage

Build for all browsers:
```bash
python scripts/eq12_cross_browser_extension_builder.py -s example_extension -o dist
```

This creates:
- `dist/chrome/` - Chrome/Chromium compatible (Manifest V3)
- `dist/firefox/` - Firefox compatible (Manifest V2) 
- `dist/edge/` - Edge compatible (Manifest V3)
- `dist/safari/` - Safari compatible (Manifest V2)