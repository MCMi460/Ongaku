# Delete previous build files
rm -rf ./build/
rm -rf ./dist/

python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt py2app
python setup.py py2app
open dist
