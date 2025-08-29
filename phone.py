from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from time import sleep
from subprocess import call, run
from json import loads

shortcutVer = 1
desktopUrl = "https://www.icloud.com/shortcuts/7a60615dac214ab1a9f17356cfad087c"
mobileUrl = "https://www.icloud.com/shortcuts/d9ec70d861674c7fb6287436e6b4551c"
desktopShortcut = "OngakuDesktop"
mobileShortcut = "OngakuPhone"


def shortcut_exists(shortcut_name: str) -> bool:
    result = run(["shortcuts", "list"], capture_output=True, text=True)
    return shortcut_name in result.stdout


def await_shortcut_addition(sender, shortcut_name: str, airdropButton) -> None:
    while not shortcut_exists(shortcut_name):
        sleep(1)
    disable_button(sender)
    if shortcut_exists(mobileShortcut) and shortcut_exists(desktopShortcut):
        airdropButton.setEnabled_(True)


def disable_button(button):
    button.setTitle_("✓ Shortcut Added")
    button.setEnabled_(False)


app_callback = None


class Server(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        content_len = int(self.headers.get("Content-Length"))
        post_body = loads(self.rfile.read(content_len).decode("utf-8"))
        if app_callback:
            app_callback.updateMobile(post_body)
        else:
            print(post_body)


httpd = HTTPServer(("", 18841), Server)
server = Thread(target=httpd.serve_forever, daemon=True)


def start_server(callback):
    global app_callback
    app_callback = callback
    if not server.is_alive():
        server.start()
    call(["shortcuts", "run", desktopShortcut])


if __name__ == "__main__":
    start_server(None)
