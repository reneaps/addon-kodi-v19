import xbmc
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse
import requests
import threading


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'

    def do_GET(self):
        p = urlparse(self.path)
        q = dict(parse_qsl(p.query))

        if 'u' not in q:
            self.send_error(404)
            return

        u = q['u']
        url = u[:-3] if u.endswith('-no') else u
        print(url)
        res = requests.get(url)
        ret = res.content[8:]
        self.send_header('Content-Length', len(ret))
        self.send_header('Content-Type', 'application/vnd.apple.mpegurl')
        self.end_headers()
        self.wfile.write(ret)


if __name__ == '__main__':
    server_address = ('127.0.0.1', 8964)
    httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)
    print('http server is running')
    # httpd.serve_forever()

    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.start()

    monitor = xbmc.Monitor()

    while not monitor.waitForAbort(3):
        pass

    httpd.shutdown()
    server_thread.join()