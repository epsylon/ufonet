/*
UFONet - Denial of Service Toolkit - 2013/2020 - by psy (epsylon@riseup.net)

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

// this variable defines the delay between each ajax update (statistics and geoip information)
var AJAX_DELAY = 1234

// interface control definitions, managed by leaflet
var UfoControlClass = L.Control.extend({
    options: {
        position: 'bottomright'
    },
    onAdd: function (map) {
        var container = L.DomUtil.create('div', 'ufo_msg_div leaflet-control-layers leaflet-control-layers-expanded')
	L.DomEvent.on(container,'mousedown',L.DomEvent.stopPropagation)
	    .on(container,'doubleclick',L.DomEvent.stopPropagation)
	    .on(container,'click',L.DomEvent.stopPropagation)
	return container;
    }
});

var UfoTitleClass = L.Control.extend({
    options: {
        position: 'topleft'
    },
    onAdd: function (map) {
        var container = L.DomUtil.create('div', 'ufo_title_div leaflet-control-layers leaflet-control-layers-expanded')
        return container;
    }
});

var UfoErrorClass = L.Control.extend({
    options: {
        position: 'bottomleft'
    },
    onAdd: function (map) {
        var container = L.DomUtil.create('div', 'ufo_error_div leaflet-control-layers leaflet-control-layers-expanded')
        return container;
    }
});

var UfoStatClass = L.Control.extend({
    options: {
        position: 'bottomleft'
    },
    onAdd: function (map) {
        var container = L.DomUtil.create('div', 'ufo_stat_div leaflet-control-layers leaflet-control-layers-expanded')
	L.DomEvent.on(container,'mousedown',L.DomEvent.stopPropagation)
	    .on(container,'doubleclick',L.DomEvent.stopPropagation)
	    .on(container,'click',L.DomEvent.stopPropagation)
        return container;
    }
});

// leaflet cluster, regrouping zombies by country
function Cluster(){
    this._clusters=new Array()
    this.add=function(zombie,marker){
	cc=zombie.country_code
	cg=false
	if(cc){
	    cg=this.find(cc)
	    if(cg==false){
		cg=new L.MarkerClusterGroup()
		this._clusters.push({"cc":cc,"z":zombie,"cg":cg})
	    }
	    cg.addLayer(marker)
	    map.addLayer(cg)
	}
    }
    this.find=function(cc){
	for(c in this._clusters){
	    if(this._clusters[c].cc==cc){
		return this._clusters[c].cg
	    }
	}
	return false
    }
}

// Target object
function Doll(name){
    this.name = name
    this.data=false
    this.latlong = false
    this.city = false
    this.country = false
    this.country_code = false
    this.asn = false
    this.ip = false
    this.hostname = false
    this.drawnLayers = new Array()
    this.show=function(){
	    target_icon=L.icon({iconUrl:"data:image/png;base64,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",
				iconSize: [25, 41],
				iconAnchor: [13, 42],
				popupAnchor: [-3, -76],
				shadowUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAApCAYAAACoYAD2AAAC5ElEQVRYw+2YW4/TMBCF45S0S1luXZCABy5CgLQgwf//S4BYBLTdJLax0fFqmB07nnQfEGqkIydpVH85M+NLjPe++dcPc4Q8Qh4hj5D/AaQJx6H/4TMwB0PeBNwU7EGQAmAtsNfAzoZkgIa0ZgLMa4Aj6CxIAsjhjOCoL5z7Glg1JAOkaicgvQBXuncwJAWjksLtBTWZe04CnYRktUGdilALppZBOgHGZcBzL6OClABvMSVIzyBjazOgrvACf1ydC5mguqAVg6RhdkSWQFj2uxfaq/BrIZOLEWgZdALIDvcMcZLD8ZbLC9de4yR1sYMi4G20S4Q/PWeJYxTOZn5zJXANZHIxAd4JWhPIloTJZhzMQduM89WQ3MUVAE/RnhAXpTycqys3NZALOBbB7kFrgLesQl2h45Fcj8L1tTSohUwuxhy8H/Qg6K7gIs+3kkaigQCOcyEXCHN07wyQazhrmIulvKMQAwMcmLNqyCVyMAI+BuxSMeTk3OPikLY2J1uE+VHQk6ANrhds+tNARqBeaGc72cK550FP4WhXmFmcMGhTwAR1ifOe3EvPqIegFmF+C8gVy0OfAaWQPMR7gF1OQKqGoBjq90HPMP01BUjPOqGFksC4emE48tWQAH0YmvOgF3DST6xieJgHAWxPAHMuNhrImIdvoNOKNWIOcE+UXE0pYAnkX6uhWsgVXDxHdTfCmrEEmMB2zMFimLVOtiiajxiGWrbU52EeCdyOwPEQD8LqyPH9Ti2kgYMf4OhSKB7qYILbBv3CuVTJ11Y80oaseiMWOONc/Y7kJYe0xL2f0BaiFTxknHO5HaMGMublKwxFGzYdWsBF174H/QDknhTHmHHN39iWFnkZx8lPyM8WHfYELmlLKtgWNmFNzQcC1b47gJ4hL19i7o65dhH0Negbca8vONZoP7doIeOC9zXm8RjuL0Gf4d4OYaU5ljo3GYiqzrWQHfJxA6ALhDpVKv9qYeZA8eM3EhfPSCmpuD0AAAAASUVORK5CYII=',
				shadowSize: [68, 95],
				shadowAnchor: [22, 94]
			       })
	var marker = L.marker(this.latlong,{icon: target_icon})
	var popup = L.Popup({
	    maxHeight: 50})
	var popupcontent = "<b>"+this.name+"</b>"
	    +"<br />-------------<br />"        
	    +"Localisation: "+this.city+"/"+this.country
	    +"<br/>"
	    +"IP: "+this.ip+"<br/>"
	    +"Hostname: "+this.hostname+"<br/>"
	    +"ASN: "+this.asn+"<br/>"
	marker.bindPopup(popupcontent)
	this.drawnLayers.push(marker)
	map.addLayer(marker)
    }
    this.setData = function(data){
	this.data=data
	this.latlong = data[0]
	this.city = data[1]
	this.country = data[2]
	this.country_code = data[3]
	this.asn = data[4]
	this.ip = data[5]
	this.hostname = data[6]
    }
}

// object for each zombie
function zombieEntry(name,data){
    this.data=data
    this.name = name
    this.latlong = data[0]
    this.city = data[1]
    this.country = data[2]
    this.country_code = data[3]
    this.asn = data[4]
    this.ip = data[5]
    this.hostname = data[6]
    this.drawnLayers = new Array()
    this.index=0
    this.state='awakening'
    this.speed= 1000 // animation speed in ms
    this.cluster = false
    this.show=function(){
	if(this.state==='awakening'){
	    this.state='awake'
	    this.stop_anim=false
	    this.drawMarker()
	}
    }
    this.drawMarker=function(){
	if(!zombie_icon)
	    zombie_icon=L.icon({iconUrl:"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAPCAYAAADtc08vAAABn0lEQVQoz4WSPUiVYRTHf3+9+PqxNERlQYOFRQbdQWwQJx2C4N4lgqYiUNwbozGCIEhqUBCSuwRFS4uTUxI01BAUhkkFLUESJYp/KU/LEV5ernXggfPxnN85zzmPaCOWHgCngC2gG/gGTBUR5l9iqdfSiqWhiv9Y+vv/B3hlqc/SIUtzabcsDWT8XTVHpeQ6cAlYAFbb8MeAk8BGEfGsXfXblo5aWrMUbc5W3ntczuso6YeBHmAAoDNY7gqudwZPM95jaRA4uB/gEzCa+r1axE1FnKtFzAFX0z8CDFn6nV1Nd1hasjQDzAPjefE0sAt8ATaBi+kfBvqBO0C9iJjF0llLke97Yum1pdhBPwPd30HrWW3F0nNLPyw1y8M7sgdI++U+Q1zN+IKlVhkwYWm3spFrleQbpdgVS9/37BrwEZClbaAAPgAblS2fKOkjwK+EDctSH9AEjifsQuprwDTwHjhTATaAr8AbWTLQBfwBZrKDA8AtYCnhDeBydjKbhR4B67I0VkS8sHQXOA/05grfFhGTlh4mZBP4nB+pDiwCjb/iorRmvUZYHQAAAABJRU5ErkJggg==",
				iconSize: [16, 15],
				iconAnchor: [8, 8],
				popupAnchor: [-3, -76]
			       })
	var marker = L.marker(this.latlong,{icon:zombie_icon}) //,{icon: this.makeCustomMarker()})
	var popup = L.Popup({
	    maxHeight: 50})
	var popupcontent = "<b>"+this.name+"</b>"
            +"<br />-------------<br />"        
            +"Localisation: "+this.city+"/"+this.country+"<br/>"
            +"IP: "+this.ip+"<br/>"
            +"Hostname: "+this.hostname+"<br/>"
            +"ASN: "+this.asn+"<br/>"
	marker.bindPopup(popupcontent)
	cluster.add(this,marker)
	this.drawnLayers.push(marker)
	this.fire()
    }
    this.fire = function(){
	if(doll){
	    var src = this.latlong
	    var dest = doll.latlong
	    var b = new R.BezierAnim([src, dest])
	    map.addLayer(b)
	    this.drawnLayers.push(b)
	}
    }
    this.makeCustomMarker= function(){
	if (this.index < this.counter_max){
	    var customIcon = new L.icon({
		iconUrl: 'data:image/png;base64,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',
		iconSize:     [30, 30], // size of the icon
		iconAnchor:   [15, 15], // point of the icon which will correspond to marker's location
		popupAnchor:  [-150, 50] // point from which the popup should open relative to the iconAnchor
	    });
	}
	if (this.index == this.counter_max){
	    var customIcon = new L.icon({
		iconUrl: 'data:image/png;base64,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',
		iconSize:     [30, 30], // size of the icon
		iconAnchor:   [15, 15], // point of the icon which will correspond to marker's location
		popupAnchor:  [-150, 0] // point from which the popup should open relative to the iconAnchor
	    });
	}
	return customIcon
    }
    this.makeClusterGroups=function(country_code_list){
	for (var i = 0; i < this.unique_country_code_list.length; i++){
	    if (this.unique_country_code_list[i] == this.country_code_list[this.index]){
		if (this.clusterGroups[this.unique_country_code_list[i]]){
		    //checks if a cluster for the country already exists
		    return
		}
		else
		    //if not make it.
		    this.clusterGroups[this.unique_country_code_list[i]] = new L.MarkerClusterGroup();
	    }
	}
    }
    this.AddMarkerCluster=  function(marker){
	this.clusterGroups[this.country_code_list[this.index]].addLayer(marker)
	map.addLayer(this.clusterGroups[this.country_code_list[this.index]])
	this.drawnLayers.push(this.clusterGroups[this.country_code_list[this.index]])
    }
    this.AddMarker=function(src){
	var marker = L.marker([src[0], src[1]],{icon: this.makeCustomMarker()})
	this.drawnLayers.push(marker)
    }
    this.hide=function() {
	$('.header').hide()
	this.index =0
	    this.state='awakening'
	    this.stop_anim=true
	    for (i in this.drawnLayers){
		if(map.hasLayer(this.drawnLayers[i]))
		    map.removeLayer(this.drawnLayers[i])
	    }
	    this.drawnLayers=new Array()
	}
}

// List of zombies
function  Herd(){
    this.zombieEntries = new Array
    this.find=function (name){
	for (z in this.zombieEntries){
	    if (this.zombieEntries[z].name === name){
		return this.zombieEntries[z]
	    }
	}
	return false;
    }
    this.load=function(name){
	e=this.find(name)
	if(e){
	    e.show()
	    return
	}
	return false
    }
    this.hideAll = function(){
	for (ufoe in this.zombieEntries)
	    this.zombieEntries[ufoe].hide()
	this.render()
    }
    this.hide = function(name){
	var ufoe=this.find(name)
	if(!ufoe) return
	ufoe.hide()
	this.render()
    }
    this.remove = function(name){
	for (z in this.zombieEntries){
	    if(this.zombieEntries[z].name === name){
		this.zombieEntries[z].hide()
		this.zombieEntries.splice(z,1)
		this.render()
		return
	    }
	}
    }
    this.add = function(name,data){
	var ufoe=this.find(name)
	if(!ufoe){
	    ufoe=new zombieEntry(name,data)
	    this.zombieEntries.push(ufoe)
	}
	ufoe.show()
	return ufoe
    }
    this.stop=function() {
	for(i=0;i<this.zombieEntries.length;i++) {
	    this.zombieEntries[i].stop();
	}  
	this.render()
    }
    this.count=function(){
	return this.zombieEntries.length
    }
}

// jquery shortcuts
function ufomsg(msg){
    if ($('#ufomsg').html().indexOf(msg) == -1){
	$('#ufomsg').append(msg+"<br/>\n")
	$('#ufomsg_last').html(msg)
    }
}

function show_error(){
    $(".ufo_error_div").toggle()
}

function zombie_detail(data=''){
    t=''
    if (data!=''){
	t+="<h2>Zombie: <i>"+data.name+"</i> <a href='#' onclick='zombie_detail()'>X</a></h2>"
	t+=data.hits+" hits / "+data.retries+" retries / "+data.fails+" fails <br/>"
	t+=data.min_time+" min time / "+data.avg_time+" average time / "+data.max_time+" max time <br/>"
	t+=data.min_size+" min size / "+data.avg_size+" average size / "+data.max_size+" max size <br/>"
    }
    $('#zombie_detail').html(t)
}

// watchdog function
function ufowatch(){
    // if attack mode we have a doll, and do a check if herd is done and bail if so
    // if herd is not done, get stats
    if(doll && !hdone){
	d = new Date()
	$("#ufostat").load("/js/ajax.js?stats="+d.getTime()).show()
    }
    // load doll geoip data
    if(doll && !doll.data)
	$(".ufo_error_div").load("/js/ajax.js?fetchdoll="+doll.name)
    // bail if all zombies are done in view mode
    if (zdone) 
	return
    // we are not finished loading zombie geoip data, let's start...
    d=new Date
    var lw=d.getTime()
    error=''
    // basic check to prevent overload - relies on AJAX_DELAY variable
    if(last_watch < lw - AJAX_DELAY){
	last_watch=lw
	// loading next zombie
	$(".ufo_error_div").load('/js/ajax.js?zombie='+btoa(unescape(encodeURIComponent(last_zombie))))
	label=Zombies.count()+"/"+total_zombies
	if (Zombies.count()== total_zombies)
	    label = total_zombies
	else
	    if (Zombies.count() +dead_zombies.length== total_zombies){
		label=total_zombies
		if(dead_zombies.length>0){
		    label=total_zombies -dead_zombies.length
		    $('.ufo_error_div').html('<div id="ufo_error_div">To be discarded : <br/><ul>'
					     +dead_zombies.join("<li> -")+'</ul></div>')
		    error = "<a href='#' onclick='show_error()'> + "+dead_zombies.length+" not listed...</a>"
		}
	    }
	$(".ufo_title_div").html('<div id="status"><center><h2><font color="red">Zombies:</font></h2><h3><font color="green" size="9px"><b>'+label+'</b></font></h3>'+error+'</center></div>');
    }
}

// (leaflet) map initialization
function initMap (targetdoll=false) {
    if(map){
	return
    }
    if(targetdoll){
	doll=targetdoll
    }
    index = 0
    osm_sat = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
    map = L.map('map',{
	minZoom: 2,
	maxZoom: 7,
	zoomControl:false,
	layers: [osm_sat]
    });
    if (typeof latlong !== 'undefined') {
	map.setView(latlong[index], 1)
    }
    else{
	map.setView(new L.LatLng(0,0), 1)
    }
    osm_sat.addTo(map)
    var baseMaps = {
	"Sats": osm_sat,
    }
    //  initializing controls:
    new L.control.layers(baseMaps, null, {collapsed:false}).addTo(map)
    new L.Control.Zoom({position: 'topright'}).addTo(map)
    map.scrollWheelZoom.disable()
    map.addControl(new UfoControlClass())
    $('.ufo_msg_div').html("<h2 style='text-align:right'>Map Console <a href=\"#\" id='showMsg'>[+]</a> <a href=\"#\" id='hideMsg'>[-]</a></h2><div id='ufomsg'>[Info] [AI] [Control] Locating zombies... -> [Waiting!]<br/><br/></div><div id='ufomsg_last'>[Info] [AI] [Control] Locating zombies.... -> [Waiting!]<br/></div>")
    map.addControl(new UfoTitleClass())
    $(".ufo_title_div").html('<div id="status"><h2><font color="red">Zombies:</font></h2><center><h3><font color="green" size="9px"><b>'+total_zombies+'</b></font></h3></center></div>');
    map.addControl(new UfoErrorClass())
    $('.ufo_error_div').hide()
    map.addControl(new UfoStatClass())
    $('.ufo_stat_div').html("<h2 style='text-align:right'>Last Statistics <a href=\"#\" id='showStat'>[+]</a> <a href=\"#\" id='hideStat'>[-]</a></h2><div id='zombie_detail'></div><div id=\"ufostat\"></div>").hide()
    $('a#showStat').hide()
    $('a#showStat').click(function(){
	$('a#showStat').hide()
	$('a#hideStat').show()
	$('#ufostat').show()
    })
    $('a#hideStat').click(function(){
	$('a#hideStat').hide()
	$('a#showStat').show()
	$('#ufostat').hide()
    })
    $('a#hideMsg').hide()
    $('#ufomsg').hide()
    $('a#showMsg').click(function(){
	$('a#showMsg').hide()
	$('a#hideMsg').show()
	$('#ufomsg').show()
	$('#ufomsg_last').hide()
    })
    $('a#hideMsg').click(function(){
	$('a#hideMsg').hide()
	$('a#showMsg').show()
	$('#ufomsg').hide()
	$('#ufomsg_last').show()
    })
    // starting watchdog ajax request
    window.setInterval("ufowatch()",AJAX_DELAY)
}
// global variables
var Zombies = new Herd()
var cluster = new Cluster()
var map = false
var last_zombie = 'None'
var zombie_icon = false
d=new Date
var last_watch = d.getTime()
var target_icon = false
var doll = false
var dead_zombies = new Array()
var errdiv = false
var hdone = false
var zdone = false
var total_zombies=false
