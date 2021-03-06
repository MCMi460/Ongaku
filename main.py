from sys import platform, exit # This gives us our current OS' information

# Make sure platform is MacOS
if platform.startswith("darwin") != True:
    exit(f"There is not currently a {platform} version supported, please use a different application.")
else:
    from rumps import App, clicked, alert, notification, quit_application # This module adds menu bar support
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
    exit("Apple Script is broken before Big Sur 11.3 - please update to use this program.")
# Don't know what this is about, but I wanted to port Spotlight's code to Python exactly, so I kept this
elif ver == 10.15:
    assetName = "music_logo"
# Use old iTunes logo and appname
else:
    appName = "iTunes"
    assetName = "itunes_logo"

# Set Discord Rich Presence ID
rpc = Presence('402370117901484042')

from os.path import expanduser # Get home directory path
from datetime import datetime # Lets us get current time and date

path = expanduser("~/Library/Application Support/Ongaku")

def log_error(error):
    print(error)
    while True:
        try:
            with open(f'{path}/error.txt',"a") as append:
                append.write(f'[{datetime.now().strftime("%Y/%m/%d %H:%M:%S")}] {error}\n')
            break
        except:
            from os import mkdir # Create the directory
            mkdir(path)
            continue

def connect():
    # Set fails variable to 0
    fails = 0

    while True:
        # Attempt to connect to Discord. Will wait until it connects
        try:
            rpc.connect()
            break
        except Exception as e:
            sleep(0.1)
            fails += 1
            if fails > 500:
                # If program fails 500 consecutive times in a row to connect, then send a notification with the exception
                notification("Error in Ongaku", "Make an issue if error persists", f"\"{e}\"")
                log_error(e)
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

def process(cmd):
    return run(['osascript', '-e', cmd % appName], capture_output=True).stdout.decode('utf-8').rstrip()

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
    return int(process(cmd))

# Get trackname will return the name of the current track
def get_trackname():
    cmd = """
        on run
    		tell application "%s"
    			return name of current track
    		end tell
        end run
    """
    return process(cmd)

# Get info will return the album and artist of the current track
def get_info():
    cmd = """
        on run
    		tell application "%s"
                return {album,artist} of current track
    		end tell
        end run
    """
    return process(cmd)

# Get duration returns the Music player's position and the duration of the current track
def get_duration():
    cmd = """
        on run
    		tell application "%s"
    			return player position & duration of current track
    		end tell
        end run
    """
    return process(cmd)

# Find out whether this is a user-uploaded song or otherwise
def get_cloud():
    cmd = """
        on run
    		tell application "%s"
    			return cloud status of current track
    		end tell
        end run
    """
    return process(cmd)

# Contains logic code that calls functions to grab data using Apple Script and updates the RPC controller with the data
def update():
    # Grab playing status
    status = get_status()
    global player_status
    player_status = status
    # If the song is on the player get name, album, and artist
    if status > 0:
        local = False
        trackname = get_trackname()
        global cached_track
        cached_track = trackname
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
        # Get current epoch time
        global start
        start = round(time())
        stamp = get_duration()
        # Format position and duration data
        pos = round(float(stamp.split(", ")[0]))
        duration = round(float(stamp.split(", ")[1]))
        global end
        end = start + (duration - pos)
        # Update Rich Presence
        if local:
            # Display without Store URL button
            rpc.update(details=details,state=state,large_image=assetName,large_text=details,start=start,end=end)
        else:
            # Update RPC with Store URL button included
            rpc.update(details=details,state=state,large_image=assetName,large_text=details,start=start,end=end,buttons=[{"label": "View in Store", "url": url}])
    # If the song is paused
    elif status == 2:
        details = f"Paused - {trackname}"
        # Update Rich Presence
        if local:
            # Display without Store URL button
            rpc.update(details=details,state=state,large_image=assetName,large_text=details)
        else:
            # Update RPC with Store URL button included
            rpc.update(details=details,state=state,large_image=assetName,large_text=details,buttons=[{"label": "View in Store", "url": url}])
    # If the song is stopped (rather, anything else)
    else:
        cached_track = ""
        # Update Rich Presence with non-dynamic data
        rpc.update(details="Stopped",state="Nothing is currently playing",large_image=assetName,large_text="There's nothing here!")

# Run update loop on a separate thread so the menu bar app can run on the main thread
class BackgroundUpdate(Thread):
    def run(self,*args,**kwargs):
        global call_update
        # Set fails variable to 0
        fails = 0
        # Loop for the rest of the runtime
        while True:
            # Only run when app is activated
            if activated:
                # The following logic statements are to check if the song playing has changed. If so, it will queue it up for Discord to update
                # Check if track playing is different
                if cached_track != str(get_trackname()):
                    call_update = True
                # Check if user changed the player state
                elif player_status != get_status():
                    call_update = True
                elif player_status == 1:
                    stamp = get_duration()
                    # If player status is set to playing, check if the start vs end time is within 15 (or so) seconds of what it's supposed to be. If not, then update
                    if round(end - start) - round(float(stamp.split(", ")[1]) - float(stamp.split(", ")[0])) not in range(15):
                        call_update = True
                if call_update:
                    # Call update function
                    try:
                        update()
                        fails = 0
                    except Exception as e:
                        notification("Error in Ongaku", "Make an issue if error persists", f"\"{e}\"")
                        log_error(e)
                        fails += 1
                        if fails > 5:
                            print(f"Error, failed after 5 attempts\n\"{e}\"")
                            quit_application()
                            exit()
                            # Here, we just use everything we can to get the application to stop running!
                    call_update = False
                else:
                    # Wait one second
                    sleep(1)

# Make sure it runs on start
activated = True
# Set variables for slight optimizations to code
cached_track = ""
player_status = ""
start = 0
end = 0
call_update = True

# Grab class and start it
background_update = BackgroundUpdate()
background_update.start()

# Define menu bar object and run it
class OngakuApp(App):
    def __init__(self):
        super(OngakuApp, self).__init__("Ongaku",title="???")
        self.menu = ["Disable", "Reconnect"]
    # Make an activate button
    @clicked("Disable")
    def button(self, sender):
        global activated
        activated = not activated
        global call_update
        if sender.title == "Disable":
            sender.title = "Enable"
            rpc.clear()
            call_update = False
        else:
            sender.title = "Disable"
            call_update = True
    # Make a reconnect button
    @clicked("Reconnect")
    def reconnect(self, _):
        # Attempt to connect to Discord, and if failed, it will output an alert with the exception
        try:
            rpc.clear()
        except:
            pass
        try:
            rpc.connect()
            alert("Connected to Discord!\n(You may have to restart Discord)")
        except Exception as e:
            alert(f"Failed to connect:\n\"{e}\"")
            log_error(e)

# Make sure process is the main script and run status bar app
if __name__ == "__main__":
    OngakuApp().run()
