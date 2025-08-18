from Foundation import *
from PyObjCTools import AppHelper

defaultCenter = NSDistributedNotificationCenter.defaultCenter()

music_bundle_id = "com.apple.Music"
name = NSNotificationName(f"{music_bundle_id}.playerInfo")


class Observer(NSObject):
    def init(self):
        defaultCenter.addObserver_selector_name_object_(
            self, "receiveNotification:", name, None
        )
        return self

    def kill(self):
        defaultCenter.removeObserver_name_object_(self, name, None)

    def receiveNotification_(self, notification):
        print(notification)


catcher = Observer.alloc().init()

if __name__ == "__main__":
    AppHelper.runEventLoop()

catcher.kill()
