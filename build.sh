curl https://codeload.github.com/MCMi460/Ongaku/zip/refs/heads/main -o Ongaku.zip
unzip Ongaku.zip
rm Ongaku.zip
cd Ongaku-main
python3 -m venv vpy
source vpy/bin/activate
python -m pip install -r requirements.txt py2app
python setup.py py2app
open ./dist
rm ../build.sh
