#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2017 Thomas Korell
import ConfigParser, os
import gi
import shutil, errno
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import gettext
t = gettext.translation('jackproject', "/usr/share/locale/")
t.install()
_ = t.ugettext

CONFIGPATH = os.path.expanduser('~/.config/MusEStarter')
if not os.path.exists(CONFIGPATH):
	os.makedirs(CONFIGPATH)
CONFIG = os.path.expanduser(CONFIGPATH + '/musestarter.cfg')
PROJECT_EXTENSION = ".med"
TEXT_EXTENSION = ".odt"

class MyParser(ConfigParser.ConfigParser):

	def as_dict(self):
		d = dict(self._sections)
		for k in d:
			d[k] = dict(self._defaults, **d[k])
			d[k].pop('__name__', None)
		return d


class CopyTemplate(Gtk.Window):

	def __init__(self):
		Gtk.Window.__init__(self, title=_("Copy MusE-Project"))
		self.set_border_width(10)
		self.vbox = Gtk.VBox(spacing=10)
		self.grid = Gtk.Grid()
		self.grid.set_column_homogeneous(False)
		self.grid.set_column_spacing(10)
		self.grid.set_row_spacing(10)

		self.config = MyParser()
		self.config.read(CONFIG)
		self.projects = {}
		if (self.config.has_section('projects')):
			self.projects = self.config.as_dict()['projects']

		# Build the project-scan-row
		self.buildHeaderBox()

		self.buildProjectSelectionBox()

		# Build the row for the new project
		self.buildAddProjectBox()

		# make some settings
		if (self.config.has_section('global')):
			self.projectPath.set_text(self.config.get('global', 'projectpath', ""))
			set_combo_active_value(self.comboProject, self.config.get('global', 'lastproject', ""))

		# Build the starter-button
		self.apply_button = Gtk.Button(_("Copy"))
		self.apply_button.set_sensitive(True)
		self.apply_button.connect('clicked', self.on_apply)
		self.apply_button.set_tooltip_text(_("Click here copy the selected project."))
		self.apply_button.set_size_request(100, 30);
		hbox = Gtk.Box(spacing=10)
		hbox.pack_end(self.apply_button, False, False, 0)

		self.vbox.add(self.grid)
		self.vbox.add(hbox)
		self.add(self.vbox)
		return

	def buildAddProjectBox(self):
		self.labelAddProject = Gtk.Label(_("New Project:"), xalign=0)
		self.grid.attach_next_to(self.labelAddProject, self.labelProject, Gtk.PositionType.BOTTOM, 1, 1)
		self.addProject = Gtk.Entry()
		self.addProject.set_editable(True)
		self.grid.attach_next_to(self.addProject, self.labelAddProject, Gtk.PositionType.RIGHT, 1, 1)
		return

	def buildProjectSelectionBox(self):
		self.labelProject = Gtk.Label(_("Project:"), xalign=0)
		self.grid.attach_next_to(self.labelProject, self.labelPath, Gtk.PositionType.BOTTOM, 1, 1)
		self.comboProject = get_simple_combo(self.projects)
		self.comboProject.set_tooltip_text(_("Select a project here."))
		self.grid.attach_next_to(self.comboProject, self.labelProject, Gtk.PositionType.RIGHT, 1, 1)
		self.comboProject.connect("changed", self.on_comboProject_changed)
		return

	def buildHeaderBox(self):
		self.labelPath = Gtk.Label(_("Project-path:"), xalign=0)
		self.grid.add(self.labelPath)
		self.projectPath = Gtk.Entry()
		self.projectPath.set_editable(False)
		self.grid.attach_next_to(self.projectPath, self.labelPath, Gtk.PositionType.RIGHT, 1, 1)
		# Build the open-folder-button
		self.open_button = Gtk.Button(_("Open"))
		self.open_button.set_sensitive(True)
		self.open_button.connect('clicked', self.on_open_folder)
		self.open_button.set_tooltip_text(_("Click here to open the project-directory."))
		self.open_button.set_size_request(30, 30);
		self.grid.attach_next_to(self.open_button, self.projectPath, Gtk.PositionType.RIGHT, 1, 1)
		# Build the scan-button
		self.scan_button = Gtk.Button(_("Scan"))
		self.scan_button.set_sensitive(True)
		self.scan_button.connect('clicked', self.on_scan)
		self.scan_button.set_tooltip_text(_("Click here to scan the project-directory for projects."))
		self.scan_button.set_size_request(100, 30);
		self.grid.attach_next_to(self.scan_button, self.open_button, Gtk.PositionType.RIGHT, 1, 1)
		return


	def on_comboProject_changed(self, obj):
		currentProject = get_combo_active_value(self.comboProject)
		if (not currentProject == ""):
			if (self.config.has_section(currentProject)):
				pass

		return

	def on_scan(self, obj):
		self.projects = {}
		for root, dirs, files in os.walk(self.projectPath.get_text()):
			for file in files:
				if file.endswith(PROJECT_EXTENSION):
					fullpath = os.path.join(root, file)
					projectname = os.path.splitext(os.path.basename(fullpath))[0]
					self.projects[projectname] = fullpath

		type_store = self.comboProject.get_model()
		type_store.clear()
		type_store.append(('', ''))
		for k in self.projects.iterkeys():
			print k, self.projects[k]
			type_store.append((self.projects[k], k))
		cmb = Gtk.ComboBox.new_with_model(type_store)
		renderer = Gtk.CellRendererText()
		cmb.pack_start(renderer, True)
		cmb.add_attribute(renderer, 'text', 1)
		cmb.set_entry_text_column(1)

		return

	def checkInput(self):
		rtnValue = True
		msgLines = ""
		projectDir = self.projectPath.get_text()
		newProjectName = self.addProject.get_text()
		newProject = os.path.join(projectDir, newProjectName)
		oldProject = get_combo_active_value(self.comboProject)
		print oldProject
		if not projectDir or projectDir.strip() == "":
			rtnValue = False
			msgLines = _("No project-path given")
		elif not os.path.isdir(projectDir):
			rtnValue = False
			msgLines = _("Project-path {0} not found.").format(oldProject.decode('utf-8'))
		elif not os.path.isfile(oldProject):
			rtnValue = False
			msgLines = _("Source {0} not found.").format(oldProject.decode('utf-8'))
		elif not newProjectName or newProjectName.strip() == "":
			rtnValue = False
			msgLines = _("No name for the new project given")
		elif os.path.isdir(newProject) or os.path.isfile(newProject):
			rtnValue = False
			msgLines = _("There is already a Object called {0}").format(newProject.decode('utf-8'))
		if not rtnValue:
			dlg = Gtk.MessageDialog(self,
				type=Gtk.MessageType.ERROR,
				buttons=Gtk.ButtonsType.OK,
				message_format=msgLines
			)
			dlg.run()
			dlg.destroy()

		return rtnValue

	def copyAnything(self, src, dst):
		try:
			shutil.copytree(src, dst)
		except OSError as exc: # python >2.5
			if exc.errno == errno.ENOTDIR:
				shutil.copy(src, dst)
			else: raise

	def renameSomeFiles(self):
		projectDir = self.projectPath.get_text()
		newProjectName = self.addProject.get_text()
		newProject = os.path.join(projectDir, newProjectName)
		oldProjectName = get_combo_active_key(self.comboProject)
		try:
			oldMuseFile = os.path.join(newProject, oldProjectName+PROJECT_EXTENSION)
			newMuseFile = os.path.join(newProject, newProjectName+PROJECT_EXTENSION)
			print "Rename: ", oldMuseFile, newMuseFile
			os.rename(oldMuseFile, newMuseFile)
		except:
			raise
		# "libreoffice": "/usr/bin/libreoffice;--nologo;--writer;%projectdir%/Text/%project%.odt",
		try:
			oldTextFile = os.path.join(newProject, "Text", oldProjectName+TEXT_EXTENSION)
			newTextFile = os.path.join(newProject, "Text", newProjectName+TEXT_EXTENSION)
			if os.path.isfile(oldTextFile):
				print "Rename: ", oldTextFile, newTextFile
				os.rename(oldTextFile, newTextFile)
			else:
				print "creating: ", newTextFile
				if not os.path.isdir(os.path.dirname(newTextFile)):
					os.mkdir(os.path.dirname(newTextFile))
				touch(newTextFile)
		except:
			raise

	def on_apply(self, obj):
		if not self.checkInput():
			return False

		if (not self.config.has_section('global')):
			# Create non-existent section
			self.config.add_section('global')
		self.config.set('global', 'projectpath', self.projectPath.get_text())

		if (not self.config.has_section('projects')):
			self.config.add_section('projects')
		for k in self.projects.iterkeys():
			self.config.set('projects', k, self.projects[k])

		projectDir = self.projectPath.get_text()
		newProjectName = self.addProject.get_text()
		newProject = os.path.join(projectDir, newProjectName)

		oldProject = os.path.dirname(get_combo_active_value(self.comboProject))
		combo_iter = self.comboProject.get_active_iter()
		print "Old: ", oldProject
		print "New: ", newProject
		try:
			self.copyAnything(oldProject, newProject)
			self.renameSomeFiles()
			self.config.set('projects', newProjectName, os.path.join(newProject, newProjectName+PROJECT_EXTENSION))
		except:
			raise

		with open(CONFIG, 'wb') as configfile:
			self.config.write(configfile)

		Gtk.main_quit()
		return

	def on_open_folder(self, widget):
		dialog = Gtk.FileChooserDialog(_("Open Project-Directory"),
                                      self,
                                      Gtk.FileChooserAction.SELECT_FOLDER,
                                     (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
										Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
		response = dialog.run()
		if response == Gtk.ResponseType.ACCEPT:
			self.projectPath.set_text(dialog.get_filename())

		dialog.destroy()
		return

def get_simple_combo(keyValue):
	## Create ComboBox
	type_store = Gtk.ListStore(str, str)
	type_store.append(('', ''))
	for k in keyValue.iterkeys():
		print k, keyValue[k]
		type_store.append((keyValue[k], k))
	cmb = Gtk.ComboBox.new_with_model(type_store)
	renderer = Gtk.CellRendererText()
	cmb.pack_start(renderer, True)
	cmb.add_attribute(renderer, 'text', 1)
	cmb.set_entry_text_column(1)
	return cmb

def set_combo_active_value(combo, value):
	model = combo.get_model()
	combo.set_active(0)
	i = 0
	if value is not None:
		for row in model:
			if row[0] == value:
				combo.set_active(i)
				break
			i += 1

def get_combo_active_value(combo):
	ret_val = ''
	model = combo.get_model()
	combo_iter = combo.get_active_iter()
	if combo_iter is not None:
		ret_val = model.get_value(combo_iter, 0)
	return ret_val

def get_combo_active_key(combo):
	ret_val = ''
	model = combo.get_model()
	combo_iter = combo.get_active_iter()
	if combo_iter is not None:
		##ret_val = model[combo_iter][1]
		ret_val = model.get_value(combo_iter, 1)
	return ret_val

def touch(path):
	with open(path, 'a'):
		os.utime(path, None)

win = CopyTemplate()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
