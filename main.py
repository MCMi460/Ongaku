import sys

if not sys.platform.startswith('darwin'):
    sys.exit('Non-MacOS is not yet supported. Sorry!')

import platform, os, json, time, threading, subprocess, urllib, typing, enum, datetime
import rumps, requests, pypresence

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

class Script:
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
                cmd % appName
            ],
            capture_output = True
        ).stdout.decode('utf-8').rstrip()

    @property
    def song(self) -> 'Script.Track':
        position, duration = Script._get_duration()
        return Script.Track(
            ID = Script._get_ID(),
            State = Script._get_state(),
            Name = Script._get_trackname(),
            Album = Script._get_album(),
            Artist = Script._get_artist(),
            #Lyrics = Script._get_lyrics(),
            Position = position,
            Duration = duration,
            Cloud_Status = Script._get_cloud(),
        )

    # database ID
    def _get_ID() -> typing.Optional[int]:
        cmd = """
            on run
                tell application "%s"
                    return database ID of current track
                end tell
            end run
        """
        response = Script._process(cmd)
        return int(response) if response else None

    # stopped, paused, playing
    def _get_state() -> 'Script.State':
        cmd = """
            on run
        		tell application "%s"
        			return player state
        		end tell
            end run
        """
        return Script.State[
            Script._process(cmd)
            .upper()
            .replace(' ', '_')
        ]

    # name
    def _get_trackname() -> str:
        cmd = """
            on run
        		tell application "%s"
        			return name of current track
        		end tell
            end run
        """
        return Script._process(cmd)

    # album
    def _get_album() -> str:
        cmd = """
            on run
        		tell application "%s"
                    return album of current track
        		end tell
            end run
        """
        return Script._process(cmd)

    # artist
    def _get_artist() -> str:
        cmd = """
            on run
        		tell application "%s"
                    return artist of current track
        		end tell
            end run
        """
        return Script._process(cmd)

    # lyrics ... deprecated
    def _get_lyrics() -> str:
        cmd = """
            on run
        		tell application "%s"
        			return lyrics of current track
        		end tell
            end run
        """
        return Script._process(cmd)

    # position and duration
    def _get_duration() -> typing.Tuple[typing.Optional[float], typing.Optional[float]]:
        cmd = """
            on run
        		tell application "%s"
        			return player position & duration of current track
        		end tell
            end run
        """
        try: return tuple(map(float, Script._process(cmd).split(', ')))
        except: return None, None

    # cloud status
    def _get_cloud() -> typing.Optional['Script.Cloud_Status']:
        cmd = """
            on run
        		tell application "%s"
        			return cloud status of current track
        		end tell
            end run
        """
        try:
            return Script.Cloud_Status[
                Script._process(cmd)
                .upper()
                .replace(' ', '_')
            ]
        except KeyError:
            return None

    # artwork ... deprecated for now
    def _get_artwork() -> str:
        cmd = """
            on run
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
            coversPath = os.path.join(path, 'covers')
            filePath = os.path.join(coversPath, id + '.' + format)
            if not os.path.isdir(coversPath):
                os.mkdir(coversPath)
            if not os.path.isfile(filePath):
                with open(filePath, 'wb+') as file:
                    file.write(bytes.fromhex(data.lstrip('«data tdta').rstrip('»')))
        return response

class Client(rumps.App):
    def __init__(self):
        self.rpc = None
        self.savedResults = {}
        self.allowJoiners = False
        self.connect()
        threading.Thread(target = self.routine, daemon = True).start()

        super().__init__('Ongaku', title = '♫')

    def create_instance(self, clientID:str = '402370117901484042', pipe:int = 0):
        self.rpc = pypresence.Presence(clientID, pipe = pipe)

    def connect(self):
        if not self.rpc:
            self.create_instance()
        try:
            self.rpc.connect()
        except Exception as e:
            self.handle_error(e, True)

    def handle_error(self, error:Exception, quit:bool = False):
        with open(path + '/error.txt', 'a') as file:
            file.write('[%s] %s\n' % (datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), error))
        if quit:
            rumps.alert('Error in Ongaku', '"%s"' % error)
            raise error
            sys.exit()
        print(error)
        rumps.notification('Error in Ongaku', 'Make an issue if error persists', '"%s"' % error)

    def routine(self):
        while True:
            track = Script().song
            # Script._get_artwork()
            # Add local artwork loading at a later date
            try:
                self.update(track)
            except Exception as err:
                self.handle_error(err, True)
            time.sleep(2)

    def update(self, track:dict):
        dict = {
            'large_image': assetName,
            'large_text': appName,
        }
        if track.State != Script.State.STOPPED:
            dict['details'] = track.Name.ljust(2, '_')[:127]
            dict['state'] = ', '.join(filter(lambda str : str != '', [track.Artist, track.Album if not track.Album in (track.Name, track.Name + ' - Single') else '']))
            if track.State == Script.State.PAUSED:
                dict['state'] = 'Paused - ' + dict['state']
            else:
                dict['start'] = time.time()
                dict['end'] = time.time() + (track.Duration - track.Position)
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
                    if not self.allowJoiners:
                        dict['buttons'] = [{
                            'label': 'View in Store',
                            'url': store[0]['trackViewUrl'],
                        },]
                        dict['large_image'] = store[0]['artworkUrl100']
                        dict['large_text'] = dict['details']
                        # Lyrics support is deprecated
                        #if track.Lyrics != '':
                        #    dict['buttons'].append(
                        #        {
                        #            'label': 'View Lyrics',
                        #            'url':
                        #                'https://music.mi460.dev/#api=True&lyrics='
                        #                + urllib.parse.quote(track.Lyrics)
                        #                + '&song='
                        #                + urllib.parse.quote(track.Name)
                        #                + '&state='
                        #                + urllib.parse.quote(dict['state'])
                        #        }
                        #    )
            self.rpc.update(**dict)
        else:
            self.rpc.clear()

if __name__ == '__main__':
    Client().run()
