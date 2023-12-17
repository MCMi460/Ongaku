ONGAKU_VER = 1.3
VER_STR = 'Ongaku v%s' % ONGAKU_VER
import sys

if not sys.platform.startswith('darwin'):
    sys.exit('Non-MacOS is not yet supported. Sorry!')

import platform, os, json, time, threading, subprocess, urllib, typing, enum, datetime, webbrowser, random, faulthandler, base64
faulthandler.enable()
import rumps, requests, pypresence
if __name__ == '__main__': # Prevent import recursion
    from graphics import aboutWindow, preferencesWindow

ver = platform.mac_ver()[0].split('.')
ver = float('.'.join((ver[0], ''.join(ver[1:]))))

appName = 'Music'

if 11.3 > ver >= 11.0:
    sys.exit('Apple Script is broken before Big Sur 11.3 - please update to use this program.')
if ver >= 10.16:
    assetName = 'big_sur_logo'
elif ver == 10.15:
    assetName = 'music_logo'
else:
    appName = 'iTunes'
    assetName = 'itunes_logo'

# Working directory
path = os.path.expanduser('~/Library/Application Support/Ongaku')
if not os.path.isdir(path):
    os.mkdir(path)
configFile = os.path.join(path, 'config.json')

# Default settings
class Config:
    def init():
        Config.write({
            'uploadCovers': False,
            'allowJoiners': False,
        })
    
    def read() -> dict:
        if not os.path.isfile(configFile):
            Config.init()
        
        with open(configFile, 'r') as file:
            return json.loads(file.read())
    
    def write(configs:dict):
        with open(configFile, 'w+') as file:
            file.write(json.dumps(configs))

class Script:
    DELIMITER = '🤷'

    class State(enum.Enum):
        STOPPED = 0
        PLAYING = 1
        PAUSED = 2
        FAST_FORWARDING = 3
        REWINDING = 4

    class Cloud_Status(enum.Enum):
        UNKNOWN = 0
        PURCHASED = 1
        MATCHED = 2
        UPLOADED = 3
        INELIGIBLE = 4
        REMOVED = 5
        ERROR = 6
        DUPLICATE = 7
        SUBSCRIPTION = 8
        PRERELEASE = 9
        NO_LONGER_AVAILABLE = 10
        NOT_UPLOADED = 11

    class Track:
        def __init__(self, **kwargs) -> None:
            for key in kwargs.keys():
                self.__dict__[key] = kwargs[key]

    def _process(cmd) -> str:
        return subprocess.run(
            [
                'osascript',
                '-e',
                cmd % (Script.DELIMITER, appName)
            ],
            capture_output = True
        ).stdout.decode('utf-8').rstrip()

    @property
    def song(self) -> 'Script.Track':
        # typing.Tuple[typing.Tuple[int, str, str, str, float, 'Script.Cloud_Status', 'Script.State', float]]
        try:
            ID, Name, Album, Artist, Duration, Cloud_Status, State, Position = Script._script().split(Script.DELIMITER)
            ID = int(ID)
            Duration = float(Duration)
            Cloud_Status = Script.Cloud_Status[
                Cloud_Status
                .upper()
                .replace(' ', '_')
            ]
            State = Script.State[
                State
                .upper()
                .replace(' ', '_')
            ]
            Position = float(Position)
        except ValueError:
            ID = Name = Album = Artist = Duration = Cloud_Status = Position = None
            State = Script.State.STOPPED
        except Exception as err:
            raise err # Intentionally raise exception
        finally:
            return Script.Track(
                ID = ID,
                Name = Name,
                Album = Album,
                Artist = Artist,
                Duration = Duration,
                Cloud_Status = Cloud_Status,
                State = State,
                Position = Position,
                #Lyrics = Script._get_lyrics(),
            )

    # get all necessary fields
    def _script() -> str:
        cmd = """
            on run
                set text item delimiters to "%s"
                tell application "%s"
                    return {database ID, name, album, artist, duration, cloud status} of current track & player state & player position as text
                end tell
            end run
        """
        return Script._process(cmd)

    # lyrics ... deprecated
    def _get_lyrics() -> str:
        cmd = """
            on run
                set text item delimiters to "%s"
        		tell application "%s"
        			return lyrics of current track
        		end tell
            end run
        """
        return Script._process(cmd)

    # start and finish
    def _get_times() -> typing.Tuple[typing.Optional[float], typing.Optional[float]]:
        cmd = """
            on run
                set text item delimiters to "%s"
        		tell application "%s"
        			return {start, finish} of current track as text
        		end tell
            end run
        """
        try: return tuple(map(float, Script._process(cmd).split(Script.DELIMITER)))
        except: return None, None

    # artwork ... deprecated for now
    def _get_artwork() -> typing.Optional[str]:
        cmd = """
            on run
                set text item delimiters to "%s"
            	tell application "%s"
            		return {format, raw data} of first artwork of current track & database ID of current track
            	end tell
            end run
        """
        response = Script._process(cmd)
        if response:
            format, data, id = response.split(', ')
            if 'picture' in format:
                format = format.rstrip(' picture')
            else:
                format = format.lstrip('«class ').rstrip(' »')
            data = bytes.fromhex(data.lstrip('«data tdta').rstrip('»'))
            # Cover paths
            coversPath = os.path.join(path, 'covers')
            if not os.path.isdir(coversPath):
                os.mkdir(coversPath)
            idPath = os.path.join(coversPath, 'urls.json')
            if not os.path.isfile(idPath):
                with open(idPath, 'w+') as file: file.write(json.dumps({'ids':[]}))

            with open(idPath, 'r') as read:
                items = json.loads(read.read())
                if len([ item for item in items['ids'] if item[0] == id ]) == 0:
                    url = requests.post(
                        'https://freeimage.host/api/1/upload',
                        data = {
                            'key': '6d207e02198a847aa98d0a2a901485a5',
                            'source': base64.b64encode(data),
                        },
                    ).json()['image']['url']
                    with open(idPath, 'w') as write:
                        items['ids'].append(
                            (id, url)
                        )
                        write.write(json.dumps(items))
                else:
                    for item in items['ids']:
                        if item[0] == id:
                            url = item[1]
                            break
            return url
            # Disable writing
            #filePath = os.path.join(coversPath, id + '.' + format)
            #if not os.path.isfile(filePath):
            #    with open(filePath, 'wb+') as file:
            #        file.write(data)
            #return filePath
        return None

class Client(rumps.App):
    def __init__(self) -> None:
        self.rpc = None
        self.savedResults = {}
        self.allowJoiners = False # Not recommended
        self.uploadCovers = False
        self.handleConfigs()
        self.prevTrack = None
        self.metaCheckVar = 0
        self.connect()
        threading.Thread(target = self.routine, daemon = True).start()

        super().__init__('Ongaku', icon = 'images/icon_light.png', template = True, quit_button = None)

    def handleConfigs(self):
        config = Config.read()
        if config['allowJoiners'] and not self.allowJoiners:
            self.allowJoiners = random.getrandbits(64)
            self.rpc.register_event('ACTIVITY_JOIN', self.join)
            self.rpc.subscribe('ACTIVITY_JOIN')
        elif not config['allowJoiners'] and self.allowJoiners:
            self.allowJoiners = False
            self.rpc.unsubscribe('ACTIVITY_JOIN')
        self.uploadCovers = config['uploadCovers']

    @rumps.clicked(VER_STR)
    def About(self, sender):
        aboutWindow.orderFrontRegardless()
    
    @rumps.clicked('Preferences')
    def Preferences(self, sender):
        preferencesWindow.orderFrontRegardless()
    
    @rumps.clicked('Quit')
    def Quit(self, sender):
        rumps.quit_application()

    def create_instance(self, clientID:str = '402370117901484042') -> None:
        for pipe in range(3):
            try:
                self.rpc = pypresence.Client(clientID, pipe = pipe)
                return
            except Exception as err:
                pass
        raise err

    def connect(self) -> None:
        if not self.rpc:
            self.create_instance()
        try:
            self.rpc.start()
        except Exception as e:
            self.handle_error(e, True)

    def handle_error(self, error:Exception, quit:bool = False) -> None:
        with open(path + '/error.txt', 'a') as file:
            file.write('[%s] %s\n' % (datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), error))
        if quit:
            rumps.alert('Error in Ongaku', '"%s"' % error)
            raise error
            sys.exit()
        print(error)
        rumps.notification('Error in Ongaku', 'Make an issue if error persists', '"%s"' % error)

    def join(self, event:dict):
        secret = json.loads(event['secret'])
        webbrowser.open(secret['url'])

    def stateChange(self, track:Script.Track) -> bool:
        return (
            not self.prevTrack
            or (
                not (self.prevTrack.State == track.State == Script.State.STOPPED)
                and (
                    self.prevTrack.State != track.State
                    or self.prevTrack.ID != track.ID
                    or (abs(self.prevTrack.metaCheck - (time.time() + (track.Duration - track.Position))) > 2 and track.State != Script.State.PAUSED)
                )
            )
        )

    def routine(self) -> None:
        while True:
            track = Script().song
            imageUrl = None
            self.handleConfigs()

            if self.stateChange(track) or self.allowJoiners:
                self.prevTrack = track
                try:
                    if track.State != Script.State.STOPPED:
                        self.prevTrack.metaCheck = time.time() + (track.Duration - track.Position)
                        if self.uploadCovers:
                            imageUrl = Script._get_artwork()
                except Exception as err:
                    self.handle_error(err)
                try:
                    self.update(track, imageUrl)
                    time.sleep(1)
                except Exception as err:
                    self.handle_error(err, True)
            time.sleep(1)

    def update(self, track:Script.Track, imageUrl:str = None) -> None:
        dict = {
            'large_image': assetName if not imageUrl else imageUrl,
            'large_text': appName,
        }
        if track.State != Script.State.STOPPED:
            dict['details'] = track.Name.ljust(2, '_')[:127]
            dict['state'] = ' — '.join(filter(lambda str : str != '', [track.Artist, track.Album if not track.Album in (track.Name, track.Name + ' - Single') else '']))
            if track.State == Script.State.PAUSED:
                dict['small_image'] = 'pause'
                dict['small_text'] = 'Paused'
            elif track.Position is not None and track.Duration:
                dict['start'] = time.time() + track.Position
                dict['end'] = time.time() + (track.Duration - track.Position)
                dict['small_image'] = 'play'
                dict['small_text'] = 'Playing'
            dict['state'] = dict['state'].ljust(2, '_')[:127]

            if track.Cloud_Status in (
                Script.Cloud_Status.PURCHASED,
                Script.Cloud_Status.SUBSCRIPTION
            ):
                searchString = 'https://itunes.apple.com/search?term=' + '+'.join([track.Name, track.Artist]).replace(' ', '+')
                if searchString in self.savedResults:
                    store = self.savedResults[searchString]
                else:
                    store = requests.get(searchString).json()['results']
                    self.savedResults[searchString] = store
                if len(store) > 0:
                    if not self.uploadCovers:
                        dict['large_image'] = store[0]['artworkUrl100'] 
                    if not self.allowJoiners:
                        dict['buttons'] = [{
                            'label': 'View in Store',
                            'url': store[0]['trackViewUrl'],
                        },]
                    else:
                        dict['join'] = json.dumps({
                            'url': store[0]['trackViewUrl'],
                            'pos': track.Position,
                        })
                        dict['party_id'] = str(self.allowJoiners)
                        dict['party_size'] = [1, 2]
            if dict['large_image'] != assetName:
                dict['large_text'] = dict['details']
            self.rpc.set_activity(**dict)
        else:
            self.rpc.clear_activity()

if __name__ == '__main__':
    app = Client()
    app.menu = [
        rumps.MenuItem(
            VER_STR,
            icon = 'images/AppIcon.iconset/icon_1024x1024.png',
            dimensions = (18, 18),
        ),
        'Preferences',
        None,
        rumps.MenuItem('Quit', key = 'q'),
    ]
    app.run()
