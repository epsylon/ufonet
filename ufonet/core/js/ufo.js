/*
UFONet - DDoS Botnet via Web Abuse - 2013/2014/2015 - by psy (epsylon@riseup.net)

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
	    target_icon=L.icon({iconUrl:"/js/leaflet/images/marker-icon.png",
				iconSize: [25, 41],
				iconAnchor: [13, 42],
				popupAnchor: [-3, -76],
				shadowUrl: '/js/leaflet/images/marker-shadow.png',
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
	    zombie_icon=L.icon({iconUrl:"/js/leaflet/images/ufonet-zombie.png",
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
		iconUrl: 'images/markers/marker-icon-'+this.index+'.png',
		iconSize:     [30, 30], // size of the icon
		iconAnchor:   [15, 15], // point of the icon which will correspond to marker's location
		popupAnchor:  [-150, 50] // point from which the popup should open relative to the iconAnchor
	    });
	}
	if (this.index == this.counter_max){
	    var customIcon = new L.icon({
		iconUrl: 'images/markers/marker-icon-last.png',
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
		    error = "<a href='#' onclick='show_error()'> + "+dead_zombies.length+" to be discarded...</a>"
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
    osm_sat = L.tileLayer('http://otile1.mqcdn.com/tiles/1.0.0/sat/{z}/{x}/{y}.png')
    streets = L.tileLayer('http://api.tiles.mapbox.com/v4/mapbox.streets/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoicmxsZmZmIiwiYSI6IkZyVmt4bUUifQ.R--ZDzdb-672Dx1E3suO9A')
    dark = L.tileLayer('http://api.tiles.mapbox.com/v4/mapbox.dark/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoicmxsZmZmIiwiYSI6IkZyVmt4bUUifQ.R--ZDzdb-672Dx1E3suO9A')

    map = L.map('map',{
	minZoom: 2,
	maxZoom: 7,
	zoomControl:false,
	layers: [dark]
    });

    if (typeof latlong !== 'undefined') {
	map.setView(latlong[index], 1)
    }
    else{
	map.setView(new L.LatLng(0,0), 1)
    }
    dark.addTo(map)
    
    var baseMaps = {
	"Light": streets,
        "Dark": dark,
	"Sats": osm_sat,
    }
    
    //  initializing controls:
    new L.control.layers(baseMaps, null, {collapsed:false}).addTo(map)
    
    new L.Control.Zoom({position: 'topright'}).addTo(map)

    map.scrollWheelZoom.disable()

    map.addControl(new UfoControlClass())
    $('.ufo_msg_div').html("<h2 style='text-align:right'>messages <a href=\"#\" id='showMsg'>[+]</a> <a href=\"#\" id='hideMsg'>[-]</a></h2><div id='ufomsg'>locating tombstones...<br/></div><div id='ufomsg_last'>locating tombstones....<br/></div>")
    map.addControl(new UfoTitleClass())
    $(".ufo_title_div").html('<div id="status"><h2><font color="red">Zombies:</font></h2><center><h3><font color="green" size="9px"><b>'+total_zombies+'</b></font></h3></center></div>');
    map.addControl(new UfoErrorClass())
    $('.ufo_error_div').hide()
    map.addControl(new UfoStatClass())
    $('.ufo_stat_div').html("<h2 style='text-align:right'>stats <a href=\"#\" id='showStat'>[+]</a> <a href=\"#\" id='hideStat'>[-]</a></h2><div id='zombie_detail'></div><div id=\"ufostat\"></div>").hide()
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
