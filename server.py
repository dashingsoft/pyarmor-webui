#! /usr/bin/env python
import argparse
import logging
import json
import os
import posixpath
import shutil
import sys

try:
    from urllib import unquote
except Exception:
    from urllib.parse import unquote
try:
    from BaseHTTPServer import BaseHTTPRequestHandler
except ImportError:
    from http.server import BaseHTTPRequestHandler
try:
    import SocketServer as socketserver
except ImportError:
    import socketserver

try:
    from .handler import RootHandler
except Exception:
    from handler import RootHandler

__version__ = '1.4.0'

__config__ = {
    'version': __version__,
    'wwwroot': os.path.join(os.path.dirname(__file__), 'static'),
    'basepath': os.path.dirname(__file__),
    'homepath': os.path.expanduser(os.path.join('~', '.pyarmor')),
}


def _fix_up_win_console_freeze():
    import win32api
    import ctypes
    try:
        win32api.SetConsoleTitle("Pyarmor Webui")
        # Disable quick edit in CMD, as it can freeze the application
        handle = win32api.GetStdHandle(-10)
        if handle != -1 and handle is not None:
            ctypes.windll.kernel32.SetConsoleMode(handle, 128)
    except Exception:
        pass


class HelperHandler(BaseHTTPRequestHandler):

    server_version = "HelperHTTP/" + __version__
    root_handler = RootHandler(__config__)

    def do_OPTIONS(self):
        """Serve a OPTIONS request."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS,PUT")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_POST(self):
        """Serve a POST request."""
        t = self.headers.get('Content-Type')
        self.log_message("Content-Type: %s", t)

        n = int(self.headers.get('Content-Length', 0))
        if n == 0:
            args = {}
        else:
            args = json.loads(self.rfile.read(n).decode())
        self.log_message("Post-Data: %s", args)

        result = dict(err=0)
        try:
            result['data'] = self.root_handler.dispatch(self.path[1:], args)
        except Exception as e:
            logging.exception("Failed to handle request")
            result['err'] = 1
            result['data'] = str(e)

        if result:
            data = json.dumps(result).encode()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS,PUT")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Last-Modified", self.date_time_string())
            self.end_headers()
            self.wfile.write(data)

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path[1:])
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                self.send_error(404, "File not found")
                return None

        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = os.path.join(__config__['wwwroot'], unquote(path))
        return posixpath.normpath(path)

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']
    extensions_map = {
        '': 'application/octet-stream',
        '.svg': 'image/svg+xml',
        '.css': 'text/css',
        '.html': 'text/html',
        '.js': 'application/x-javascript',
        }


def main(argv=None):
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    parser = argparse.ArgumentParser(
        prog='pyarmor-webui',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('-v', '--version', action='version',
                        version=__version__)
    parser.add_argument('-p', '--port', type=int, default=9096,
                        help='Serve port, default is 9096')
    parser.add_argument('-H', '--host', default='localhost',
                        help='Bind host, default is localhost')
    parser.add_argument('-n', '--no-browser', action='store_true',
                        help='Do not open web browser')
    parser.add_argument('-i', '--index', default='',
                        help='Index page, default is index.html')
    parser.add_argument('--data-path',
                        help='Where to save projects, default is ~/.pyarmor')
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    if args.data_path:
        __config__['homepath'] = args.data_path
    logging.info("Data path: %s", __config__['homepath'])

    if sys.platform == 'win32':
        _fix_up_win_console_freeze()

    server = socketserver.TCPServer((args.host, args.port), HelperHandler)
    logging.info("Serving HTTP on %s port %s ...", *server.server_address)

    if not args.no_browser:
        from webbrowser import open_new_tab
        open_new_tab("http://%s:%d/%s" % (args.host, args.port, args.index))
    server.serve_forever()


if __name__ == '__main__':
    main()
