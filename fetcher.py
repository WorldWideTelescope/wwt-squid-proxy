#! /usr/bin/env python3
# Copyright 2021 the .NET Foundation
# Licensed under the MIT License

"""
A simple HTTP(S) proxy service for allowing the WWT webclient to work around
CORS restrictions.

I was hoping not to have to deploy custom code for this service, but this
service needs to follow HTTP redirects, which general-purpose HTTP proxies
properly do not do. Fortunately the implementation is fairly simple.

"""

import logging
import tornado.httpclient
import tornado.httputil
import tornado.ioloop
import tornado.web
from urllib.parse import urlparse

from tornado.log import enable_pretty_logging
enable_pretty_logging()

PASSTHROUGH_HEADERS = [
    'Cache-Control',
    'Content-Encoding',
    'Content-Language',
    'Content-Length',
    'Content-Type',
    'Expires',
    'Last-Modified',
    'Pragma',
]

FIXED_HEADERS = [
    ('Access-Control-Allow-Headers', 'Content-Disposition,Content-Encoding,Content-Type'),
    ('Access-Control-Allow-Methods', 'GET'),
    ('Access-Control-Allow-Origin', '*'),
]

class ProxyHandler(tornado.web.RequestHandler):
    async def get(self):
        self.clear()
        self._inner_headers = tornado.httputil.HTTPHeaders()
        self._start_line_data = None

        # if targeturl is unspecified, this will raise an error resulting in
        # an HTTP 400 Bad Request error, which is the right outcome.
        url = self.get_argument('targeturl')

        # http.fetch() handles most of this, but I think it's good to have some
        # explicit validation here.
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            raise tornado.web.HTTPError(400, f'URL {url!r} is not HTTP or HTTPS protocol')
        if not parsed.netloc:
            raise tornado.web.HTTPError(400, f'URL {url!r} is not absolute')

        # We sometimes end up being asked to handle VirtualEarth tiles because
        # their SSL configuration is broken -- we're basically laundering SSL
        # rather than CORS. We'll vouch for this content to keep things running
        # smoothly.

        if parsed.netloc.endswith('tiles.virtualearth.net') and parsed.scheme == 'https':
            # It feels dirty to use this underscored method but apparently it's part
            # of the namedtuple API ...
            url = parsed._replace(scheme='http').geturl()

        http = tornado.httpclient.AsyncHTTPClient()

        # Annoyingly, you need to have a `header_callback` in order to be able
        # to stream data, because you need to process all of the headers before
        # writing data.
        #
        # decompress_respose must be false, because otherwise Tornado might
        # transparently de-gzip for us, in which case we'll return a
        # Content-Length that corresponds to the gzipped content, not the data
        # that we're writing.
        #
        # raise_error = False allows us to properly forward errors such as
        # 404's.
        #
        # follow_redirects = True is the whole reason we're doing this; our
        # fetcher can't return redirects since that breaks the whole CORS
        # proxying scheme. (Well, we could return a redirect to our CORS
        # service, but why bother?)
        try:
            await http.fetch(url,
                header_callback = self.do_header_line,
                streaming_callback = self.do_data_chunk,
                decompress_response = False,
                raise_error = False,
                follow_redirects = True,
            )
        except Exception as e:
            logging.error('error trying to fetch %r: %s', url, e)
            self.set_status(502) # Bad Gateway
            self.set_header('Content-Type', 'text/plain')
            self.write('HTTP/502 Bad Gateway: unable to fetch the requested URL\n')

        self.finish()


    def do_header_line(self, text):
        if self._start_line_data is None:
            self._start_line_data = tornado.httputil.parse_response_start_line(text)
        else:
            self._inner_headers.parse_line(text)


    def do_data_chunk(self, data):
        if self._inner_headers is not None:  # First data chunk?
            self.set_status(self._start_line_data.code)

            for header in PASSTHROUGH_HEADERS:
                v = self._inner_headers.get(header)
                if v is not None:
                    self.set_header(header, v)

            for hn, hv in FIXED_HEADERS:
                self.set_header(hn, hv)

            self._inner_headers = None

        self.write(data)


class OkHandler(tornado.web.RequestHandler):
    async def get(self):
        self.set_status(200)
        self.set_header('Cache-Control', 'no-store')
        self.write('ok\n')


def make_app():
    return tornado.web.Application([
        (r'/webserviceproxy.aspx', ProxyHandler),
        (r'/wwtweb/webserviceproxy.aspx', ProxyHandler),
        (r'/WebServiceProxy.aspx', ProxyHandler),
        (r'/WWTWeb/WebServiceProxy.aspx', ProxyHandler),
        (r'/', OkHandler),
    ])

if __name__ == '__main__':
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
