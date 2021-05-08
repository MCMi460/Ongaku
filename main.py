import time
from pypresence import Presence
import subprocess
import platform

rpc = Presence('402370117901484042')

while True:
    try:
        rpc.connect()
        break
    except:
        continue

rpc.connect()

mac_ver = float(platform.mac_ver()[0])

appName = "Music"

if mac_ver >= 11.3:
    assetName = "big_sur_logo"
elif 11.3 > mac_ver >= 11.0:
    print("Apple Script is broken before Big Sur 11.3 - please update to use this program.")
    quit()
elif mac_ver == 10.15:
    assetName = "music_logo"
else:
    appName = "iTunes"
    assetName = "itunes_logo"

def get_status():
    cmd = """
        on run
    		tell application "%s"
    			if player state is playing then
    				return "1"
                else if player state is paused then
                    return "2"
                else
                return "0"
    			end if
    		end tell
        end run
    """
    return str(subprocess.run(['osascript', '-e', cmd % appName], capture_output=True).stdout)[2:][:-3]

def get_trackname():
    cmd = """
        on run
    		tell application "%s"
    			if player state is playing then
    				return name of current track
                else if player state is paused then
                    return name of current track
                else
                return "Stopped"
    			end if
    		end tell
        end run
    """
    return str(subprocess.run(['osascript', '-e', cmd % appName], capture_output=True).stdout)[2:][:-3]

def get_info():
    cmd = """
        on run
    		tell application "%s"
    			if player state is playing then
    				return {album,artist} of current track
                else if player state is paused then
                    return {album,artist} of current track
                else
                return "Stopped"
    			end if
    		end tell
        end run
    """
    return str(subprocess.run(['osascript', '-e', cmd % appName], capture_output=True).stdout)[2:][:-3]

def get_duration():
    cmd = """
        on run
    		tell application "%s"
    			if player state is playing then
    				return player position & duration of current track
                else if player state is paused then
                    return player position & duration of current track
                else
                return "Stopped"
    			end if
    		end tell
        end run
    """
    return str(subprocess.run(['osascript', '-e', cmd % appName], capture_output=True).stdout)[2:][:-3]

def update():
    status = get_status()
    if status == "1":
        trackname = get_trackname()
        details = trackname
        small_image = "play"
        small_text = "Actively playing"
    elif status == "2":
        trackname = get_trackname()
        details = f"Paused - {trackname}"
        small_image = "pause"
        small_text = "Currently paused"
    elif status == "0":
        rpc.update(details="Stopped",state="Nothing is currently playing",small_image="stop",large_image=assetName,large_text="There's nothing here!",small_text="Currently stopped")
        return
    large_text = trackname
    epoch = time.time()
    stamp = get_duration()
    pos = float(stamp.split(", ")[0])
    duration = float(stamp.split(", ")[1])
    rpc.update(details=details,state=get_info(),small_image=small_image,large_image=assetName,large_text=large_text,small_text=small_text,start=epoch,end=epoch + (duration - pos))

while True:
    update()
    time.sleep(15)
