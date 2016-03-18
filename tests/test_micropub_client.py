# coding=utf-8
from __future__ import unicode_literals, print_function

import collections
import json
import os
import unittest
import requests

import flask_micropub

try:
    from unittest import mock
except:
    import mock


class MicropubClientTest(unittest.TestCase):

    def setUp(self):
        self.client = flask_micropub.MicropubClient()

    @mock.patch('requests.get')
    def test_discover_endpoints_from_http_header(self, get_method):
        r = requests.Response()
        r.headers['Link'] = '<http://foo.bar/auth>;rel=authorization_endpoint, <http://baz.bux/token>;rel=token_endpoint, <http://do.re/micropub>;rel=micropub'
        r.status_code = 200
        get_method.return_value = r
        result = self.client._discover_endpoints('http://foo.bar/')
        get_method.assert_called_once_with('http://foo.bar/')
        self.assertEqual(('http://foo.bar/auth', 'http://baz.bux/token', 'http://do.re/micropub'), result)

    @mock.patch('requests.get')
    def test_discover_endpoints_from_html(self, get_method):
        r = requests.Response()
        r._content = """
<!DOCTYPE html>
<html>
  <head>
    <link href="http://foo.bar/auth" rel="authorization_endpoint">
    <link href="http://baz.bux/token" rel="token_endpoint">
    <link href="http://do.re/micropub" rel="micropub">
  </head>
  <body>
  </body>
</html>
""".encode('utf-8')
        r.status_code = 200
        get_method.return_value = r
        result = self.client._discover_endpoints('http://foo.bar/')
        get_method.assert_called_once_with('http://foo.bar/')
        self.assertEqual(('http://foo.bar/auth', 'http://baz.bux/token', 'http://do.re/micropub'), result)
