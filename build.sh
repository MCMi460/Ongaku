# Delete previous build files
rm -rf ./build/
rm -rf ./dist/
rm setup.py

python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt py2app
py2applet --make-setup main.py images/AppIcon.icns
sed -i '' -e "s/)/    name='Ongaku')/" setup.py
python setup.py py2app
open dist
