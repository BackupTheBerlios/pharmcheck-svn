#! /usr/bin/python
# -*- coding: latin1 -*-

"""
 GPharmcheck - a graphical Frontend for Pharmcheck
 * Copyright (C) 2005 Hendrik Brandt,
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
 * 02111-1307, USA.
"""

__version__ = '0.1'
__author__  = ['Hendrik Brandt']

import sys, thread

try:
	import pygtk
	pygtk.require("2.0")
	import gtk
except:
        print "You need to install pyGTK or GTKv2 ",
        print "or set your PYTHONPATH correctly."
        print "try: export PYTHONPATH=",
        print "/usr/local/lib/python2.4/site-packages/"
        sys.exit(1)

from pharmcheck import Check

class GUI:

	def __init__(self, url):
		# Fenster + Inhalt zusammenbasteln
		self.windowMain = gtk.Window(gtk.WINDOW_TOPLEVEL)
		
		vboxMain = gtk.VBox()
		vboxInOut = gtk.VBox(False, 6)
		hboxAddress = gtk.HBox(False, 6)
		
		labelAddress = gtk.Label("_Adress:")
		labelAddress.set_use_underline(True)
		self.inputAddress = gtk.Entry()
		buttonCheck = gtk.Button("_Check")
		buttonCheck.connect("clicked", self.button_check_clicked)
		buttonClear = gtk.Button("C_lear all")
		buttonClear.connect("clicked", self.button_clear_clicked)

		self.inputAddress.connect("changed", self.input_address_changed, buttonCheck)
		self.inputAddress.connect("key_press_event", self.input_address_keypress)
		
		labelAddress.set_mnemonic_widget(self.inputAddress)
		
		hboxAddress.pack_start(labelAddress, False, True)
		hboxAddress.add(self.inputAddress)
		hboxAddress.pack_end(buttonClear, False, True)
		hboxAddress.pack_end(buttonCheck, False, True)
		
		# Tastenkürzelgruppe mit Fenster verbinden
		accel = gtk.AccelGroup()
		self.windowMain.add_accel_group(accel)
		
		# Menu zusammenbasteln
		menuBar = gtk.MenuBar()
		rootMenu = gtk.MenuItem("_GPharmcheck")
		
		mainMenu = gtk.Menu()
		menuItemAbout = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
		menuItemQuit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
		
		menuItemQuit.add_accelerator("activate", accel, ord("Q"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
		
		mainMenu.append(menuItemAbout)
		mainMenu.append(gtk.SeparatorMenuItem())
		mainMenu.append(menuItemQuit)
		
		menuItemAbout.connect("activate", self.menu_item_about_activate)
		menuItemQuit.connect("activate", self.menu_item_quit_activate)
		
		rootMenu.set_submenu(mainMenu)
		menuBar.append(rootMenu)
		
		vboxMain.pack_start(menuBar, False, True, 0)

		self.output = gtk.TextView()
		outputScroll = gtk.ScrolledWindow()
		outputScroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
		outputScroll.add(self.output)
		outputScroll.set_shadow_type(gtk.SHADOW_IN)

		vboxInOut.pack_start(hboxAddress, False, True)
		vboxInOut.pack_end(outputScroll, True, True)
		
		vboxInOut.set_border_width(6)
		
		vboxMain.add(vboxInOut)
		
		
		buttonCheck.set_sensitive(False)
		
		# Mit Signalen verbinden
		self.windowMain.connect("delete_event", self.delete_event)
		
		self.windowMain.add(vboxMain)
		self.windowMain.move(200,100)
		self.windowMain.resize(400, 300)
		self.windowMain.set_title("GPharmcheck "+__version__)
		
		self.windowMain.show_all()
		
		gtk.threads_init()
		gtk.threads_enter()	
		gtk.main()
		gtk.threads_leave()
		
	def input_address_changed(self, widget, button):
		if len(widget.get_text())>0:
			button.set_sensitive(True)
		else:
			button.set_sensitive(False)
			
	def input_address_keypress(self, widget, event):
		if gtk.gdk.keyval_name(event.keyval) == "Return" and len(self.inputAddress.get_text())>0:
			thread.start_new_thread(self.performe_check, ())
			
	def performe_check(self):
		out = self.output
		
		url = self.inputAddress.get_text()

		gtk.threads_enter()	
		output = out.get_buffer()
		output.set_text(output.get_text(output.get_start_iter(), output.get_end_iter())+"\nChecking "+url+"...\n")
		out.set_buffer(output)
		gtk.threads_leave()
		
		check = Check()
		r = check.check(url)
		o = ""
		
		if r[0] == -1:
			o = "Error: "+url+" not found"

		elif r[0] == -2:
			o =  "error querying remote server.\nerror code :" + r[1] + "\nerror message: "+ r[2]

		elif r[0] == 0:
			o =  url + " resolves LOCAL to " + r[1] +"\n"+ url + " resolves REMOTE to " + r[2] + "\nthis could be a pharming attac or a location-based dns"
			
		elif r[0] == 1:
			o = "No differences found!\n" + url + " resolves to " + self.explode(r[2])
		
		gtk.threads_enter()
		output = out.get_buffer()
		output.set_text(output.get_text(output.get_start_iter(), output.get_end_iter())+"\n"+o+"\n---\n")
		out.set_buffer(output)
		gtk.threads_leave()
		
	
	def button_check_clicked(self, widget):
		thread.start_new_thread(self.performe_check, ())				
		
	def button_clear_clicked(self, widget):
		output = self.output.get_buffer()
		output.set_text("")
		self.output.set_buffer(output)
		self.inputAddress.set_text("")
		
	
	
	def delete_event(self, widget, event):
		gtk.main_quit()
	
	def menu_item_about_activate(self, widget):
		about = gtk.AboutDialog()
		about.set_authors(["Hendrik Brandt <rtfm@deinadmin.de>"])
		about.set_name("GPharmcheck")
		about.set_version(__version__)
		about.set_copyright("(C) 2005 Hendrik Brandt")
		about.set_license("This program is distributed unter the terms of the "
						  "GNU General Public License version 2.\n\nSee http://www.fsf.org/"
						  "licensing/licenses/gpl.html for the complete license.\n\n"
						  "This program comes WITHOUT ANY WARRANTY.")

		about.set_website("http://deinadmin.de/")
		
		about.show()

	def menu_item_quit_activate(self, widget):
		print "Bye"
		gtk.main_quit()
		
	def explode(self, list):
		r = ""
		for a in list:
			r = r + a + ", "
		r=r[:-2]
		return r
	

# Start
if __name__ == '__main__':

	if len(sys.argv)==1:
		interface = GUI("")
	else:
		interface = GUI(sys.argv[1])
