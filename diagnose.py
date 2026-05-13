import os
import winreg
import re

print("=== BERLIN STEAM DIAGNOSTICS ===\n")

# Check Steam path
try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
    path, _ = winreg.QueryValueEx(key, "SteamPath")
    steam_path = path.replace("/", "\\")
    print(f"✓ Steam Path Found: {steam_path}")
except Exception as e:
    print(f"✗ Steam Path Error: {e}")
    steam_path = None

if steam_path:
    # Check loginusers.vdf file
    config_path = os.path.join(steam_path, "config", "loginusers.vdf")
    print(f"\nChecking file: {config_path}")
    print(f"File exists: {os.path.exists(config_path)}")
    
    if os.path.exists(config_path):
        # Try to read file with different encodings
        print("\nTrying different encodings...")
        for encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
            try:
                with open(config_path, "r", encoding=encoding) as f:
                    content = f.read()
                print(f"✓ Successfully read with {encoding}")
                print(f"  File size: {len(content)} characters")
                print(f"  First 500 chars:\n{content[:500]}\n")
                
                # Try to find accounts with improved regex
                print("  Searching for accounts...")
                
                # Look for account sections with 17+ digit IDs
                matches = re.findall(r'"(\d{17,})"\s*\n?\s*{(.*?)}\s*\n', content, re.DOTALL)
                print(f"  Pattern 1 (17+ digits with newlines): Found {len(matches)} entries")
                
                # Try simpler pattern
                matches2 = re.findall(r'"\d+"\s*{(.*?)}', content, re.DOTALL)
                print(f"  Pattern 2 (simple): Found {len(matches2)} entries")
                
                # Look for AccountName field
                acc_names = re.findall(r'"AccountName"\s*"([^"]*)"', content)
                print(f"  Found {len(acc_names)} AccountName entries: {acc_names}")
                
                break
            except Exception as e:
                print(f"✗ Failed with {encoding}: {e}")
    else:
        print("\n✗ loginusers.vdf file not found!")
        print(f"  Checking if config directory exists: {os.path.exists(os.path.join(steam_path, 'config'))}")
        
        # List contents of Steam directory
        if os.path.exists(steam_path):
            print(f"\n  Contents of {steam_path}:")
            for item in os.listdir(steam_path)[:10]:
                print(f"    - {item}")
