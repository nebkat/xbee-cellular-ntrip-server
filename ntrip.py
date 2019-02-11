import binascii
import json
import network
import socket
import sys
import time

print("Starting XBee Cellular NTRIP server!")
print("Author: Nebojša Cvetković")
print("Source: https://github.com/nebkat/xbee-cellular-ntrip-server/")

config = open('config.json')
c = json.load(config)
config.close()

cellular = network.Cellular()
timeout = 1

time.sleep(1)

while True:
	if not cellular.isconnected():
		print("Waiting for network.", end='')
		while not cellular.isconnected():
			print(".", end='')
			time.sleep(5)
		print(" connected")

	if timeout > 1:
		print("Waiting for %d seconds before connecting" % timeout)
	time.sleep(timeout)
	timeout *= 2
	if timeout > 60 * 30:
		timeout = 60 * 30

	s = socket.socket()

	print("Connecting to NTRIP caster at %s:%d (NTRIP v%d)" % (c['caster']['host'], c['caster']['port'], c['caster']['version']))
	try:
		s.connect(socket.getaddrinfo(c['caster']['host'], c['caster']['port'])[0][-1])
	except:
		print("Error connecting to mountpoint")
		s.close()
		continue

	print("Mounting on /%s" % (c['mountpoint']))
	if c['caster']['version'] == 2:
		authorization = binascii.b2a_base64(bytes(c['caster']['username'] + ':' + c['caster']['password'], 'utf-8')).decode('ascii')

		s.write(("POST /%s HTTP/1.1\r\n"
				"Host: %s\r\n"
				"Ntrip-Version: Ntrip/2.0\r\n"
				"Authorization: Basic %s\r\n"
				"User-Agent: NTRIP %s/2.0\r\n"
				"Connection: close\r\n"
				"\r\n") %
				(c['mountpoint'], c['caster']['host'], authorization, c['name']))
	else:
		s.write(("SOURCE %s /%s HTTP/1.1\r\n"
				"Source-Agent: NTRIP %s/2.0\r\n"
				"\r\n") %
				(c['caster']['password'], c['mountpoint'], c['name']))

	response = s.readline().decode('utf-8').strip()
	if response.startswith('HTTP/1.1'):
		response_code = response[9:12]
		if response_code == "200":
			print("Successfully connected to mountpoint")

			while s.readline() != b'\r\n':
				pass
		else:
			print("Error connecting to mountpoint:")
			print(response[9:])

			s.close()
			sys.exit()
	elif response == 'OK' or response == 'ICY 200 OK':
		print("Successfully connected to mountpoint")
	else:
		print("Error connecting to mountpoint:")
		print(response)

		s.close()
		sys.exit()

	timeout = 1

	s.write("\r\n")

	keepalive = 0
	try:
		while True:
			stdin_data = sys.stdin.buffer.read(-1)
			if stdin_data:
				s.write(stdin_data)
				keepalive = 0
			else:
				time.sleep_ms(5)
				keepalive += 1
				if keepalive > 2000:
					s.write("\r\n")
					keepalive = 0
	except:
		print("Connection closed by server")

	s.close()