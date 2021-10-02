curl https://api.github.com/repos/MCMi460/Ongaku/zipball/main -o Ongaku.zip -L
unzip Ongaku.zip -d ./Ongaku
rm Ongaku.zip
cd ./Ongaku/*/
python3 -m venv vpy
source vpy/bin/activate
python -m pip install -r requirements.txt py2app
python setup.py py2app
open ./dist
rm ../../build.sh
