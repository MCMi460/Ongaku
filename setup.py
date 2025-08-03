from setuptools import setup
from main import ONGAKU_VER, VER_STR
from datetime import datetime

APP = ["main.py"]
DATA_FILES = []
OPTIONS = {
    "iconfile": "images/AppIcon.icns",
    "plist": {
        "CFBundleName": "Ongaku",
        "CFBundleShortVersionString": ONGAKU_VER,
        "CFBundleGetInfoString": VER_STR,
        "LSUIElement": True,
        "CFBundleIdentifier": "dev.mi460.ongaku",
        "NSHumanReadableCopyright": "Copyright © 2021-%s Delta Inc.\nAll rights reserved."
        % datetime.now().year,
    },
    "packages": ["rumps"],
}

import os


def loopThrough(directory):
    files = []
    for file in os.listdir(directory):
        cur = os.path.join(directory, file)
        if os.path.isfile(cur):
            files.append(cur)
        elif os.path.isdir(cur):
            loopThrough(cur)
    DATA_FILES.append((directory, files))


loopThrough("images")

print("\n".join(list(map(str, DATA_FILES))))

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
    name="Ongaku",
)
