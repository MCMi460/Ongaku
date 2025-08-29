# Thrown-together AppKit graphics user interface
from AppKit import *
from PyObjCTools import AppHelper
from main import VER_STR, VER_STR_LONG, Config
from webbrowser import open as open_url
from phone import (
    desktopUrl,
    mobileUrl,
    desktopShortcut,
    mobileShortcut,
    await_shortcut_addition,
    disable_button,
    shortcut_exists,
    start_server,
)
from threading import Thread

configs = Config.read()

application = NSApplication.sharedApplication()


# Overwrite window closing method to comply with rumps
class Delegate(NSObject):
    def windowShouldClose_(self, window: NSWindow) -> bool:
        window.hide()
        return False

    def updateConfig_(self, sender):
        global configs
        for setting in configMatch.keys():
            if configMatch[setting] == sender.title():
                configs[setting] = bool(sender.state())
                Config.write(configs)
                break

    def desktopShortcut_(self, sender):
        sender.setTitle_("⧖ Waiting...")
        open_url(desktopUrl)
        sender.setEnabled_(False)
        Thread(
            target=await_shortcut_addition,
            args=(
                sender,
                desktopShortcut,
                airdropButton.object,
            ),
            daemon=True,
        ).start()

    def mobileShortcut_(self, sender):
        sender.setTitle_("⧖ Waiting...")
        open_url(mobileUrl)
        sender.setEnabled_(False)
        Thread(
            target=await_shortcut_addition,
            args=(
                sender,
                mobileShortcut,
                airdropButton.object,
            ),
            daemon=True,
        ).start()

    def airdropStart_(self, sender):
        Thread(target=start_server, args=(airdropButton.callback,), daemon=True).start()


delegate = Delegate.alloc().init()

configMatch = {
    "uploadCovers": "Display local cover art\n(WARNING: This uploads your cover arts to freeimage.host)",
    "allowJoiners": "Allow invites to/from other Ongaku users\n(Not recommended)",
}


# Windows
class Window(NSWindow):
    def showFront(self):
        self.orderFrontRegardless()
        self.makeKeyAndOrderFront_(self)
        application.activate()

    def hide(self):
        self.orderOut_(
            self
        )  # This little 'hack' fixes seg faults when running with rumps


# Links
class URL:
    def __init__(self, link: str):
        self.object = NSURL.URLWithString_(link)


# Text fields
class Text:
    def __init__(self, rect: NSRect):
        self.object = NSText.alloc().initWithFrame_(rect)
        self.object.setDrawsBackground_(False)
        self.object.setEditable_(False)
        self.object.setRichText_(True)
        self.object.setFont_(NSFont.systemFontOfSize_(NSFont.systemFontSize()))
        # self.object.setSelectable_(False)

    @property
    def string(self) -> str:
        return self.object.string()

    @string.setter
    def string(self, text: str):
        self.object.setString_(text)

    def setBold(self):
        self.object.textStorage().applyFontTraits_range_(
            NSBoldFontMask, NSMakeRange(0, len(self.string))
        )

    def setItalic(self):
        self.object.textStorage().applyFontTraits_range_(
            NSItalicFontMask, NSMakeRange(0, len(self.string))
        )

    def addLink(self, link: URL, start: int, length: int):
        self.object.textStorage().addAttribute_value_range_(
            NSLinkAttributeName, link.object, NSMakeRange(start, length)
        )

    def hideLink(self):
        # linkAttrs = self.object.linkTextAttributes()
        # for key in linkAttrs:
        #    print("%s:%s"%(key, linkAttrs[key]))
        self.object.setLinkTextAttributes_(
            NSDictionary.dictionaryWithDictionary_(
                {
                    NSUnderlineStyleAttributeName: NSUnderlineStyleNone,
                    NSCursorAttributeName: NSCursor.pointingHandCursor(),
                }
            )
        )

    def center(self):
        self.object.setAlignment_(NSCenterTextAlignment)

    def rightAlign(self):
        self.object.setAlignment_(NSRightTextAlignment)

    def small(self):
        self.object.setFont_(NSFont.systemFontOfSize_(NSFont.smallSystemFontSize()))


# Buttons
class Button:
    def __init__(self, rect: NSRect):
        self.object = NSButton.alloc().initWithFrame_(rect)
        self.object.setTarget_(delegate)

    @property
    def title(self) -> str:
        return self.object.title()

    @title.setter
    def title(self, text: str):
        self.object.setTitle_(text)

    def setAction(self, action: str):
        self.object.setAction_(action)

    def enable(self):
        self.object.setEnabled_(True)

    def disable(self):
        self.object.setEnabled_(False)


class Checkbox(Button):
    def __init__(self, rect: NSRect):
        super().__init__(rect)
        self.object.setButtonType_(NSButtonTypeSwitch)

    @property
    def state(self) -> bool:
        return bool(self.object.state())

    @state.setter
    def state(self, toggle: bool):
        self.object.setState_(int(toggle))


# Images
class Image:
    def __init__(self, rect: NSRect):
        self.object = NSImageView.alloc().initWithFrame_(rect)

    @property
    def path(self) -> str:
        return r"¯\_(ツ)_/¯"

    @path.setter
    def path(self, file: str):
        image = NSImage.alloc().initByReferencingFile_(file)
        image.setScalesWhenResized_(True)
        self.object.setImage_(image)


# Actual view-building

# Set application accent color
application._setAccentColor_(NSColor.redColor())
# NSColor.colorWithCalibratedRed_green_blue_alpha_(0.988, 0.235, 0.267, 1.0)

# Create NSWindow -- 'About' page
aboutWindow = Window.alloc().initWithContentRect_styleMask_backing_defer_(
    NSMakeRect(0.0, 0.0, 300.0, 300.0),
    NSTitledWindowMask | NSClosableWindowMask | NSMiniaturizableWindowMask,
    NSBackingStoreBuffered,
    False,
)
aboutWindow.center()
aboutWindow.setTitle_("About Ongaku")
aboutWindow.setDelegate_(delegate)
aboutWindow.hide()

icon = Image(NSMakeRect(85.0, 150.0, 130.0, 130.0))
icon.path = "images/AppIcon.iconset/icon_1024x1024.png"
aboutWindow.contentView().addSubview_(icon.object)

title = Text(NSMakeRect(18.0, 125.0, 265.0, 20.0))
title.string = "Ongaku"
title.addLink(URL("https://github.com/MCMi460/Ongaku"), 0, 6)
title.hideLink()
title.center()
title.setBold()
aboutWindow.contentView().addSubview_(title.object)
author = Text(NSMakeRect(18.0, 100.0, 265.0, 20.0))
author.string = "You know, ongaku."
author.addLink(URL(r"https://jisho.org/word/%E9%9F%B3%E6%A5%BD"), 10, 6)
author.setItalic()
author.center()
aboutWindow.contentView().addSubview_(author.object)
version = Text(NSMakeRect(18.0, 75.0, 265.0, 20.0))
version.string = VER_STR_LONG
version.center()
version.small()
aboutWindow.contentView().addSubview_(version.object)
copyrightText = Text(NSMakeRect(18.0, 25.0, 265.0, 20.0))
copyrightText.string = "™ and © 2021-2025 Delta Inc.\nAll Rights Reserved."
copyrightText.addLink(URL("https://mi460.dev/"), 0, 49)
copyrightText.hideLink()
copyrightText.center()
copyrightText.small()
aboutWindow.contentView().addSubview_(copyrightText.object)

# Create NSWindow -- 'Preferences' page
preferencesWindow = Window.alloc().initWithContentRect_styleMask_backing_defer_(
    NSMakeRect(0.0, 0.0, 380.0, 300.0),
    NSTitledWindowMask | NSClosableWindowMask | NSMiniaturizableWindowMask,
    NSBackingStoreBuffered,
    False,
)
preferencesWindow.center()
preferencesWindow.setTitle_("Ongaku Settings")
preferencesWindow.setDelegate_(delegate)
preferencesWindow.hide()

uploadCoversButton = Checkbox(NSMakeRect(30.0, 180.0, 350.0, 40.0))
uploadCoversButton.title = configMatch["uploadCovers"]
uploadCoversButton.state = configs["uploadCovers"]
uploadCoversButton.setAction("updateConfig:")
preferencesWindow.contentView().addSubview_(uploadCoversButton.object)

allowJoinersButton = Checkbox(NSMakeRect(30.0, 120.0, 350.0, 40.0))
allowJoinersButton.title = configMatch["allowJoiners"]
allowJoinersButton.state = configs["allowJoiners"]
allowJoinersButton.setAction("updateConfig:")
preferencesWindow.contentView().addSubview_(allowJoinersButton.object)

# Create NSWindow -- 'iPhone' page
phoneWindow = Window.alloc().initWithContentRect_styleMask_backing_defer_(
    NSMakeRect(0.0, 0.0, 380.0, 300.0),
    NSTitledWindowMask | NSClosableWindowMask | NSMiniaturizableWindowMask,
    NSBackingStoreBuffered,
    False,
)
phoneWindow.center()
phoneWindow.setTitle_("iPhone Connect")
phoneWindow.setDelegate_(delegate)
phoneWindow.hide()

phoneIcon = Image(NSMakeRect(145.0, 180.0, 90.0, 90.0))
phoneIcon.path = "images/iphone.gen2.crop.circle.png"
phoneWindow.contentView().addSubview_(phoneIcon.object)

title = Text(NSMakeRect(57.0, 145.0, 265.0, 20.0))
title.string = "iPhone Connect"
title.center()
title.setBold()
phoneWindow.contentView().addSubview_(title.object)

desktopAdd = Button(NSMakeRect(200.0, 100.0, 150.0, 40.0))
desktopAdd.title = "+ Add Shortcut"
desktopAdd.setAction("desktopShortcut:")
if shortcut_exists(desktopShortcut):
    disable_button(desktopAdd.object)
phoneWindow.contentView().addSubview_(desktopAdd.object)

desktopAddText = Text(NSMakeRect(30.0, 110.0, 150.0, 20.0))
desktopAddText.string = "OngakuDesktop:"
desktopAddText.rightAlign()
phoneWindow.contentView().addSubview_(desktopAddText.object)

mobileAdd = Button(NSMakeRect(200.0, 60.0, 150.0, 40.0))
mobileAdd.title = "+ Add Shortcut"
mobileAdd.setAction("mobileShortcut:")
if shortcut_exists(mobileShortcut):
    disable_button(mobileAdd.object)
phoneWindow.contentView().addSubview_(mobileAdd.object)

mobileAddText = Text(NSMakeRect(30.0, 70.0, 150.0, 20.0))
mobileAddText.string = "OngakuPhone:"
mobileAddText.rightAlign()
phoneWindow.contentView().addSubview_(mobileAddText.object)

airdropButton = Button(NSMakeRect(115.0, 20.0, 150.0, 40.0))
airdropButton.title = "Connect to iPhone"
airdropButton.setAction("airdropStart:")
if not shortcut_exists(mobileShortcut) or not shortcut_exists(desktopShortcut):
    airdropButton.disable()
phoneWindow.contentView().addSubview_(airdropButton.object)

# If running as a debug process
if __name__ == "__main__":
    application.setDelegate_(delegate)
    # Windows
    aboutWindow.orderFrontRegardless()
    preferencesWindow.orderFrontRegardless()
    phoneWindow.orderFrontRegardless()

    # Misc.
    airdropButton.callback = None

    AppHelper.runEventLoop()
