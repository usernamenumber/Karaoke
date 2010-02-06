#!/usr/bin/python
import sys; sys.path.append('pylib')
import os, os.path, string, time, web
import simplejson
render = web.template.render('templates/',cache=False)
from pysqlite2 import dbapi2 as sqlite
tmpFn = "/tmp/karaoke-dbFn"

urls = (
  '/', 'index',    
	'/add', 'add', 
	'/get', 'get', 
	'/playlist', 'playlist',
	'/prototypejs', 'prototypejs',
	'/karaokejs', 'karaokejs', 
	'/loadcss', 'loadcss',)
	
def usage():
        appname = os.path.basename(sys.argv[0])
        print "\nUSAGE: %s CONFIGFN\n" % appname
        print """Example configuration file:
[general]
dbFn = /var/karaoke/karaoke.sqlite
musicDir = /var/karaoke/music
"""
	
def put_main():
		conn = sqlite.connect(dbFn)
		cursor = conn.cursor()
		songs = []
		#genres = cursor.execute("select distinct genre from music").fetchall()
		#playlistQuery = "select music.artist,music.title,playlist.user from music inner join playlist on playlist.song_id = music.id"
		#playlist = cursor.execute(playlistQuery).fetchall()
		return render.index()
	
class prototypejs:
	def GET(self):
		#fh = open("lib/protoculous-1.0.2-packed.js","r")
		fh = open("lib/prototype.js","r")
		return fh.read()
		
class karaokejs:
	def GET(self):
		fh = open("lib/karaoke.js","r")
		return fh.read()
	
class loadcss:
	def GET(self):
		fh = open(os.path.join("themes","default.css"),"r")
		return fh.read()
		
		
class index:
	def GET(self):
		return put_main()
		
class playlist:
	def POST(self):
		conn = sqlite.connect(dbFn)
		cursor = conn.cursor()
		inputs = web.input()
		if inputs.has_key('trackSelector') and inputs['trackSelector'] != "":
			trackid = web.input()['trackSelector']
			if inputs.has_key('singerName'):
				user	= web.input()['singerName']
			else:
				user 	= "Some Singer"
			cursor.execute("insert into playlist values (NULL,?,?,?)", (trackid,time.time(),user))
			conn.commit()
			
		playlistQuery = "select music.artist,music.title,playlist.user from music inner join playlist on playlist.song_id = music.id limit 20"
		playlist = cursor.execute(playlistQuery).fetchall()		
		web.header('Content-type', 'application/json')
		fh = open("/tmp/karaokeLog","w")
		fh.write("%s\n\n%s\n" % (playlistQuery,inputs))
		fh.close()
		return simplejson.dumps(playlist)
	
	def GET(self):
		return self.POST()
		
class get:
	def POST(self):
		conn = sqlite.connect(dbFn)
		cursor = conn.cursor()
		inputs = web.input()
		criteriaList = []	
		criteriaArgs = []
		
		if inputs.has_key('genre') and inputs['genre'] != "":
			criteriaList.append('genre=?')
			criteriaArgs.append(inputs['genre'])
			
		if inputs.has_key('artistSelector') and inputs['artistSelector'] != "":
			criteriaList.append("artist = ?")
			criteriaArgs.append(inputs['artistSelector'])
		
		if inputs.has_key('artistPartial') and inputs['artistPartial'] != "":
			if inputs.has_key('lookfor') and inputs['lookfor'] == "combined":
				criteriaList.append("(artist like '%%%s%%' OR title like '%%%s%%')" % (inputs['artistPartial'],inputs['artistPartial']))
			else:
				criteriaList.append("artist like '%%%s%%'" % inputs['artistPartial'])
		
		if len(criteriaList) > 0:
			criteria = "WHERE " + string.join(criteriaList," AND ")
		else:
			criteria = ""
		
		q = False
		if inputs.has_key('lookfor') and inputs['lookfor'] == "tracks":
			# Refuse to list every track if no critera are given
			if criteria != "":
				q = "select id,title from music %s" % criteria
		elif inputs.has_key('lookfor') and inputs['lookfor'] == "combined":
			if criteria != "":
				q = "select id,artist,title from music %s" % criteria
		elif inputs.has_key('lookfor') and inputs['lookfor'] == "genre":
			q = "select distinct genre from music %s" % criteria
		else:
			q = "select id,artist from music %s group by artist" % criteria
		
		if q:
			results = cursor.execute(q,criteriaArgs).fetchall()
		else: 
			results = []		
		#results.append(q)
		#results.append(criteriaArgs)
		web.header('Content-type', 'application/json')
		return simplejson.dumps(results)
		
		#fh = open("/tmp/karaokeQueryLog","a")
		#if q:
		#	fh.write("%s:\nQUERY:\n%s, %s\nRESULTS:\n%s\n" % (time.ctime(),q,criteriaArgs,simplejson.dumps(results)))
		##else: 
		##	fh.write("%s: get() run, but no query constructed\n" % time.ctime())
		#fh.close()

	def GET(self):
		self.POST()
		
			
if __name__ == "__main__": 
	import ConfigParser
	c = ConfigParser.ConfigParser()
	if len(sys.argv) < 2:
		usage()
		sys.exit(1)
	configFn = sys.argv[1]
	del(sys.argv[1])
	c.read(configFn)
	dbFn = c.get("general","dbFn")
	
	# this bit is really kludgey, but calls to handle web clients
	# create separate invocations that don't use __main__, so
	# we need a way of sharing the config data between instances
	# without hard-coding the location of the config file.
	tmpFh = open(tmpFn,"w")
	tmpFh.write(dbFn)
	tmpFh.close()
	app = web.application(urls, globals(),autoreload=True)
	app.run()
else:
	tmpFh = open(tmpFn,"r")
	dbFn = tmpFh.readline()
	
