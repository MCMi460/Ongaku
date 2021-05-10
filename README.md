# Ongaku
_You know, [ongaku](https://jisho.org/word/%E9%9F%B3%E6%A5%BD)._

A port of **[Ongaku](https://github.com/spotlightishere/Ongaku)** to Python. Why? I don't know.

A simple application providing the now playing state from iTunes (or the Music app) as RPC in Discord via [PyPresence](https://github.com/qwertyquerty/pypresence).

## How to use

Unzip and open the latest x86_64 version from the [releases tab](https://github.com/MCMi460/Ongaku/releases)

## How to build

**Step 1:**

### [Download master.zip](https://github.com/MCMi460/Ongaku/archive/main.zip)
Unzip, then type this in terminal: `cd ~/Downloads/Ongaku-main`

Now, we're going to install the required modules. Just copy `python3 -m pip install -r requirements.txt` into the terminal.

Next, type `python3 -m pip install py2app` to install our application builder.

**Step 2:**

Now, let's run the app to make sure nothing breaks. Copy `python3 main.py` to the terminal and make sure the app runs well.

**Step 3:**

If nothing breaks or acts weird, then go ahead and type `python3 setup.py py2app` in the terminal.

Give it time to finish, then type `open ./dist` and enjoy your app!

---
If you have any issues, [contact me here](https://mi460.dev/bugs).

### Credits
[Spotlight](https://github.com/spotlightishere) for (unknowingly and unwillingly) letting me use their code as reference for this.

<a href="https://mi460.dev/github"><img src="https://img.shields.io/static/v1?label=MCMi460&amp;message=Github&amp;color=c331d4"></a>
<a href="https://mi460.dev/discord"><img src="https://discordapp.com/api/guilds/699728181841887363/embed.png"></a>

[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

<!--- You found an easter egg! Here's a cookie UwU :totallyrealcookie.png: -->
