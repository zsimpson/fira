#!/usr/bin/env python
import httplib
import sys
import urllib
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler


class Handler(SimpleHTTPRequestHandler):
	protocol_version = 'HTTP/1.0'

	def send_reply(self, status, content_type, body):
		self.send_response(status)
		self.send_header('content-type', content_type)
		self.send_header('content-length', len(body))
		self.send_header('access-control-allow-origin', '*')
		self.send_header('access-control-allow-headers', 'content-type')
		self.end_headers()
		self.wfile.write(body)

	def do_GET(self):
		if self.path == '/':
			with open('fira.html') as f:
				self.send_reply(200, 'text/html', f.read())

		else:
			body = ''
			if 'content-length' in self.headers:
				body = self.rfile.read(int(self.headers['content-length']))

			jira_conn = httplib.HTTPSConnection('mousera.atlassian.net', 443)
			headers = {
				'content-type': self.headers['content-type'],
				'content-length': str(len(body)),
				'cookie': urllib.unquote(self.headers['Cookie'].replace('jiracookie=', '')),
			}
			jira_conn.request(self.command, self.path, body, headers)
			jira_resp = jira_conn.getresponse()
			jira_headers = dict(jira_resp.getheaders())
			jira_reply = jira_resp.read()
			self.send_reply(jira_resp.status, jira_headers['content-type'], jira_reply)

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
