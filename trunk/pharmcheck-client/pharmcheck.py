#! /usr/bin/python
# -*- coding: latin1 -*-

"""
 Pharmcheck security checker
 * Copyright (C) 2005 Lorenz Kiefner and Hendrik Brandt,
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

__version__ = '0.3'
__author__  = ['Lorenz Kiefner', 'Hendrik Brandt']


from httplib import HTTP
import sys, socket


# Checking-Object
class Check:
	def __init__(self):
		pass	
	def check(self, url):
		try:
			local = self.localdns(url)
		except:
			# Not found
			return [-1]

		remote = self.server_lookup(url)
		
		if remote[0]==1:
			if remote[1].count(local) !=0:
				# All OK
				return [1, local, remote[1]]
			else:
				# Not OK
				return [0, local, remote[1]]
		else:
			return remote
		
	def localdns(self, addr):
		return socket.gethostbyname(addr)

	def server_lookup(self, addr):
		req = HTTP("deinadmin.de")
		req.putrequest("GET", "/projects/pharmcheck/pharmcheck.php?name=" + addr)
		req.putheader("Host", "deinadmin.de")
		req.putheader("User-Agent", "pharmcheck v0.3 2005-08-14")
		req.endheaders()
		ec, em, h = req.getreply()

		if (ec != 200):
			return [-2, ec, em]
		else:
			fd=req.getfile()
		
			lines=[]
			line=fd.readline()
			while line:
				lines.append(line[:-1])		# \n abschneiden. windows-kompatibel?
				line=fd.readline()

			fd.close()
			return [1, lines]


# For Text-Internface
class Terminal:
	myname = ""
	def __init__(self, myname):
		self.myname = myname
		
	def check(self, url):
		check = Check()
		r = check.check(url)

		print self.myname, "- checking", url

		if r[0] == -1:
			print "Error: '", url, "' not found"

		elif r[0] == -2:			
			print "error querying remote server."
			print "error code   :", r[1]
			print "error message:", r[2]

		elif r[0] == 0:
			print url, "resolves LOCAL  to", r[1]
			print url, "resolves REMOTE to", self.explode(r[2])
			print "this could be a pharming attac or a location-based dns"
			
		elif r[0] == 1:
			print "No differences found!", url, "resolves to", self.explode(r[2])
		
		sys.exit(0)

	def explode(self, list):
		r = ""
		for a in list:
			r = r + a + ", "
		r=r[:-2]
		return r

	def options_exit(self):
		print self.myname, "checks dns-lookups"
		print "syntax:", self.myname, "<your banking server>"
		
# Start
if __name__ == '__main__':

	interface = Terminal(sys.argv[0])

	if len(sys.argv) != 2:
		interface.options_exit();
		sys.exit(0);
		
	else:
		interface.check(sys.argv[1])

