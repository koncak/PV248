import http.server
import json
import urllib.request
from urllib.error import HTTPError
import socket
import sys

PORT = 9999
UPSTREAM = 'example.com'
TIMEOUT = 1


class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        url = 'http://' + UPSTREAM
        d = {}
        try:
            headers = {x[0]: x[1] for x in self.headers._headers if x[0] not in ('Host')}
            req = urllib.request.Request(url, headers=headers)
            r = urllib.request.urlopen(req, timeout=TIMEOUT)
            data = r.read()
            d = {'code': r.status, 'headers': {k: v for k, v in r.headers._headers}}

            try:
                d['json'] = json.loads(data.decode('utf8').replace("'", '"'))
            except ValueError:
                d['content'] = data.decode('utf8')

        except socket.timeout:
            d = {'code': "timeout"}
        except HTTPError as error:
            d = {'code': error.code}
        except Exception as ex:
            d = {'code': ex.__str__()}
        finally:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = json.dumps(d)
            self.wfile.write(message.encode())

    def do_POST(self):

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        d = {}
        try:
            my_json = json.loads(post_data.decode('utf8').replace("'", '"'))
            url = my_json['url']
            headers = my_json['headers'] if 'headers' in my_json.keys() else {}
            timeout = int(my_json['timeout']) if 'timeout' in my_json.keys() else TIMEOUT
            request_type = my_json['type'] if 'type' in my_json.keys() else 'GET'
            content = None
            if request_type == 'POST':
                content = my_json['content'].encode('utf8')

            req = urllib.request.Request(url, headers=headers, data=content)
            r = urllib.request.urlopen(req, timeout=timeout)
            data = r.read()

            d = {'code': r.status, 'headers': {k: v for k, v in r.headers._headers}}
            try:
                d['json'] = json.loads(data.decode('utf8').replace("'", '"'))
            except ValueError:
                d['content'] = data.decode('utf8')

        except (ValueError, KeyError):
            d = {'code': "invalid json"}
        except socket.timeout:
            d = {'code': "timeout"}
        except HTTPError as error:
            d = {'code': error.code}
        except Exception as ex:
            d = {'code': ex.__str__()}
        finally:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = json.dumps(d)
            self.wfile.write(message.encode())


if len(sys.argv) < 3:
    exit("Too less arguments calling script")

PORT = int(sys.argv[1])
UPSTREAM = sys.argv[2]

server_address = ('127.0.0.1', PORT)
try:
    server = http.server.HTTPServer(server_address, MyHandler)
    print('Started http server')
    server.serve_forever()
except KeyboardInterrupt:
    print('^C received, shutting down server')
    server.socket.close()