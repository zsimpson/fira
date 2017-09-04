#!/usr/bin/env python
import httplib
import sys
import urllib
import threading
import json
import hashlib
import hmac
import os
import base64
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
# import chardet

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
			print 'here1'
			if 'content-length' in self.headers:
				orig_body = self.rfile.read(int(self.headers['content-length']))
				print 'orig_body start'
				print orig_body
				print 'orig_body end'
				body = json.loads(orig_body)

				header_signature = self.headers.get('X-Hub-Signature')
				print 'here2'
				if header_signature is None:
					print 'here3'
					self.abort(403)
					return

				# HMAC requires the key to be bytes, but data is string
				print 'here6', type(bytes(secret).encode('utf-8')), type(bytes(orig_body).encode('utf-8'))
				signature = 'sha1=' + hmac.new(bytes(secret).encode('utf-8'), bytes(orig_body).encode('utf-8'), hashlib.sha1).hexdigest()

				print 'here6.1', signature, header_signature
				if signature == header_signature:
					print 'GOOD!'

				hm = hmac.new(bytes(secret), bytes(orig_body), hashlib.sha1)
				print 'by base64', base64.b64encode(hm.digest())

				# h = hmac.new(os.environ.get('GITHUB_SECRET'), orig_body, hashlib.sha1)
				# print 'using compare digest', hmac.compare_digest(bytes("sha1=" + h.hexdigest()), bytes(header_signature))

				# Implement ping
				print 'here12'
				event = self.headers.get('X-GitHub-Event', 'ping')
				if event == 'ping':
					print 'here13'
					self.send_reply(200, 'application/json', json.dumps({'msg': 'pong'}))
					return

				else:
					print 'event', event					
					self.send_reply(200, 'application/json', '')
					return
			else:
				print 'here14'
				self.abort(501)
				return
			pass

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
		os.killpg(os.getpgrp(), 9)
		break
	except:
		pass
