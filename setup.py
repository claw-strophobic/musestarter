#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.command.install import install
import sys, os
import shutil

print("Setup-Mode: %s" % (sys.argv[1]) )

class jackproject_install(install):
	description="Custom Install Process"
	user_options=install.user_options[:]
	user_options.extend([('localprefix=', None, 'Localization Path if not /usr/local/share/')])

	def initialize_options(self):
		self.localprefix = None
		install.initialize_options(self)

	def finalize_options(self):
		if self.localprefix is None :
			self.localprefix = "/usr/share/locale/"
		install.finalize_options(self)

	def install_translations(self):
		print "copy translations"
		for root, dirs, files in os.walk('./jackproject/locale/'):
			for filename in files:
				basename, file_extension = os.path.splitext(filename)
				if file_extension == ".mo":
					src_file = os.path.join(root, filename)
					man_root = os.path.join(self.localprefix, \
						root.replace('./jackproject/locale/', ''))
					dest_file = os.path.join(man_root, filename)
					if not os.path.exists(man_root):
						os.makedirs(man_root)
					print("copy %s -> %s " % (src_file, dest_file))
					shutil.copy(src_file, dest_file)

	def run(self):
		install.run(self)
		# Custom stuff here
		# distutils.command.install actually has some nice helper methods
		# and interfaces. I strongly suggest reading the docstrings.

		if sys.argv[1] == "install" :
			print "installiere config"
			self.install_translations()
		

setup(
	name="jackProject",
	version="0.9",
	packages=['jackproject'],
	scripts=["addProject.py", "getsession.py", "startJackProject.py", "openProject.py",],

	# Project uses reStructuredText, so ensure that the docutils get
	# installed or upgraded on the target machine
	requires=['argparse (>=1.1)',],

	# metadata for upload to PyPI
	author="Thomas Korell",
	author_email="claw.strophobic@gmx.de",
	description="A jack-project managing tool",
	license="GNU General Public License (v2 or later)",
	keywords="jack MusE sequencer",

	# could also include long_description, download_url, classifiers, etc.
	# cmdclass={'setconfig': my_install},
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: X11 Applications',
		'Intended Audience :: End Users/Desktop',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
		'Operating System :: POSIX',
		'Programming Language :: Python',
		'Topic :: Multimedia :: Sound/Audio',
	],
	cmdclass={"install": jackproject_install},

)

