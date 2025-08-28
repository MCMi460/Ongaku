from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from time import sleep
from subprocess import call, run

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


class Serv(BaseHTTPRequestHandler):

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        content_len = int(self.headers.get("Content-Length"))
        post_body = self.rfile.read(content_len)
        print(post_body)


if __name__ == "__main__":
    httpd = HTTPServer(("", 18841), Serv)
    Thread(target=httpd.serve_forever, daemon=True).start()

    sleep(1)

    call(["shortcuts", "run", desktopShortcut])
