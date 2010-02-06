#!/bin/bash

dbFn=$1
if [ -z $dbFn ] 
then
	echo "Specify a db"
	exit 1 
fi

if [ ! -f $dbFn ]
then
	echo "Could not find $dbFn"
	exit 2
fi 

id=$(echo "select song_id from playlist limit 1;" | sqlite3 $dbFn)
if [ $? -ne 0 ]
then
	echo "Failed to get song id: $id"
	exit 3
fi

path=$(echo "select archivefn from playlist inner join music on playlist.song_id = music.id limit 1;" | sqlite3 $dbFn)
if [ $? -ne 0 ]
then
 	echo "Failed to get archive name: $path"
	exit 4
fi

delQuery="delete from playlist where song_id=$id;delete from music where id=$id;"
echo $delQuery | sqlite3 $dbFn

if echo $path | grep '[[:alpha:]]' &>/dev/null
then
	mv "$path" /media/MEDIA/Projects/Karaoke/broken_songs/
else
	echo "Warning: Not attempting to move non-existent path"
fi

echo ""
echo "Removed track ID $id, $path"
echo ""

