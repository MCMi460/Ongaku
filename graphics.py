# Thrown-together AppKit graphics user interface
from AppKit import *
from PyObjCTools import AppHelper
from main import VER_STR, Config

configs = Config.read()

# Overwrite window closing method to comply with rumps
class Delegate(NSObject):
    def windowShouldClose_(self, window:NSWindow) -> bool:
        window.orderOut_(window)
        return False
    
    def updateConfig_(self, sender):
        global configs
        for setting in configMatch.keys():
            if configMatch[setting] == sender.title():
                configs[setting] = bool(sender.state())
                Config.write(configs)
                break

delegate = Delegate.alloc().init()

configMatch = {
    'uploadCovers': 'Display local cover art\n(WARNING: This uploads your cover arts to freeimage.host)',
}

# Text fields
class Text:
    def __init__(self, rect:NSRect):
        self.object = NSText.alloc().initWithFrame_(rect)
        self.object.setDrawsBackground_(False)
        self.object.setEditable_(False)
        self.object.setRichText_(True)
        #self.object.setSelectable_(False)

    @property
    def string(self) -> str:
        return self.object.string()
    @string.setter
    def string(self, text:str):
        self.object.setString_(text)
    
    def setBold(self):
        self.object.textStorage().applyFontTraits_range_(NSBoldFontMask, NSMakeRange(0, len(self.string)))

    def center(self):
        self.object.setAlignment_(NSCenterTextAlignment)

# Buttons
class Button:
    def __init__(self, rect:NSRect):
        self.object = NSButton.alloc().initWithFrame_(rect)
        self.object.setTarget_(delegate)

    @property
    def title(self) -> str:
        return self.object.title()
    @title.setter
    def title(self, text:str):
        self.object.setTitle_(text)

    def setAction(self, action:str):
        self.object.setAction_(action)

class Checkbox(Button):
    def __init__(self, rect:NSRect):
        super().__init__(rect)
        self.object.setButtonType_(NSButtonTypeSwitch)
    
    @property
    def state(self) -> bool:
        return bool(self.object.state())
    @state.setter
    def state(self, toggle:bool):
        self.object.setState_(int(toggle))

# Images
class Image:
    def __init__(self, rect:NSRect):
        self.object = NSImageView.alloc().initWithFrame_(rect)

    @property
    def path(self) -> str:
        return r'¯\_(ツ)_/¯'
    @path.setter
    def path(self, file:str):
        image = NSImage.alloc().initByReferencingFile_(file)
        image.setScalesWhenResized_(True)
        self.object.setImage_(image)

# Actual view-building

# Create NSWindow -- 'About' page
aboutWindow = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
    NSMakeRect(0.0, 0.0, 300.0, 300.0),
    NSTitledWindowMask | NSClosableWindowMask | NSMiniaturizableWindowMask,
    NSBackingStoreBuffered,
    False,
)
aboutWindow.center()
aboutWindow.setTitle_('About Ongaku')
aboutWindow.setDelegate_(delegate)
aboutWindow.orderOut_(aboutWindow) # This little 'hack' fixes seg faults when running with rumps

icon = Image(NSMakeRect(85.0, 150.0, 130.0, 130.0))
icon.path = 'images/AppIcon.iconset/icon_1024x1024.png'
aboutWindow.contentView().addSubview_(icon.object)

title = Text(NSMakeRect(18.0, 125.0, 265.0, 20.0))
title.string = 'Ongaku'
title.center()
title.setBold()
aboutWindow.contentView().addSubview_(title.object)
author = Text(NSMakeRect(18.0, 100.0, 265.0, 20.0))
author.string = 'Made painstakingly by MCMi460'
author.center()
aboutWindow.contentView().addSubview_(author.object)
version = Text(NSMakeRect(18.0, 75.0, 265.0, 20.0))
version.string = VER_STR
version.center()
aboutWindow.contentView().addSubview_(version.object)

# Create NSWindow -- 'Preferences' page
preferencesWindow = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
    NSMakeRect(0.0, 0.0, 380.0, 300.0),
    NSTitledWindowMask | NSClosableWindowMask | NSMiniaturizableWindowMask,
    NSBackingStoreBuffered,
    False,
)
preferencesWindow.center()
preferencesWindow.setTitle_('Ongaku Preferences')
preferencesWindow.setDelegate_(delegate)
preferencesWindow.orderOut_(preferencesWindow)

uploadCoversButton = Checkbox(NSMakeRect(30.0, 180.0, 350.0, 40.0))
uploadCoversButton.title = configMatch['uploadCovers']
uploadCoversButton.state = configs['uploadCovers']
uploadCoversButton.setAction('updateConfig:')
preferencesWindow.contentView().addSubview_(uploadCoversButton.object)

title = Text(NSMakeRect(107.0, 260.0, 165.0, 20.0))
title.string = 'Ongaku Preferences'
title.setBold()
title.center()
preferencesWindow.contentView().addSubview_(title.object)

# If running as a debug process
if __name__ == '__main__':
    application = NSApplication.sharedApplication()
    application.setDelegate_(delegate)
    # Windows
    aboutWindow.orderFrontRegardless()
    preferencesWindow.orderFrontRegardless()

    AppHelper.runEventLoop()
