git clone https://github.com/MCMi460/Ongaku
cd Ongaku
python3 -m venv vpy
source vpy/bin/activate
python -m pip install -r requirements.txt py2app
python setup.py py2app
open ./dist
rm ../build.sh
