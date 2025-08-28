from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from time import sleep


class Serv(BaseHTTPRequestHandler):

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        content_len = int(self.headers.get("Content-Length"))
        post_body = self.rfile.read(content_len)
        print(post_body)


httpd = HTTPServer(("", 18841), Serv)
Thread(target=httpd.serve_forever, daemon=True).start()

sleep(1)

from subprocess import call, run
from webbrowser import open as open_url

desktop = "OngakuDesktop"
mobile = "OngakuPhone"
result = run(["shortcuts", "list"], capture_output=True, text=True)
if not desktop in result.stdout:
    open_url("https://www.icloud.com/shortcuts/8095149f89be46819cd9f6701ed68b7f")
if not mobile in result.stdout:
    open_url("https://www.icloud.com/shortcuts/5820601243994a039bd40960f5c9f9d8")
call(["shortcuts", "run", desktop])
