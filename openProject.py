#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2017 Thomas Korell
import ConfigParser, os, subprocess
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import gettext
t = gettext.translation('jackproject', "/usr/share/locale/")
t.install()
_ = t.ugettext
import jackproject

CONFIGPATH = os.path.expanduser('~/.config/MusEStarter')
if not os.path.exists(CONFIGPATH):
	os.makedirs(CONFIGPATH)
CONFIG = os.path.expanduser(CONFIGPATH + '/musestarter.cfg')
PROJECT_EXTENSION = ".med"
START_PROJECT_PGM = "python;/usr/local/bin/startJackProject.py;--projectdir=%projectdir%;--project=%project%"

class MySwitch(Gtk.Switch):
	pgm = ""

class MyParser(ConfigParser.ConfigParser):

	def as_dict(self):
		d = dict(self._sections)
		for k in d:
			d[k] = dict(self._defaults, **d[k])
			d[k].pop('__name__', None)
		return d


class Configurator(Gtk.Window):

	START_OPT = jackproject.START_OPT

	def __init__(self):
		Gtk.Window.__init__(self, title=_("MusE-Project-Starter"))
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
		hHeaderbox = self.buildHeaderBox()

		self.hProjectSelectionBox = self.buildProjectSelectionBox()
		# Build the Grid with the starter-switches
		self.buildPgmSwitchGrid()

		# make some settings
		if (self.config.has_section('global')):
			self.projectPath.set_text(self.config.get('global', 'projectpath', ""))
			set_combo_active_value(self.comboProject, self.config.get('global', 'lastproject', ""))

		# Build the starter-button
		self.apply_button = Gtk.Button(_("Apply"))
		self.apply_button.set_sensitive(True)
		self.apply_button.connect('clicked', self.on_apply)
		self.apply_button.set_tooltip_text(_("Click here to see a preview of this field."))
		self.apply_button.set_size_request(100, 30);
		hbox = Gtk.Box(spacing=10)
		hbox.pack_end(self.apply_button, False, False, 0)

		self.vbox.add(hHeaderbox)
		self.vbox.add(self.hProjectSelectionBox)
		self.vbox.add(self.grid)
		self.vbox.add(hbox)
		self.add(self.vbox)
		return

	def buildProjectSelectionBox(self):
		hProjectSelectionBox = Gtk.Box(spacing=10)
		labelPath = Gtk.Label(_("Project:"), xalign=0)
		hProjectSelectionBox.pack_start(labelPath, False, False, 0)
		self.comboProject = get_simple_combo(self.projects)
		self.comboProject.set_tooltip_text(_("Select a project here."))
		hProjectSelectionBox.pack_start(self.comboProject, False, False, 0)
		self.comboProject.connect("changed", self.on_comboProject_changed)
		return hProjectSelectionBox

	def buildHeaderBox(self):
		hHeaderbox = Gtk.Box(spacing=10)
		labelPath = Gtk.Label(_("Project-path:"), xalign=0)
		hHeaderbox.pack_start(labelPath, False, False, 0)
		self.projectPath = Gtk.Entry()
		self.projectPath.set_editable(False)
		hHeaderbox.pack_start(self.projectPath, False, False, 0)
		# Build the open-folder-button
		self.open_button = Gtk.Button(_("Open"))
		self.open_button.set_sensitive(True)
		self.open_button.connect('clicked', self.on_open_folder)
		self.open_button.set_tooltip_text(_("Click here to open the project-directory."))
		self.open_button.set_size_request(30, 30);
		hHeaderbox.pack_start(self.open_button, False, False, 0)
		# Build the scan-button
		self.scan_button = Gtk.Button(_("Scan"))
		self.scan_button.set_sensitive(True)
		self.scan_button.connect('clicked', self.on_scan)
		self.scan_button.set_tooltip_text(_("Click here to scan the project-directory for projects."))
		self.scan_button.set_size_request(100, 30);
		hHeaderbox.pack_end(self.scan_button, False, False, 0)
		return hHeaderbox

	def buildPgmSwitchGrid(self):
		i = 0
		labels = []
		self.switches = []
		labels.append(Gtk.Label(_("Start programs:"), xalign=0))
		self.grid.add(labels[i])
		lastLabelLeft = labels[i]
		for pgm in self.START_OPT:
			i += 1
			self.switches.append(MySwitch(halign=Gtk.Align.START, valign=Gtk.Align.CENTER))
			self.switches[i-1].pgm = pgm
			self.switches[i-1].set_tooltip_text(_("Start the program " + self.switches[i-1].pgm + "?"))
			self.switches[i-1].set_sensitive(False)
			labels.append(Gtk.Label(pgm, xalign=0))
			if i%2 == 1: # left
				self.grid.attach_next_to(labels[i], lastLabelLeft, Gtk.PositionType.BOTTOM, 1, 1)
				lastLabelLeft = labels[i]
				lastLeft = self.switches[i-1]
			else: #right
				self.grid.attach_next_to(labels[i], lastLeft, Gtk.PositionType.RIGHT, 1, 1)
			self.grid.attach_next_to(self.switches[i-1], labels[i], Gtk.PositionType.RIGHT, 1, 1)
		return

	def on_comboProject_changed(self, obj):
		for switch in self.switches:
			switch.set_sensitive(True)
			switch.set_active(False)
		currentProject = get_combo_active_value(self.comboProject)
		if (not currentProject == ""):
			if (self.config.has_section(currentProject)):
				for switch in self.switches:
					try:
						switch.set_active(self.config.getboolean(currentProject, switch.pgm))
					except:
						switch.set_active(False)

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

	def on_apply(self, obj):
		currentProject = get_combo_active_value(self.comboProject)
		projectname = os.path.splitext(os.path.basename(currentProject))[0]
		if (not self.config.has_section('global')):
			# Create non-existent section
			self.config.add_section('global')
		self.config.set('global', 'projectpath', self.projectPath.get_text())
		self.config.set('global', 'lastproject', currentProject)

		if (not self.config.has_section('projects')):
			self.config.add_section('projects')
		for k in self.projects.iterkeys():
			self.config.set('projects', k, self.projects[k])

		if (not currentProject == ""):
			if (not self.config.has_section(currentProject)):
				self.config.add_section(currentProject)
			for switch in self.switches:
				self.config.set(currentProject, switch.pgm, switch.get_active())

		with open(CONFIG, 'wb') as configfile:
			self.config.write(configfile)

		text = START_PROJECT_PGM.replace('%projectdir%', os.path.dirname(currentProject))
		text = text.replace('%project%', projectname)
		for switch in self.switches:
			if switch.get_state():
				text += ";--"+switch.pgm+"=1"
		print('Starte: {!s}'.format(text))
		args = text.split(';')
		p = subprocess.Popen(args)
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


win = Configurator()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
