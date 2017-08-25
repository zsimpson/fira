#!/usr/bin/env python
import httplib
import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler


with open('jira_cookie.txt') as f:
    cookie = f.read()

class Handler(SimpleHTTPRequestHandler):
	protocol_version = 'HTTP/1.0'

	def do_GET(self):
		body = ''
		if 'content-length' in self.headers:
			body = self.rfile.read(int(self.headers['content-length']))

		jira_conn = httplib.HTTPSConnection('mousera.atlassian.net', 443)
		headers = {
			'content-type': self.headers['content-type'],
			'content-length': str(len(body)),
			'cookie': cookie,
		}
		jira_conn.request(self.command, self.path, body, headers)
		jira_resp = jira_conn.getresponse()
		jira_headers = dict(jira_resp.getheaders())
		jira_reply = jira_resp.read()

		self.send_response(jira_resp.status)
		self.send_header('content-type', jira_headers['content-type'])
		self.send_header('content-length', len(jira_reply))
		self.send_header('access-control-allow-origin', '*')
		self.send_header('access-control-allow-headers', 'content-type')
		self.end_headers()
		self.wfile.write(jira_reply)

	def do_OPTIONS(self):
		self.send_response(200)
		self.send_header('access-control-allow-origin', '*')
		self.send_header('access-control-allow-headers', 'content-type')
		self.send_header('access-control-allow-methods', 'GET, POST, PUT, DELETE, OPTIONS')
		self.end_headers()
		self.wfile.write('')

	do_HEAD = do_GET
	do_POST = do_GET
	do_PUT = do_GET
	do_DELETE = do_GET


httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 8080), Handler)
httpd.serve_forever()
