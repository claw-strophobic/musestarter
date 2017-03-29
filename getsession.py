#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell

from lxml import etree
import sys
import argparse as myArg
import gettext
t = gettext.translation('dacapo', "/usr/share/locale/")
t.install()
import subprocess

JACK = '/usr/bin/jack_connect'

argparser = myArg.ArgumentParser(description=_('Liest die Session-Datei von QJackCTL aus und verbindet die Kanäle.'))
argparser.add_argument("-p", "--project", help=_('Projektname'))
argparser.add_argument("-d", "--projectdir", help=_('Projektverzeichnis'))

# -------------------- Main() -----------------------------------------------------------------
class SessionReader(object):

	def runSession(self):
		global argparser
		args = argparser.parse_args()

		xmlFile = None
		project = None
		sessionDir = None

		if args.project:
			project = args.project
		if args.projectdir:
			sessionDir = args.projectdir

		if (project is None) or (sessionDir is None):
			print  >> sys.stderr, "\n\n_('Kein Projektname und/oder kein Projektverzeichnis gegeben!')\n\n "
			exit()

		xmlFile = sessionDir + '/Session/' + project + '.xml'
		print('Verarbeite Datei: {!s}'.format(xmlFile))

		parser = etree.XMLParser(remove_blank_text=True)
		xmltree = etree.parse(xmlFile, parser)
		root = xmltree.getroot()

		for child in root:
			if (child.tag == 'client'):
				self.runClient(child)


	def runClient(self, client):
		global JACK
		# print('client gefunden: {!s}'.format(client.attrib['name']))
		c_name = client.attrib['name']
		for child in client:
			if (child.tag == 'port'):
				# print('\tPort gefunden: Typ: {!s} Name: {!s}'.format(child.attrib['type'], child.attrib['name']))
				c_port = c_name + ':' + child.attrib['name']
				for connection in child.getchildren():
					if (connection.tag == 'connect'):
						# print('\t\tConnect to port: {!s} Client: {!s}'.format(connection.attrib['port'], connection.attrib['client']))
						target = connection.attrib['client'] + ':' + connection.attrib['port']
						# args = [JACK, '"'+c_port+'"', '"'+target+'"']
						args = [JACK, c_port, target]
						p = subprocess.Popen(args)




if __name__ == '__main__':
	if len(sys.argv) < 2:
		print  >> sys.stderr, "\n\nNo Session-File given!\n\n "
		exit()
	s = SessionReader()
	s.runSession()


