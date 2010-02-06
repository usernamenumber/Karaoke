#!/usr/bin/python
import sys; sys.path.append('pylib')
import os, os.path,string,time,types
#import eyeD3
import tagpy
import re
import zipfile
import cStringIO
from pysqlite2 import dbapi2 as sqlite
import random
updateCnt = 0
insertCnt = 0

def usage():
	appname = os.path.basename(sys.argv[0])
	print "\nUSAGE: %s CONFIGFN\n" % appname
	print """Example configuration file:
[general]
dbFn = /var/karaoke/karaoke.sqlite
musicDir = /var/karaoke/music
"""
class karaokeTrack():
	def __init__(self,cdgFn,musicFn,zipFn=None):
		self.cdgFn	 	= cdgFn
		self.musicFn 	= musicFn
		self.zipFn		= zipFn
		
	def getMusicData(self):
		ext = self.musicFn.split(".")[-1]
		if self.zipFn is not None:
			print "GET for %s" % self.zipFn
			z = zipfile.ZipFile(self.zipFn)
			## Catching this at a higher level
			#try:
			#	data = z.read(self.musicFn)
			#except BadZipfile:
			#	return False
			data = z.read(self.musicFn)
			#return cStringIO.StringIO(data)
			return writeTmpFile(data,ext)
		else:
			print "GET for %s" % self.cdgFn
			data = open(self.musicFn,"r").read()
			#return data
			return writeTmpFile(data,ext)			
			
def writeTmpFile(data,ext):
  fn = "/tmp/karaoke-%s.%s" % (random.randint(1000,9999),ext)
  while os.path.exists(fn): 
    fn = "/tmp/karaoke-%s.%s" % (random.randint(1000,9999),ext)
  #print fn
  open(fn,"w").write(data)
  return fn
  

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

def storedata(arg,dirname,fnames):
		global updateCnt
		global insertCnt
		reFnSplit = re.compile('(.*)\.(.*)')
		for fn in fnames:
			# Hackish fixes for filenames with funky chars, which
			# pykdb chokes on.
			# TODO: There's probably a better way to test this...
			try:
				fixedFn = fixFn(fn)
			except UnicodeDecodeError:
				sys.stderr.write("WARNING: Skipping bad filename %s\n" % fn)
				continue
			if fn != fixedFn:
				sys.stderr.write("Changing bad FN %s to %s\n" %	(fn,fixedFn))				
				fn = os.path.join(dirname,fn)
				fixedFn = os.path.join(dirname,fixedFn)
				try:
					os.rename(fn,fixedFn)
				except Exception, e:
					sys.stderr.write("Rename operation FAILED. Skipping: %s\n" % e)
					continue
				# dirname already added above
				fn = fixedFn
			else:
				fn = os.path.join(dirname,fn)
			
			tracks = []			
			# zip files may contain mp3/cdg combos
			if fn.endswith(".zip"):
				if not zipfile.is_zipfile(fn):
					continue
				zipFn = fn
				files = {}
				z = zipfile.ZipFile(zipFn)
				# List filenames in the zip
				for zfn in z.namelist():
					m = reFnSplit.match(zfn)
					if not m:
						continue
					(base,ext) = m.groups()
					if not files.has_key(ext):
						files[ext] = []
					files[ext].append(base)
				# Use a cdg only if there is also an associated music file
				for baseFn in files['cdg']:
					for ext in musicExtensions:
						if files.has_key(ext) and baseFn in files[ext]:
							tracks.append(karaokeTrack(baseFn+'.cdg',baseFn+'.'+ext,zipFn))
							break
							
			# For non-archives, we only care about .cdg files
			elif not fn.endswith(".cdg"):
				continue
				
			# ...and should skip .cdgs that don't have .ogg or .mp3s
			baseFn = string.join(string.split(fn,".")[:-1])
			musicFn = None
			for ext in musicExtensions:
				if os.path.exists(baseFn+"."+ext):
					tracks.append(karaokeTrack(baseFn+'.cdg',baseFn+'.'+ext))
					break
					
			if len(tracks) == 0:
				continue
						
			# We seem to have a valid cdg/{ogg,mp3} combo. 
			for track in tracks:
				if track.zipFn:
					# This needs to be done now, rather than in karaokePlayer
					# because storing it in the db can change the encoding,
					# making comparisions with the result of fixFn on entries
					# read from the zip later on misleading
					cdgFn = fixFn(track.cdgFn)
					archiveFn = track.zipFn
				else:
					cdgFn = track.cdgFn
					archiveFn = "NULL"
				#id = eyeD3.Tag()
				try:
					trackData = track.getMusicData()
				except Exception,e:
					if track.zipFn:
						fn = track.zipFn
					else:
						fn = track.cdgFn
					raise
					sys.stderr.write("Error reading %s: %s" % (fn,e))
					continue
				# No longer necesary if exceptions caught above?
				if not trackData:
					sys.stderr.write("Bad zipfile: %s" % track.zipFn)
					continue
				#id.link(trackData)
				id = tagpy.FileRef(trackData).tag()
				artist 		= id.artist and "%s" % id.artist or "NULL"
				album 		= id.album and "%s" % id.album or "NULL"
				title 		= id.title and "%s" % id.title or "NULL"
				genre 		= id.genre and "%s" % id.genre or "NULL"
				#tracknumber = id.getTrackNum()[0] and "'%d'" % id.getTrackNum()[0] or "NULL"
				tracknumber = "NULL"
				if os.path.exists(trackData):
				  os.unlink(trackData)
				q = "select * from music where (cdgfn=? and archivefn=?)"
				res = cursor.execute(q, (cdgFn,archiveFn)).fetchall()
				if len(res) > 0:
					cursor.execute("update music set artist=?,album=?,title=?,genre=?,tracknumber=? where (cdgfn=? and archivefn=?)", (artist,album,title,genre,tracknumber,cdgFn,archiveFn))
					updateCnt += 1
				else:
					cursor.execute("insert into music	values(NULL,?,?,?,?,?,?,?)", (cdgFn,archiveFn,artist,album,title,genre,tracknumber))
					insertCnt += 1
		return (insertCnt,updateCnt)
							
if __name__ == "__main__":
	import ConfigParser
	c = ConfigParser.ConfigParser()
	if len(sys.argv) < 2:
		usage()
		sys.exit(1)
	configFn = sys.argv[1]
	c.read(configFn)
	musicDir = c.get("general","musicDir")
	dbFn = c.get("general","dbFn")

	createQs = []
	if not os.path.exists(dbFn):
		createQs.append("CREATE TABLE music (id integer primary key autoincrement, cdgfn text, archiveFn text, artist text, album text, title text, genre text, tracknumber int)") 
		createQs.append("CREATE TABLE playlist (id integer primary key, song_id int, added, user)")


	conn = sqlite.connect(dbFn)
	cursor = conn.cursor()

	for q in createQs:
		cursor.execute(q)

	musicExtensions = ["ogg","mp3","wav"]
	os.path.walk(musicDir,storedata,None)
	conn.commit()
	print "Added %s new records\nUpdated %s existing records" % (insertCnt,updateCnt)
