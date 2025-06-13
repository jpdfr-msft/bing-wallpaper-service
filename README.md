# Bing Wallpaper Service for macOS

A simple service that automatically sets the Bing Image of the Day as your:
- Desktop wallpaper
- Microsoft Teams background
- macOS Camera background

## Features

- Automatically downloads the Bing Image of the Day
- Sets multiple backgrounds in one go
- Auto-updates from GitHub repository
- Easy installation as a Launch Agent

## Requirements

- macOS Sequoia or later
- Python 3.x
- `requests` library (install via `pip install requests`)

## Installation

1. **Clone the Repository**:
   Clone this repository to your local machine using:
   ```
   git clone https://github.com/jpdfr-msft/bing-wallpaper-service.git
   ```

2. **Make the script executable**:
   ```
   chmod +x bing_wallpaper.py
   ```

3. **Install as a Launch Agent**:
   ```
   ./bing_wallpaper.py --install
   ```
   This will create a launch agent that runs at login and once daily.

## Manual Usage

If you prefer to run the script manually:

```
./bing_wallpaper.py
```

## Automatic Updates

The script automatically checks for updates when run. If a new version is available, it will:
1. Download the latest script from GitHub
2. Create a backup of the current script
3. Replace the script with the new version
4. Restart itself with the updated code

## Repository Setup for Development

If you're developing this project, here's how to set up GitHub releases:

1. Create the GitHub repository
2. Update the `REPO_URL` variable in the script with your actual repository URL
3. Create a GitHub Actions workflow in `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Create Release
        id: create_release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            bing_wallpaper.py
            LICENSE
            README.md
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

4. Tag and push to create a release:
```
git tag v1.0.0
git push origin v1.0.0
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.