# Bing Wallpaper Service

<img src="https://img.shields.io/github/v/release/jpdfr-msft/bing-wallpaper-service" alt="Current Version">
<img src="https://img.shields.io/github/license/jpdfr-msft/bing-wallpaper-service" alt="License">

A macOS service that automatically sets the Bing Image of the Day as your:
- Desktop wallpaper
- Microsoft Teams background
- macOS Camera background

## Features

✅ **Auto-updates**: The script checks for updates at runtime and installs new versions automatically  
✅ **Daily Updates**: When installed as a service, updates backgrounds daily  
✅ **Multiple Background Support**: Sets backgrounds for desktop, Teams, and camera  
✅ **Easy Installation**: Simple one-line command to install as a macOS service  

## Requirements

- macOS Sequoia or later
- Python 3.x
- `requests` library

## Quick Install

```bash
# Clone the repository
git clone https://github.com/jpdfr-msft/bing-wallpaper-service.git

# Enter the directory
cd bing-wallpaper-service

# Install Python requests if needed
python3 -m pip install requests

# Make the script executable
chmod +x bing_wallpaper.py

# Install as a service (runs at login)
./bing_wallpaper.py --install
```

## Manual Usage

If you prefer not to install the service, you can run the script manually:

```bash
./bing_wallpaper.py
```

## How It Works

1. **Version Check**: The script checks GitHub for newer versions
2. **Downloads Image**: Gets the current Bing Image of the Day
3. **Sets Backgrounds**: Updates desktop wallpaper, Teams backgrounds, and camera backgrounds
4. **Daily Updates**: When installed as a service, runs once per day

## Verifying the Installation

To verify that the service will run at login:

```bash
# Check if the launch agent plist file exists
ls -l ~/Library/LaunchAgents/com.user.bing-wallpaper-service.plist

# View the launch agent configuration
plutil -p ~/Library/LaunchAgents/com.user.bing-wallpaper-service.plist

# Check if the launch agent is loaded
launchctl list | grep bing-wallpaper

# Force the service to run immediately
launchctl start com.user.bing-wallpaper-service

# Check the log file for execution records
tail -n 20 ~/Library/Logs/bing_wallpaper_service.log
```

Proper configuration should show:
- `RunAtLoad` set to `1` (runs at login)
- `StartInterval` set to `86400` (runs daily)
- Script path pointing to your installation

## Troubleshooting

- **Error with `requests` module**: Install using `pip3 install requests` or `python3 -m pip install requests`
- **Permission errors**: Ensure the script is executable with `chmod +x bing_wallpaper.py`
- **Services not running**: Reinstall the service with `./bing_wallpaper.py --install`
- **Service doesn't start at login**: Try manual reload with `launchctl unload ~/Library/LaunchAgents/com.user.bing-wallpaper-service.plist && launchctl load -w ~/Library/LaunchAgents/com.user.bing-wallpaper-service.plist`

## License

MIT License - Feel free to use, modify, and distribute this software.

## Contribute

Contributions are welcome! Please feel free to submit a Pull Request.
