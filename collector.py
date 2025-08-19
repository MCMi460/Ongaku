from main import path, Script
import time, json, os


class Collector:
    def __init__(self):
        self.path = os.path.join(path, "collection.json")
        self.songs = (
            self.readSongs() if os.path.isfile(self.path) else self.writeSongs({})
        )
        self.recent = []

    def readSongs(self):
        with open(self.path, "r") as file:
            return json.loads(file.read())

    def writeSongs(self, songs: dict):
        with open(self.path, "w+") as file:
            file.write(json.dumps(songs))
        return songs

    def collectTrack(self, track: Script.Track):
        self.songs[track.ID] = track.subrosa
        self.writeSongs(self.songs)


# Debug process
if __name__ == "__main__":
    tester = Collector()
    tester.collectTrack(Script().song)
