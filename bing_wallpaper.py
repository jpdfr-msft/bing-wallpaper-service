#!/usr/bin/python3

"""
Bing Wallpaper Service for macOS
- Sets Bing Image of the Day as:
  1. Desktop Wallpaper
  2. Microsoft Teams Background
  3. macOS Camera Background

Requirements:
- requests library
- MacOS Sequoia

Usage:
1. Ensure the script is executable: chmod +x bing_wallpaper.py
2. Run the script manually or set it up as a login item to run at startup.

Version Check:
The script checks for a new version before execution. Update the version variable to the latest version when releasing updates.
"""

import datetime
import json
import os
import subprocess
import shutil
import glob
import logging
import requests
import plistlib
import sys

CURRENT_VERSION = "1.0.0"  # Update this version when releasing a new version
REPO_URL = "https://api.github.com/repos/jpdfr-msft/bing-wallpaper-service/releases/latest"

def setup_logging():
    log_dir = os.path.expanduser('~/Library/Logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'bing_wallpaper_service.log')
    
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )

def check_for_updates():
    """
    Check for updates and download the latest script version if available
    Returns:
        bool: True if using latest version or update successful, False otherwise
    """
    try:
        # Get script path for potential replacement
        script_path = os.path.abspath(__file__)
        
        # Get latest release info from GitHub
        response = requests.get(REPO_URL, headers={"Accept": "application/vnd.github.v3+json"})
        if response.status_code != 200:
            logging.warning(f"Failed to check for updates: HTTP {response.status_code}")
            return True
            
        latest_release = response.json()
        latest_version = latest_release.get("tag_name", "").strip('v')
        
        if not latest_version:
            logging.warning("Could not determine latest version")
            return True
            
        if latest_version != CURRENT_VERSION:
            logging.info(f"New version available: {latest_version} (current: {CURRENT_VERSION})")
            
            # Get the download URL for the script
            assets = latest_release.get("assets", [])
            script_url = None
            for asset in assets:
                if asset.get("name") == "bing_wallpaper.py":
                    script_url = asset.get("browser_download_url")
                    break
            
            if script_url:
                # Download the updated script
                updated_script = requests.get(script_url).text
                
                # Create backup of current script
                backup_path = f"{script_path}.bak"
                shutil.copy2(script_path, backup_path)
                logging.info(f"Created backup at: {backup_path}")
                
                # Save the new script
                with open(script_path, 'w') as f:
                    f.write(updated_script)
                
                logging.info(f"Updated script to version {latest_version}")
                
                # Re-run with the new version
                os.execv(sys.executable, [sys.executable] + sys.argv)
                return False  # This won't be reached due to execv
            else:
                logging.warning("Update available but couldn't find script download URL")
        
        logging.info("Using latest version")
        return True
    except Exception as e:
        logging.error(f"Error checking for updates: {e}")
        return True  # Proceed even if we can't check for updates

def download_bing_image():
    try:
        response = requests.get("https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=fr-FR")
        image_data = json.loads(response.text)
        image_url = image_data["images"][0]["urlbase"]
        full_image_url = f"https://www.bing.com{image_url}_1920x1080.jpg"
        
        unique_id = "bing-image-of-the-day"
        pictures_dir = os.path.expanduser('~/Pictures/Backgrounds')
        os.makedirs(pictures_dir, exist_ok=True)
        
        image_name = os.path.join(pictures_dir, f"{unique_id}.jpg")
        img_data = requests.get(full_image_url).content
        with open(image_name, 'wb') as handler:
            handler.write(img_data)
        
        logging.info(f"Downloaded Bing image: {image_name}")
        return image_name
    
    except Exception as e:
        logging.error(f"Error downloading Bing image: {e}")
        raise

def set_desktop_wallpaper(image_path):
    try:
        image_path = os.path.abspath(image_path)
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        applescript = f'''
        tell application "System Events"
            tell current desktop
                set picture to POSIX file "{image_path}"
            end tell
        end tell
        '''
        
        methods = [
            lambda: subprocess.run(['osascript', '-e', applescript], check=True),
            lambda: subprocess.run(f'sqlite3 ~/Library/Application\ Support/Dock/desktoppicture.db "UPDATE data SET value = \'{image_path}\';" && killall Dock', shell=True, check=True),
            lambda: subprocess.run(['defaults', 'write', 'com.apple.desktop', 'Background', '-dict-add', 'Changes', '-string', image_path], check=True),
            lambda: subprocess.run(['killall', 'Dock'], check=False)
        ]
        
        for method in methods:
            try:
                method()
                logging.info(f"Successfully set desktop wallpaper: {image_path}")
                return
            except subprocess.CalledProcessError as e:
                logging.warning(f"Method failed: {e}")
                continue
        
        raise Exception("Could not set desktop wallpaper using any method")
    
    except Exception as e:
        logging.error(f"Error setting desktop wallpaper: {e}")
        raise

def set_teams_background(image_path):
    try:
        teams_background_dirs = [
            os.path.expanduser('~/Library/Containers/com.microsoft.teams2/Data/Library/Application Support/Microsoft/MSTeams/Backgrounds/Uploads'),
            os.path.expanduser('~/Library/Application Support/Microsoft/Teams/Backgrounds/Uploads')
        ]
        
        teams_filename = "bing-background.jpg"
        
        for directory in teams_background_dirs:
            os.makedirs(directory, exist_ok=True)
            dest_path = os.path.join(directory, teams_filename)
            shutil.copy2(image_path, dest_path)
            logging.info(f"Copied Teams background to: {dest_path}")
    
    except Exception as e:
        logging.error(f"Error setting Teams background: {e}")

def set_camera_background(image_path):
    try:
        background_dirs = [
            os.path.expanduser('~/Library/Containers/com.apple.Camera/Data/Library/Backgrounds/'),
            os.path.expanduser('~/Library/Preferences/Camera/Backgrounds/'),
            os.path.expanduser('~/Pictures/Camera Backgrounds/'),
            os.path.expanduser('~/Library/Application Support/com.apple.Camera/Backgrounds/')
        ]
        
        for directory in background_dirs:
            os.makedirs(directory, exist_ok=True)
            destination = os.path.join(directory, os.path.basename(image_path))
            shutil.copy2(image_path, destination)
            logging.info(f"Copied camera background to: {destination}")
        
        escaped_image_path = image_path.replace('"', '\\"')
        methods = [
            f'defaults write com.apple.AVFoundation AVCaptureBackgroundImageURL -string "{escaped_image_path}"',
            f'systemsetup -setdesktoppicture "{escaped_image_path}"'
        ]
        
        for method in methods:
            result = subprocess.run(method, shell=True, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                logging.info(f"Successfully set camera background method: {method}")
            else:
                logging.warning(f"Camera background setting failed: {result.stderr}")
        
        logging.info(f"Camera background set to: {image_path}")
    
    except Exception as e:
        logging.error(f"Error setting Camera background: {e}")

def create_launch_agent():
    """Create a macOS launch agent to run the script at login"""
    try:
        # Path to the current script
        script_path = os.path.abspath(__file__)
        
        # Create a property list for the launch agent
        launch_agent = {
            'Label': 'com.user.bing-wallpaper-service',
            'ProgramArguments': ['/usr/bin/python3', script_path],
            'RunAtLoad': True,
            'KeepAlive': False,
            'StartInterval': 86400  # Run once a day (24 hours)
        }
        
        # Ensure the LaunchAgents directory exists
        launch_agents_dir = os.path.expanduser('~/Library/LaunchAgents')
        os.makedirs(launch_agents_dir, exist_ok=True)
        
        # Path for the plist file
        plist_path = os.path.join(launch_agents_dir, 'com.user.bing-wallpaper-service.plist')
        
        # Write the plist file
        with open(plist_path, 'wb') as f:
            plistlib.dump(launch_agent, f)
        
        # Load the launch agent
        subprocess.run(['launchctl', 'unload', plist_path], check=False)
        subprocess.run(['launchctl', 'load', '-w', plist_path], check=True)
        
        logging.info(f"Created and loaded launch agent: {plist_path}")
        return True
    
    except Exception as e:
        logging.error(f"Error creating launch agent: {e}")
        return False

def main():
    """Main function to download and set backgrounds"""
    setup_logging()
    
    # Process command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--install":
            create_launch_agent()
            logging.info("Launch agent installed. The script will run at login.")
            return
    
    if not check_for_updates():
        return
    
    try:
        image_path = download_bing_image()
        set_desktop_wallpaper(image_path)
        set_teams_background(image_path)
        set_camera_background(image_path)
        
        logging.info("Background update completed successfully")
    
    except Exception as e:
        logging.error(f"Failed to update backgrounds: {e}")

if __name__ == "__main__":
    main()