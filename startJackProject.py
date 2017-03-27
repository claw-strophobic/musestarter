#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell

import sys, os
import argparse as myArg
import gettext
import subprocess
import time

t = gettext.translation('dacapo', "/usr/share/locale/")
t.install()
_ = t.ugettext

argparser = myArg.ArgumentParser(description=_(u'Liest die Session-Datei von QJackCTL aus und verbindet die Kanäle.'))
argparser.add_argument("-p", "--project", help=_('Projektname'))
argparser.add_argument("-d", "--projectdir", help=_('Projektverzeichnis'))
argparser.add_argument("--muse", type=int, help=_('starte MusE 0/1'), choices=[0, 1], default=0)
argparser.add_argument("--hydrogen", type=int, help=_('starte hydrogen 0/1'), choices=[0, 1], default=0)
argparser.add_argument("--yoshimi", type=int, help=_('starte yoshimi 0/1'), choices=[0, 1], default=0)
argparser.add_argument("--aeolus", type=int, help=_('starte aeolus 0/1'), choices=[0, 1], default=0)
argparser.add_argument("--seq24", type=int, help=_('starte seq24 0/1'), choices=[0, 1], default=0)
argparser.add_argument("--lingot", type=int, help=_('starte lingot 0/1'), choices=[0, 1], default=0)
argparser.add_argument("--libreoffice", type=int, help=_('starte libreoffice 0/1'), choices=[0, 1], default=0)
argparser.add_argument("--calfjackhost", type=int, help=_('starte Calf-Effekte 0/1'), choices=[0, 1], default=0)

class StartJackProject(object):
	START_OPT = {
		"muse": "/usr/bin/muse;-J;%projectdir%/%project%.med",
		"hydrogen": "/usr/bin/hydrogen;--song=%projectdir%/Hydrogen/drums.h2song",
		"yoshimi": "/usr/bin/yoshimi;--state=%projectdir%/Yoshimi/yoshimi.state",
		"aeolus": "/usr/bin/aeolus",
		"seq24": "/usr/bin/seq24;%projectdir%/Seq24/seq.midi",
		"lingot": "/usr/bin/lingot",
		"libreoffice": "/usr/bin/libreoffice;--nologo;--writer;%projectdir%/Text/%project%.odt",
	}
	GET_SESSION = "/usr/local/bin/getsession.py;--project=%project%;--projectdir=%projectdir%"

	def runSession(self):
		global argparser
		myargs = argparser.parse_args()

		project = None
		sessionDir = None

		if myargs.project:
			project = myargs.project
		if myargs.projectdir:
			sessionDir = myargs.projectdir

		if (project is None) or (sessionDir is None):
			print  >> sys.stderr, "\n\n"+_(u'Kein Projektname und/oder kein Projektverzeichnis gegeben!')+"\n\n "
			exit()

		# Starting the elemtary Jack-Programs
		if (self.get_pid('qjackctl') == 0):
			p = subprocess.Popen('/usr/bin/qjackctl')
		if (self.get_pid('a2jmidi_bridge') == 0):
			p = subprocess.Popen('/usr/bin/a2jmidi_bridge')
		if (self.get_pid('calfjackhost') == 0) and (myargs.calfjackhost == 1):
			for filename in os.listdir(sessionDir+"/Calf-Effekte/"):
				text = '/usr/bin/calfjackhost;--client;calf_%name%;'.replace("%name%", os.path.basename(filename)) + \
					'--load;%name%'.replace("%name%", sessionDir+"/Calf-Effekte/"+filename)
				print('Starte: {!s}'.format(text))
				args = text.split(';')
				p = subprocess.Popen(args)

		# Wait for everything is ready
		time.sleep(2)

		# Now start the optional programs
		for pgm in self.START_OPT:
			attr = 0
			if hasattr(myargs, pgm):
				attr = getattr(myargs, pgm)
			if (attr == 0):
				print('Programm: {!s} soll nicht gestartet werden'.format(pgm))
				continue
			if (self.get_pid(pgm) == 0):
				text = self.START_OPT[pgm].replace('%projectdir%', sessionDir)
				text = text.replace('%project%', project)
				print('Starte: {!s}'.format(text))
				args = text.split(';')
				p = subprocess.Popen(args)

		# Wait again for everything is ready
		time.sleep(4)
		text = self.GET_SESSION.replace('%projectdir%', sessionDir)
		text = text.replace('%project%', project)
		print('\n\n\n\n\nStarte: {!s}'.format(text))
		args = text.split(';')
		p = subprocess.Popen(args)


	def get_pid(self, name):
		try:
			return int(subprocess.check_output(["pidof", "-s", name]))
		except:
			return 0

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print  >> sys.stderr, "\n\nNo Session-File given!\n\n "
		exit()
	s = StartJackProject()
	s.runSession()


