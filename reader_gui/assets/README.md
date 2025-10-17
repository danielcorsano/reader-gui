# Assets

## Icons

- **icon.png** - Original 1024x1024 source icon
- **icon.icns** - macOS icon (generated from icon.png)
- **icon.ico** - Windows icon (TODO: generate with ImageMagick or on Windows)

## Generating icon.ico

On Windows or with ImageMagick installed:
```bash
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
```
