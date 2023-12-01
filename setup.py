from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'iconfile': 'images/AppIcon.icns',
    'plist': {
        'CFBundleName': 'Ongaku',
        'CFBundleShortVersionString': '1.3',
        'LSUIElement': True,
    },
    'packages': ['rumps'],
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

loopThrough('images')

print('\n'.join(list(map(str, DATA_FILES))))

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name='Ongaku')
