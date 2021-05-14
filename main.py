from sys import platform, exit, argv # This gives us our current OS' information

# Make sure platform is MacOS
if platform.startswith("darwin") != True:
    print(f"There is not currently a {platform} version supported, please use a different application.")
    quit()
else:
    from rumps import App, clicked, alert, notification # This module adds menu bar support
    from platform import mac_ver # Get MacOS version
    from requests import get # This lets us receive website data
    from json import loads # This is useful for formatting some web data in the future
    from threading import Thread # This allows us to run multiple blocking processes at once
    from time import sleep, time # This lets us get the exact time stamp as well as wait time
    from pypresence import Presence # This is what connects us to Discord and lets us change our status
    from subprocess import run # This will allow us to execute Apple Script

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

# Set Discord Rich Presence ID
rpc = Presence('402370117901484042')

def connect():
    # Set fails variable to 0
    fails = 0

    while True:
        # Attempt to connect to Discord. Will wait until it connects
        try:
            rpc.connect()
            break
        except Exception as e:
            print(e)
            sleep(0.1)
            fails += 1
            if fails > 500:
                # If program fails 500 consecutive times in a row to connect, then send a notification with the exception
                notification("Error in Ongaku", "Make an issue if error persists", f"\"{e}\"")
                exit(f"Error, failed after 500 attempts\n\"{e}\"")
            continue

connect()

try:
    # Sometimes PyPresence returns a Client ID error even if we already connected, so this will try to connect again
    rpc.connect()
except:
    exit("Failed to connect")

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
        local = False
        trackname = get_trackname()
        if len(trackname) < 2:
            trackname = "Song has no name assigned"
        elif len(trackname) > 128:
            trackname = trackname[:127]
        state = get_info()
        if len(state) < 2:
            state = "Song has no artist assigned"
        elif len(state) > 128:
            state = state[:127]
        type = get_cloud()
        if type == "purchased" or type == "subscription":
            try:
                # Use Music's API to grab Store URL by searching for it. Apple Script cannot get the Store URL, so I had to code this alternate method
                url = loads(get(f"https://itunes.apple.com/search?term={trackname.replace(' ','+')}+{trackname.replace(' ','+')}+{state.replace(', ',' ').replace(' ','+')}").content.decode('utf-8'))["results"][0]['trackViewUrl']
            except:
                # If it cannot get a song, then it will just update without the Store URL button
                local = True
        else:
            # Song is either self-uploaded or otherwise.
            local = True
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
        # Update Rich Presence
        if local:
            # Display without Store URL button
            rpc.update(details=details,state=state,small_image=small_image,large_image=assetName,large_text=details,small_text=small_text,start=epoch,end=epoch + (duration - pos))
        else:
            # Update RPC with Store URL button included
            rpc.update(details=details,state=state,small_image=small_image,large_image=assetName,large_text=trackname,small_text=small_text,start=epoch,end=epoch + (duration - pos),buttons=[{"label": "View in Store", "url": url}])
    # If the song is paused
    elif status == 2:
        details = f"Paused - {trackname}"
        small_image = "pause"
        small_text = "Currently paused"
        # Update Rich Presence
        if local:
            # Display without Store URL button
            rpc.update(details=details,state=state,small_image=small_image,large_image=assetName,large_text=trackname,small_text=small_text)
        else:
            # Update RPC with Store URL button included
            rpc.update(details=details,state=state,small_image=small_image,large_image=assetName,large_text=trackname,small_text=small_text,buttons=[{"label": "View in Store", "url": url}])
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
                notification("Error in Ongaku", "Make an issue if error persists", f"\"{e}\"")
                print(e)
            # Wait because Discord only accepts the newest Rich Presence update every 15 seconds
            sleep(15)

# Grab class and start it
background_update = BackgroundUpdate()
background_update.start()

# Define menu bar object and run it
class OngakuApp(App):
    # Make a reconnect button
    @clicked("Reconnect")
    def prefs(self, _):
        # Attempt to connect to Discord, and if failed, it will output an alert with the exception
        try:
            rpc.connect()
            alert("Connected to Discord!")
        except Exception as e:
            alert(f"Failed to connect:\n\"{e}\"")

# Make sure process is the main script and run status bar app
if __name__ == "__main__":
    OngakuApp("♫").run()
