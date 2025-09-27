import subprocess
import re
import sys

def get_wall_duration(pkg, activity):
    # Build adb command
    cmd = ["adb", "shell", "am", "start", "-W", "-n", f"{pkg}/{activity}"]

    try:
        # Run adb command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout

        # Extract WaitTime using regex
        match = re.search(r"WaitTime:\s*(\d+)", output)
        if match:
            wait_time = int(match.group(1))
            print(f"Wall duration for {pkg}/{activity} = {wait_time} ms")
            return wait_time
        else:
            print("WaitTime not found in output.")
            print(output)
            return None

    except subprocess.CalledProcessError as e:
        print("Error running adb:", e)
        return None

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python wall_duration.py <package> <activity>")
        print("Example: python wall_duration.py com.android.settings .homepage.SettingsHomepageActivity")
        sys.exit(1)

    pkg = sys.argv[1]
    activity = sys.argv[2]
    get_wall_duration(pkg, activity)
