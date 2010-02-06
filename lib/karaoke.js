//alert("loaded karaoke.js");

function handleError(request) {
	alert("ERROR");
	//var status = request.status;
	//var text	 = request.statusText;
	//$ ('warnings').innerHTML += 'ERROR: ' + status + ': ' + text;
}

function renderSearchToggle(searchType) {
	$ ('searchToggleContainer').innerHTML = "";
	
	var searchToggleArtist = document.createElement('input');
	searchToggleArtist.setAttribute("id","searchToggleArtist");
	searchToggleArtist.setAttribute("type","radio");
	searchToggleArtist.setAttribute("name","searchToggle");
	searchToggleArtist.setAttribute("value","artist");
	searchToggleArtist.setAttribute("onchange","javascript:searchToggle('artist')");
	searchToggleArtistText = document.createTextNode('Browse by Artist');
	$ ('searchToggleContainer').appendChild(searchToggleArtist);
	$ ('searchToggleContainer').appendChild(searchToggleArtistText);
	
	var searchToggleCombined = document.createElement('input');
	searchToggleCombined.setAttribute("id","searchToggleCombined");
	searchToggleCombined.setAttribute("type","radio");
	searchToggleCombined.setAttribute("name","searchToggle");
	searchToggleCombined.setAttribute("value","combined");
	searchToggleCombined.setAttribute("onchange","javascript:searchToggle('combined')");
	searchToggleCombinedText = document.createTextNode('General Search');
	$ ('searchToggleContainer').appendChild(searchToggleCombined);
	$ ('searchToggleContainer').appendChild(searchToggleCombinedText);
}

function renderArtistlist(request) {
	//alert('renderArtistlist START');
	var jsonData = request.responseJSON;
	var artistSelector = document.createElement('select');
	artistSelector.setAttribute("multiple",true);
	artistSelector.setAttribute("size",10);
	artistSelector.setAttribute("id","artistSelector");
	artistSelector.setAttribute("class","artistSelector");
	artistSelector.setAttribute("onupdate","javascript:clearTracklist()");
	artistSelector.setAttribute("onclick","javascript:updateTracks()");
	jsonData.each(function(v) {
		var option = document.createElement('option');
		option.innerHTML = v[1];
		artistSelector.appendChild(option)
	});
	if ($ ('artistSelector')) {
		$ ('artistContainer').removeChild($ ('artistSelector'))
	}
	$ ('artistContainer').appendChild(artistSelector);
	//alert('renderArtistlist DONE');
}

function renderCombinedList(request) {
	//alert('renderCombinedList');
	/*while ($ ('combinedList').rows.length > 0) {
		//alert($ ('combinedList').rows.length);
		$ ('combinedList').deleteRow(0);
	}*/
	
	freshTbl = document.createElement("table");
	freshTbl.setAttribute("id","combinedList");
	freshTblHead = freshTbl.createTHead();
	freshTblHeadHeadings = freshTblHead.insertRow(0);
	freshTblHeadArtist = freshTblHeadHeadings.insertCell(0);
	freshTblHeadArtist.innerHTML = "Artist";
	freshTblHeadTrack = freshTblHeadHeadings.insertCell(1);
	freshTblHeadTrack.innerHTML = "Track";	
	$ ('combinedList').replace(freshTbl);
	
	var jsonData = request.responseJSON;
	if (jsonData.length > 0) {
		var i = 0;
		jsonData.each(function(v) {
			var row = document.createElement('tr');
			row.setAttribute("ondblclick","javascript:updatePlaylist(false,'"+v[0]+"')");
			var artistCell = row.insertCell(0);
			artistCell.innerHTML = v[1];
			artistCell.setAttribute("class","unselectable");
			artistCell.onselectstart = function() { return(false); };
			var titleCell  = row.insertCell(1);
			titleCell.innerHTML = v[2];
			titleCell.setAttribute("class","unselectable");
			titleCell.onselectstart = function() { return(false); };
			$ ('combinedList').appendChild(row);
		});
	} else {
		// Hmm.. for some reason the below appends to thead
		//var row  = $ ('combinedList').insertRow(1);
		var row = document.createElement('tr');
		var cell = row.insertCell(0); 
		cell.setAttribute("colspan",2);
		cell.innerHTML = "<i>No Matches</i>";
		$ ('combinedList').appendChild(row);
	}
}

function clearTracklist() {
	//alert('clearTracklist start');
	renderTracklist(false);
	//alert('clearTracklist done');
}

function renderTracklist(request) {
	//alert(request.responseText);
	if (request) {
		var jsonData = request.responseJSON;
	} else {
		var jsonData = new Array();
	}
	var trackSelector = document.createElement('select');
	trackSelector.setAttribute("multiple",true);
	//trackSelector.size = 10;
	trackSelector.setAttribute("size",10);
	trackSelector.setAttribute("id","trackSelector");
	trackSelector.setAttribute("class","trackSelector");
	trackSelector.setAttribute("ondblclick","javascript:updatePlaylist(false)");
	if (jsonData) {
		jsonData.each(function(v) {
			var option = document.createElement('option');
			option.innerHTML = v[1];
			option.setAttribute("value",v[0]);
			trackSelector.appendChild(option)
		});
	}
	if ($ ('trackSelector')) {
		$ ('trackContainer').removeChild($ ('trackSelector'))
	}
	$ ('trackContainer').appendChild(trackSelector);
	//alert('renderTracklist DONE');
}

function renderPlaylist (request) {
	freshTbl = document.createElement("table");
	//freshTbl.setAttribute("border","1");
	freshTbl.setAttribute("id","playlist");
	freshTblHead = freshTbl.createTHead();
	freshTblHeadHeadings = freshTblHead.insertRow(0);
	freshTblHeadTitle = freshTblHeadHeadings.insertCell(0);
	freshTblHeadTitle.innerHTML = "Title";
	freshTblHeadArtist = freshTblHeadHeadings.insertCell(1);
	freshTblHeadArtist.innerHTML = "Artist";
	freshTblHeadTrack = freshTblHeadHeadings.insertCell(2);
	freshTblHeadTrack.innerHTML = "Singer";	
	$ ('playlist').replace(freshTbl);
	
	var jsonData = request.responseJSON;
	if (jsonData.length > 0) {
		var i = 0;
		jsonData.each(function(v) {
			//var row = $ ('playlist').insertRow(i++);
			var row = document.createElement('tr');
			var artistCell = row.insertCell(0);
			artistCell.innerHTML = v[0];
			var titleCell  = row.insertCell(1);
			titleCell.innerHTML = v[1];
			var singerCell   = row.insertCell(2);
			singerCell.innerHTML = v[2]
			$ ('playlist').appendChild(row);
		});
	} else {
		var row = document.createElement('tr');
		var cell = row.insertCell(0); 
		cell.setAttribute("colspan",3);
		cell.innerHTML = "<i>No Playlist</i>";
		$ ('playlist').appendChild(row);
	}
	//alert('renderPlaylist done');
}

function renderGenre (request) {	
	//alert("renderGenre start");
	var jsonData = request.responseJSON;
	if ( ! $ ('genre') ) {
		var genre = document.createElement('select');
		genre.setAttribute("id","genre");
		var option = document.createElement('option');
		genre.appendChild(option);
		$ ('genreContainer').appendChild(genre);
	}
	if ( ! $ ('genre').hasAttribute('onchange') ) {
		genre.setAttribute("onchange","javascript:updateArtists()");		
	}
	if (jsonData) {
		var option = document.createElement('option');
		genre.appendChild(option);
		jsonData.each(function(v) {
			var option = document.createElement('option');
			option.innerHTML = v[0];
			$ ('genre').appendChild(option);
		});
	}
	//alert("renderGenre complete");
}

var updateGenre = function () {
	new Ajax.Request('/get', {
		parameters: { 
			lookfor: 'genre',
		},
		onSuccess: renderGenre,
		onFailure: handleError,
	});
}

var updateArtists = function () {
	var params = new Array();
	if ( $ ('genre') ) {
		params['genre'] = $F ('genre');
	} 
	if ( $ ('artistPartial') ) {
		params['artistPartial'] = $F ('artistPartial');
	}
	new Ajax.Request('/get', {
		parameters: params,
		onSuccess:  renderArtistlist,
		onFailure:  handleError,
	});
	clearTracklist();
}

var updateCombined = function() {
	//alert($F ('artistPartial'));
	var params = new Array();
	params['lookfor'] = "combined";	
	
	if ( $ ('genre') ) {
		params['genre'] = $F ('genre');
	} 
	if ( $ ('artistPartial') ) {
		params['artistPartial'] = $F ('artistPartial');
	}
	
	new Ajax.Request('/get', {
		parameters: params,
		onSuccess:  renderCombinedList,
		onFailure:  handleError,
	});
	clearTracklist();
}

var updateTracks = function () {
	var params = new Array();
	params['lookfor'] = "tracks";
	
	if ($ ('genre') && $F ('genre') != '') {
		params['genre'] = $F ('genre');
	}
	if ($ ('artistPartial') && $F ('artistPartial') != '') {
		params['artistPartial'] = $F ('artistPartial');		
	}
	if ($ ('artistSelector') && $F ('artistSelector') != '') {
		/*
		This hack brought to you by the fact that $F() seems to
		collapses spaces in the values it delivers for some reason 
		(bug?). As a result, when the value is used to find an 
		exact match in the db, values with multiple adjacent spaces
		fail to match the db values they should. 
		*/
		var artistSelectorValue = ($ ('artistSelector').options[$ ('artistSelector').selectedIndex].innerHTML).unescapeHTML();
		params['artistSelector'] = artistSelectorValue;
	}
	//alert(params['artistSelector']);
	new Ajax.Request('/get', {
		parameters: params,
		onSuccess: renderTracklist,
		onFailure: handleError,
	});
	//alert ("updateTracks finish");
}

var updatePlaylist = function (refresh, trackID) {
	//alert("Refresh: "+refresh+", trackID: "+trackID);
	params	= "lookfor=tracks&";
	//alert(refresh);
	refresh = (refresh == null) ? true : refresh;
	//alert(refresh);
	if ( ! refresh ) {
		//alert("GO");
		resources 	= new Array('trackSelector','singerName');
		if (trackID) {
			params += "trackSelector="+trackID+"&";
		} else if ($( 'trackSelector' ) && $F ( 'trackSelector' ) != '') {
			params += "trackSelector="+$F ( 'trackSelector' )+"&";
		}
		if ($ ( 'singerName' ) && $F ( 'singerName' ) != 'null') {
			params += "singerName="+$F ( 'singerName' )+"&";			
		}
	}
	new Ajax.Request ('/playlist', {
		parameters: params,
		onSuccess: renderPlaylist,
		onFailure: handleError,
	});
	//alert("updatePlaylist finish");
}

var searchToggle = function (searchType) {
		//alert(searchType);
		if (searchType == "combined") {
			$ ('trackContainer').style.visibility = 'hidden';
			$ ('artistContainer').style.visibility = 'hidden';
			$ ('combinedContainer').style.visibility = 'visible';	
			$ ('searchToggleCombined').setAttribute("checked","1");	
			//$ ('artistPartial').setAttribute("onkeyup","javascript:updateCombined()");
			$ ('artistPartial').setAttribute("onchange","javascript:updateCombined()");
			updateCombined();
		}
		else {
			$ ('trackContainer').style.visibility = 'visible';
			$ ('artistContainer').style.visibility = 'visible';	
			$ ('combinedContainer').style.visibility = 'hidden';
			$ ('searchToggleArtist').setAttribute("checked","1");
			//$ ('artistPartial').setAttribute("onkeyup","javascript:updateArtists()");
			$ ('artistPartial').setAttribute("onchange","javascript:updateArtists()");
			updateArtists();
		}
}

var karaoke_init = function() {
	updateGenre();
	updateArtists();
	updateTracks();
	updatePlaylist();
	renderSearchToggle();	searchToggle('artist');
	new PeriodicalExecuter(updatePlaylist,5);
}
