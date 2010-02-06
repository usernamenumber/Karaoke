#!/usr/bin/python

import os,os.path
# This doesn't seem to help. 
# Have to export LD_LIBRARY_PATH from shell for now
if os.environ.has_key('LD_LIBRARY_PATH'):
	os.environ['LD_LIBRARY_PATH'] += ":pylib"
else:
	os.environ['LD_LIBRARY_PATH'] = "pylib"

import sys
sys.path.insert(0,'pylib')

import curses,os,select
import pycdg,pykconstants
import pygame
from pykplayer import manager
from pysqlite2 import dbapi2 as sqlite
import zipfile
import re, types

import re
reCdgBaseFn = re.compile("(.*)\.cdg$",re.I)



def usage():
        appname = os.path.basename(sys.argv[0])
        print "\nUSAGE: %s CONFIGFN\n" % appname
        print """Example configuration file:
[general]
dbFn = /var/karaoke/karaoke.sqlite
musicDir = /var/karaoke/music
"""


class goBackException(Exception):
	pass
class quitException(Exception):
	pass

class Player(pycdg.cdgPlayer):
	def __init__(self, song, errorNotifyCallback=None, doneCallback=None):
		pycdg.cdgPlayer.__init__(self, song, errorNotifyCallback, doneCallback)
		manager.OpenDisplay(flags=pygame.FULLSCREEN)
	def handleEvent(self, event):
				if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_SPACE:
								self.Pause()
						if event.key == pygame.K_n:
								self.Close()
						if event.key == pygame.K_p:
								raise goBackException
						if event.key == pygame.K_q:
								raise quitException
				pycdg.cdgPlayer.handleEvent(self, event)

# This fcn needs to be identical in karaokePlayer and karaokeUpdatDB!
def fixFn(fn):
    encodeMe = None
    if type(fn) == types.UnicodeType:
        encodeMe = fn
    else:
        for encoding in ['ascii','latin-1','utf-8','utf-16']:
            try:
                encodeMe = fn.decode(encoding)
            except:
                continue
            else:
                #print "Match for %s encoding" % encoding
                break
    if not encodeMe:
			sys.stderr.write("WARNING: fixFn() couldn't decode string, returning as-is\n")
			encodeMe = fn
    fixedFn = encodeMe.encode('ascii','replace')
    return fixedFn

if __name__ == "__main__":
	import ConfigParser
	c = ConfigParser.ConfigParser()
	if len(sys.argv) < 2:
		usage()
		sys.exit(1)
	configFn = sys.argv[1]
	c.read(configFn)
	
	tmpDir	= c.get("general","tmpDir")
	if not os.path.exists(tmpDir):
		os.mkdir(tmpDir)
	
	dbFn 		= c.get("general","dbFn")
	conn 		= sqlite.connect(dbFn)
	cursor 	= conn.cursor()
	
	pycdg.CDG_DISPLAY_WIDTH   = 1152
	pycdg.CDG_DISPLAY_HEIGHT  = 800
	
	#CDG_DISPLAY_WIDTH   = 294
	#CDG_DISPLAY_HEIGHT  = 204
	
	while True:
		try:
			q = "select playlist.id, music.cdgfn, music.archivefn from music inner join playlist on playlist.song_id = music.id order by added limit 1"
			songinfo = cursor.execute(q).fetchone()
			if not songinfo:
				break
				
			cdgFn = songinfo[1]
			for x in range(len(songinfo)):
				print "SI[%s] = %s" % (x,songinfo[x])
			print ""
					
			if songinfo[2] is not None and songinfo[2] != "NULL".encode('utf-8'):
				baseFn = reCdgBaseFn.match(cdgFn).groups()[0]
				reBaseFnMatch = re.compile("^"+re.escape(baseFn))
				z = zipfile.ZipFile(songinfo[2])
				for fn in z.namelist():
					fixedFn = fixFn(fn)
					if reBaseFnMatch.match(fixedFn):
						fh = open(os.path.join(tmpDir,fixedFn),"w")
						fh.write(z.read(fn))
						fh.close()
						print "Wrote to %s" % fixedFn
				cdgFn = os.path.join(tmpDir,fixFn(cdgFn))
				
			print "PLAYING: %s" % cdgFn
			player = Player(cdgFn)			
			player.Play()
			
			while player.State != pykconstants.STATE_CLOSED:
				pycdg.manager.Poll()
			#songIdx += 1
		#except goBackException:
		#	songIdx -= 1
		#	continue
		except quitException:
			player.Close()
			break
		except Exception,e:
			sys.stderr.write("WARNING %s generated an exception: %s\n" %	(cdgFn,e))

		cursor.execute("delete from playlist where id=?",(songinfo[0],))
		conn.commit()

