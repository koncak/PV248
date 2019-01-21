import os
import asyncio
import sys
from aiohttp import web
from aiohttp import streamer
import mimetypes

import re

regex = r"\/(.+?)(\..+?)(\/.*)?$"
DIR = '10/static'
PORT = 15555


def get_file_name(path):
    m = re.search(regex, path)
    if m:
        file_name = m.group(1)
        file_extension = m.group(2)
        path_info = m.group(3) if m.group(3) else ""

    return file_name, file_extension, path_info


async def run_cgi(file_path, ipt=None):
    proc = await asyncio.create_subprocess_exec(
        file_path,
        stdout=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT)

    if ipt:
        proc.stdin.write(ipt)
        await proc.stdin.drain()

    stdout, _ = await proc.communicate()
    return stdout.decode()


def make_cgi_env(request, file_path, path_info):
    """Set CGI environment variables"""

    env = {}
    env['SERVER_SOFTWARE'] = "09"
    env['SERVER_NAME'] = "aiohttp"
    env['GATEWAY_INTERFACE'] = 'CGI/1.1'
    env['DOCUMENT_ROOT'] = DIR
    env['SERVER_PROTOCOL'] = "HTTP/1.1"
    env['SERVER_PORT'] = str(PORT)

    env['REQUEST_METHOD'] = request.method
    env['REQUEST_URI'] = str(request.raw_path)
    env['PATH_TRANSLATED'] = DIR + path_info
    env['REMOTE_HOST'] = request.host
    env['SCRIPT_NAME'] = file_path
    env['PATH_INFO'] = path_info
    env['QUERY_STRING'] = request.query_string
    env['CONTENT_LENGTH'] = str(request.content_length)
    env['CONTENT_TYPE'] = str(request.content_type)
    for k in request.headers:
        env['HTTP_%s' % k.upper()] = request.headers[k]
    os.environ.update(env)


async def post_handle(request):
    file_name, file_extension, path_info = get_file_name(request.path)
    file_path = os.path.join(DIR, (file_name + file_extension))
    if not os.path.exists(file_path):
        return web.Response(
            body='File <{file_path}> does not exist'.format(file_path=file_path),
            status=404
        )

    data = await request.read()

    if file_extension == '.cgi':
        make_cgi_env(request, file_path, path_info)
        result = await run_cgi(file_path, data)
        lines = result.splitlines()
        headers = {}
        index = 0
        for idx, line in enumerate(lines):
            if not line:
                index = idx
                break

            parts = line.split(':')
            headers[parts[0]] = parts[1].strip()

        return web.Response(text='\n'.join(lines[index + 1:]), headers=headers)

    return web.Response(
        body='File <{file_path}> is not valid for script running'.format(file_path=file_path),
        status=503
    )


async def get_handle(request):
    file_name, file_extension, path_info = get_file_name(request.path)
    file_path = os.path.join(DIR, (file_name + file_extension))
    if not os.path.exists(file_path):
        return web.Response(
            body='File <{file_path}> does not exist'.format(file_path=file_path),
            status=404
        )

    if file_extension == '.cgi':
        make_cgi_env(request, file_path, path_info)
        result = await run_cgi(file_path)
        lines = result.splitlines()
        headers = {}
        index = 0
        for idx, line in enumerate(lines):
            if not line:
                index = idx
                break

            parts = line.split(':')
            headers[parts[0]] = parts[1].strip()

        return web.Response(text='\n'.join(lines[index + 1:]), headers=headers)

    cont_type = mimetypes.guess_type(file_path)
    headers = {"Content-disposition": "attachment; filename={file_path}".format(file_path=file_path)}
    if cont_type:
        headers['Content-Type'] = cont_type[0]

    return web.Response(
        body=file_sender(file_path=file_path),
        headers=headers
    )


@streamer
async def file_sender(writer, file_path=None):
    """
    This function will read large file chunk by chunk and send it through HTTP
    without reading them into memory
    """
    with open(file_path, 'rb') as f:
        chunk = f.read(2 ** 16)
        while chunk:
            await writer.write(chunk)
            chunk = f.read(2 ** 16)


if len(sys.argv) < 3:
    exit("Too less arguments calling script")

PORT = int(sys.argv[1])
DIR = sys.argv[2]

if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

app = web.Application()
app.add_routes([web.get('/{tail:.*}', get_handle),
                web.post('/{tail:.*}', post_handle)])

