# Delete previous build files
rm -rf ./build/
rm -rf ./dist/

python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt py2app
python3 setup.py py2app
open dist
