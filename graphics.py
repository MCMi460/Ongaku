# Thrown-together AppKit graphics user interface
from AppKit import *
from PyObjCTools import AppHelper
from main import VER_STR

# Overwrite window closing method to comply with rumps
class Delegate(NSObject):
    def windowShouldClose_(self, window:NSWindow) -> bool:
        window.orderOut_(window)
        return False

# Text fields
class Text:
    def __init__(self, rect:NSRect):
        self.object = NSText.alloc().initWithFrame_(rect)
        self.object.setDrawsBackground_(False)
        self.object.setEditable_(False)
        self.object.setRichText_(True)
        #self.object.setSelectable_(False)

    @property
    def string(self):
        return self.object.string()
    @string.setter
    def string(self, text:str):
        self.object.setString_(text)
    
    def setBold(self):
        self.object.textStorage().applyFontTraits_range_(NSBoldFontMask, NSMakeRange(0, len(self.string)))

    def center(self):
        self.object.setAlignment_(NSCenterTextAlignment)

# Images
class Image:
    def __init__(self, rect:NSRect):
        self.object = NSImageView.alloc().initWithFrame_(rect)

    @property
    def path(self):
        return r'¯\_(ツ)_/¯'
    @path.setter
    def path(self, file:str):
        image = NSImage.alloc().initByReferencingFile_(file)
        image.setScalesWhenResized_(True)
        self.object.setImage_(image)

# Actual view-building

# Create NSWindow -- 'About' page
window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
    NSMakeRect(0.0, 0.0, 300.0, 300.0),
    NSTitledWindowMask | NSClosableWindowMask | NSMiniaturizableWindowMask,
    NSBackingStoreBuffered,
    False,
)
window.center()
window.setTitle_('About Ongaku')
window.setDelegate_(Delegate.alloc().init())
window.orderOut_(window) # This little 'hack' fixes seg faults when running with rumps

icon = Image(NSMakeRect(85.0, 150.0, 130.0, 130.0))
icon.path = 'images/AppIcon.iconset/icon_1024x1024.png'
window.contentView().addSubview_(icon.object)

title = Text(NSMakeRect(18.0, 125.0, 265.0, 20.0))
title.string = 'Ongaku'
title.center()
title.setBold()
window.contentView().addSubview_(title.object)
author = Text(NSMakeRect(18.0, 100.0, 265.0, 20.0))
author.string = 'Made painstakingly by MCMi460'
author.center()
window.contentView().addSubview_(author.object)
version = Text(NSMakeRect(18.0, 75.0, 265.0, 20.0))
version.string = VER_STR
version.center()
window.contentView().addSubview_(version.object)