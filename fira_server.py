#!/usr/bin/env python
import httplib
import sys
import urllib
import threading
import json
import hashlib
import hmac
import os
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

secret = os.environ['GITHUB_SECRET']
if secret is None:
	print 'Error: no GITHUB_SECRET declared in environ'
	sys.exit(1)

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

	def abort(self, status):
		self.send_reply(403, 'application/json', '')

	def do_GET(self):
		if self.path == '/':
			with open('fira.html') as f:
				self.send_reply(200, 'text/html', f.read())

		elif self.path == '/github':
			if 'content-length' in self.headers:
				body = self.rfile.read(int(self.headers['content-length']))
				body = json.loads(body)

				header_signature = self.headers.get('X-Hub-Signature')
				if header_signature is None:
					self.abort(403)

				sha_name, signature = header_signature.split('=')
				if sha_name != 'sha1':
					self.abort(501)

				# HMAC requires the key to be bytes, but data is string
				mac = hmac.new(str(secret), msg=request.data, digestmod='sha1')

				# Python prior to 2.7.7 does not have hmac.compare_digest
				if sys.hexversion >= 0x020707F0:
					if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
						self.abort(403)
				else:
					# What compare_digest provides is protection against timing
					# attacks; we can live without this protection for a web-based
					# application
					if not str(mac.hexdigest()) == str(signature):
						self.abort(403)

				# Implement ping
				event = request.headers.get('X-GitHub-Event', 'ping')
				if event == 'ping':
					self.send_reply(200, 'application/json', json.dumps({'msg': 'pong'}))

				else:
					print 'event', event					
					self.send_reply(204)
			else:
				self.abort(501)

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

	def log_message(self, format, *args):
		return

	do_HEAD = do_GET
	do_POST = do_GET
	do_PUT = do_GET
	do_DELETE = do_GET


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

port = int(sys.argv[1]) if len(sys.argv) > 1 else 80
print 'Server started port', port
while True:
	try:
		httpd = ThreadedHTTPServer(('0.0.0.0', port), Handler)
		httpd.serve_forever()
	except KeyboardInterrupt:
		os.killpg(os.getpgrp())
		break
	except:
		pass
