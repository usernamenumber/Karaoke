#!/usr/bin/python
import curses,os,select,sys
sys.path.insert(0,'pylib')
import pycdg,pykconstants
import pygame
from pykplayer import manager
from pysqlite2 import dbapi2 as sqlite

def usage():
  appname = os.path.basename(sys.argv[0])
  sys.stderr.write("\nUSAGE: %s file\n" % appname)
  sys.stderr.write("File can be either a .cdg or a .pls playlist (one file per line)\n\n")

class goPrevException(Exception):
  pass
class goNextException(Exception):
  pass
class quitException(Exception):
  pass

class Player(pycdg.cdgPlayer):
  def __init__(self, song, errorNotifyCallback=None, doneCallback=None):
    self.song = song
    pycdg.cdgPlayer.__init__(self, song, errorNotifyCallback, doneCallback)
    manager.OpenDisplay(flags=pygame.FULLSCREEN)
  def handleEvent(self, event):
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_SPACE:
        self.Pause()
      if event.key == pygame.K_p:
        raise goPrevException
      if event.key == pygame.K_n:
        raise goNextException
      if event.key == pygame.K_q:
        raise quitException
    pycdg.cdgPlayer.handleEvent(self, event)

class songSet():
	def __init__(self,songs):
		self.songs = songs
		self.idx = 0
	def _play(self,idx):
		song = self.songs[idx]
		print "PLAYING: %s" % song
		p = Player(song)
		p.Play()
		while p.State != pykconstants.STATE_CLOSED:
			pycdg.manager.Poll()
	def Play(self,idx=None):
		if not idx:
			idx = self.idx
		for i in range(idx,len(self.songs)):
			print "Handling song #%s" % i
			try:
				self._play(i)
			except goNextException:
				print "SKIPPING"
				continue
			except goPrevException:
				print "BACKING UP"
				if i > 0:
					self.Play(i-1)
				else:
					self.Play(i)
	
if len(sys.argv) <=1 :
	usage()
	sys.exit(1)

fn = sys.argv[1]
ext = fn.split(".")[-1]
if ext == "pls":
	files = []
	for f in open(fn,"r").readlines():
		if f[0] != "#":
			files.append(f.strip())
else:
	files = [fn,]

try:
	songSet(files).Play()
except quitException:
	pass
