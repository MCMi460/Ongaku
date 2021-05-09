from time import sleep, time
from pypresence import Presence
from subprocess import run
from platform import mac_ver
from requests import get
from json import loads
from rumps import App, quit_application
from threading import Thread

# Set Discord Rich Presence ID
rpc = Presence('402370117901484042')

# Attempt to connect to Discord. Will remain open until it connect
while True:
    try:
        rpc.connect()
        break
    except:
        continue

# Sometimes PyPresence returns a Client ID error if you don't put a second .connect() after the loop
rpc.connect()

# Get MacOS version
ver = float(mac_ver()[0])

# Set default appname we're using for grabbing music data with Apple Script
appName = "Music"

# If Big Sur 11.3 or later, then use the updated Apple Music logo
if ver >= 10.16:
    assetName = "big_sur_logo"
# If Big Sur version is below 11.3, quit program due to issues grabbing music data with Apple Script before 11.3
elif 11.3 > ver >= 11.0:
    print("Apple Script is broken before Big Sur 11.3 - please update to use this program.")
    quit()
# Don't know what this is about, but I wanted to port Spotlight's code to Python exactly, so I kept this
elif ver == 10.15:
    assetName = "music_logo"
# Use old iTunes logo and appname
else:
    appName = "iTunes"
    assetName = "itunes_logo"

# All of these 'get functions' use Python subprocess-ing to pipe Apple Script data and get it
# Then the fancy stuff when returning the function is just to format the string to look proper

# Get status will return 1 if Music is playing, 2 if Music is paused, and 0 if Music is stopped
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
    return int(run(['osascript', '-e', cmd % appName], capture_output=True).stdout.decode('utf-8').rstrip())

# Get trackname will return the name of the current track
def get_trackname():
    cmd = """
        on run
    		tell application "%s"
    			return name of current track
    		end tell
        end run
    """
    return run(['osascript', '-e', cmd % appName], capture_output=True).stdout.decode('utf-8').rstrip()

# Get info will return the album and artist of the current track
def get_info():
    cmd = """
        on run
    		tell application "%s"
                return {album,artist} of current track
    		end tell
        end run
    """
    return run(['osascript', '-e', cmd % appName], capture_output=True).stdout.decode('utf-8').rstrip()

# Get duration returns the Music player's position and the duration of the current track
def get_duration():
    cmd = """
        on run
    		tell application "%s"
    			return player position & duration of current track
    		end tell
        end run
    """
    return run(['osascript', '-e', cmd % appName], capture_output=True).stdout.decode('utf-8').rstrip()

# Find out whether this is a user-uploaded song or otherwise
def get_cloud():
    cmd = """
        on run
    		tell application "%s"
    			return cloud status of current track
    		end tell
        end run
    """
    return run(['osascript', '-e', cmd % appName], capture_output=True).stdout.decode('utf-8').rstrip()

# Contains logic code that calls functions to grab data using Apple Script and updates the RPC controller with the data
def update():
    # Grab playing status
    status = get_status()
    # If the song is on the player get name, album, and artist
    if status > 0:
        trackname = get_trackname()
        state = get_info()
        if len(state) < 2:
            state = "Song has no artist assigned"
    # If the song is playing
    if status == 1:
        details = trackname
        small_image = "play"
        small_text = "Actively playing"
        # Get current epoch time
        epoch = time()
        stamp = get_duration()
        # Format position and duration data
        pos = float(stamp.split(", ")[0])
        duration = float(stamp.split(", ")[1])
        type = get_cloud()
        failed = False
        if type == "purchased" or type == "subscription":
            try:
                # Use Music's API to grab Store URL by searching for it. Apple Script cannot get the Store URL, so I had to code this alternate method
                url = loads(get(f"https://itunes.apple.com/search?term={trackname.replace(' ','+')}+{trackname.replace(' ','+')}+{state.replace(', ',' ').replace(' ','+')}").content.decode('utf-8'))["results"][0]['trackViewUrl']
                # Update RPC with Store URL button included
                rpc.update(details=details,state=state,small_image=small_image,large_image=assetName,large_text=trackname,small_text=small_text,start=epoch,end=epoch + (duration - pos),buttons=[{"label": "View in Store", "url": url}])
            except:
                # If it cannot get a song, then it will just update without the Store URL button
                failed = True
        else:
            # Song is either self-uploaded or otherwise.
            failed = True
        # Display without Store URL button
        if failed:
            rpc.update(details=details,state=state,small_image=small_image,large_image=assetName,large_text=trackname,small_text=small_text,start=epoch,end=epoch + (duration - pos))
    # If the song is paused
    elif status == 2:
        details = f"Paused - {trackname}"
        small_image = "pause"
        small_text = "Currently paused"
        # Update Rich Presence
        rpc.update(details=details,state=state,small_image=small_image,large_image=assetName,large_text=trackname,small_text=small_text)
    # If the song is stopped (rather, anything else)
    else:
        # Update Rich Presence with non-dynamic data
        rpc.update(details="Stopped",state="Nothing is currently playing",small_image="stop",large_image=assetName,large_text="There's nothing here!",small_text="Currently stopped")

# Run update loop on a separate thread so the menu bar app can run on the main thread
class BackgroundUpdate(Thread):
    def run(self,*args,**kwargs):
        # Loop for the rest of the runtime
        while True:
            # Call update function
            try:
                update()
            except Exception as e:
                print(e)
                quit_application()
            # Wait because Discord only accepts the newest Rich Presence update every 15 seconds
            sleep(15)

# Grab class and start it
background_update = BackgroundUpdate()
background_update.start()

# Define menu bar object and run it
class OngakuApp(object):
    def __init__(self):
        self.app = App("Ongaku", "♫")

    def run(self):
        self.app.run()

if __name__ == '__main__':
    app = OngakuApp()
    app.run()
