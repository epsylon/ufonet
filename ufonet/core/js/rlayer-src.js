/*
 RaphaelLayer, a JavaScript library for overlaying Raphael objects onto Leaflet interactive maps. http://dynmeth.github.com/RaphaelLayer
 (c) 2012-2013, David Howell, Dynamic Methods Pty Ltd

 Version 0.1.3
*/

(function() {

var R, originalR;

if (typeof exports != 'undefined') {
	R = exports;
} else {
	R = {};

	originalR = window.R;

	R.noConflict = function() {
		window.R = originalR;
		return R;
	};

	window.R = R;
}

R.version = '0.1.3';

R.Layer = L.Class.extend({
	includes: L.Mixin.Events,
	
	initialize: function(options) {
		
	},

	onAdd: function (map) {
		this._map = map;
		this._map._initRaphaelRoot();
		this._paper = this._map._paper;
		this._set = this._paper.set();
		
		map.on('viewreset', this.projectLatLngs, this);
		this.projectLatLngs();
	},

	onRemove: function(map) {
		map.off('viewreset', this.projectLatLngs, this);
		this._map = null;
		this._set.forEach(function(item) {
			item.remove();
		}, this);
		this._set.clear();
	},

	projectLatLngs: function() {
		
	},

	animate: function(attr, ms, easing, callback) {
		this._set.animate(attr, ms, easing, callback);
	
		return this;
	},

	hover: function(f_in, f_out, icontext, ocontext) {
		this._set.hover(f_in, f_out, icontext, ocontext);

		return this;
	},

	attr: function(name, value) {
		this._set.attr(name, value);

		return this;
	}
});

L.Map.include({
	_initRaphaelRoot: function () {
		if (!this._raphaelRoot) {
			this._raphaelRoot = this._panes.overlayPane;
			this._paper = Raphael(this._raphaelRoot);

			this.on('moveend', this._updateRaphaelViewport);
			this._updateRaphaelViewport();
		}
	},

	_updateRaphaelViewport: function () {
		var	p = 0.02,
			size = this.getSize(),
			panePos = L.DomUtil.getPosition(this._mapPane),
			min = panePos.multiplyBy(-1)._subtract(size.multiplyBy(p)),
			max = min.add(size.multiplyBy(1 + p*2)),
			width = max.x - min.x,
			height = max.y - min.y,
			root = this._raphaelRoot,
			pane = this._panes.overlayPane;

		this._paper.setSize(width, height);
		
		L.DomUtil.setPosition(root, min);

		root.setAttribute('width', width);
		root.setAttribute('height', height);
		
		this._paper.setViewBox(min.x, min.y, width, height, false);
		
	}
});

R.Marker = R.Layer.extend({
	initialize: function(latlng, pathString, attr, options) {
		R.Layer.prototype.initialize.call(this, options);

		this._latlng = latlng;
		this._pathString = (typeof pathString == 'string' ? pathString : 'M16,3.5c-4.142,0-7.5,3.358-7.5,7.5c0,4.143,7.5,18.121,7.5,18.121S23.5,15.143,23.5,11C23.5,6.858,20.143,3.5,16,3.5z M16,14.584c-1.979,0-3.584-1.604-3.584-3.584S14.021,7.416,16,7.416S19.584,9.021,19.584,11S17.979,14.584,16,14.584z');
		this._attr = (typeof pathString == 'object' ? pathString : (attr ? attr : {'fill': '#000'}));
	},

	projectLatLngs: function() {		
		if (this._path) this._path.remove();

		var p = this._map.latLngToLayerPoint(this._latlng);
		var r = Raphael.pathBBox(this._pathString);
		
		this._path = this._paper.path(this._pathString)
			.attr(this._attr)
			.translate(p.x - 1.05*r.width, p.y - 1.15*r.height)
			.toFront();

		this._set.push(this._path);
	}
});

R.Pulse = R.Layer.extend({
	initialize: function(latlng, radius, attr, pulseAttr, options) {
		R.Layer.prototype.initialize.call(this, options);

		this._latlng = latlng;
		this._radius = (typeof radius == 'number' ? radius : 6);
		this._attr = (typeof radius == 'object' ? radius : (typeof attr == 'object' ? attr : {'fill': '#30a3ec', 'stroke': '#30a3ec'}));
		this._pulseAttr = (typeof radius == 'object' ? attr : typeof pulseAttr == 'object' ? pulseAttr : {
			'stroke-width': 3,
			'stroke': this._attr.stroke
		});
		this._repeat = 3;
	},

	onRemove: function (map) {
		R.Layer.prototype.onRemove.call(this, map);

		if(this._marker) this._marker.remove();		
		if(this._pulse) this._pulse.remove();
	},

	projectLatLngs: function() {
		if(this._marker) this._marker.remove();
		if(this._pulse) this._pulse.remove();

		var p = this._map.latLngToLayerPoint(this._latlng);

		this._marker = this._paper.circle(p.x, p.y, this._radius).attr(this._attr);
		this._pulse = this._paper.circle(p.x, p.y, this._radius).attr(this._pulseAttr);

		var anim = Raphael.animation({
						'0%': {transform: 's0.3', opacity: 1.0},
						'100%': {transform: 's3.0', opacity: 0.0, easing: '<'}
					}, 1000);

		this._pulse.animate(anim.repeat(this._repeat));
	}
});

R.Polyline = R.Layer.extend({
	
	initialize: function(latlngs, attr, options) {
		R.Layer.prototype.initialize.call(this, options);

		this._latlngs = latlngs;
		this._attr = attr || {'fill': '#000', 'stroke': '#000'};
	},

	projectLatLngs: function() {
		this._set.clear();	
		if (this._path) this._path.remove();
		
		this._path = this._paper.path(this.getPathString())
			.attr(this._attr)
			.toBack();

		this._set.push(this._path);
	},

	getPathString: function() {
		for(var i=0, len=this._latlngs.length, str=''; i<len; i++) {
			var p = this._map.latLngToLayerPoint(this._latlngs[i]);
			str += (i ? 'L' : 'M') + p.x + ' ' + p.y;
		}
		return str;
	}
});

R.Polygon = R.Layer.extend({
	
	initialize: function(latlngs, attr, options) {
		R.Layer.prototype.initialize.call(this, options);

		if(latlngs.length == 1) {
			if(latlngs[0] instanceof Array) {
				latlngs = latlngs[0];
			}
		}

		this._latlngs = latlngs;
		this._attr = attr || {'fill': 'rgba(255, 0, 0, 0.5)', 'stroke': '#f00', 'stroke-width': 2};
	},

	projectLatLngs: function() {
		if (this._path) this._path.remove();
		
		this._path = this._paper.path(this.getPathString())
			.attr(this._attr)
			.toBack();

		this._set.push(this._path);
	},

	getPathString: function() {
		for(var i=0, len=this._latlngs.length, str=''; i<len; i++) {
			var p = this._map.latLngToLayerPoint(this._latlngs[i]);
			str += (i ? 'L' : 'M') + p.x + ' ' + p.y;
		}
		str += 'Z';

		return str;
	}
});

R.PolygonGlow = R.Layer.extend({
	initialize: function(latlngs, attr, options) {
		R.Layer.prototype.initialize.call(this, options);

		this._latlngs = latlngs;
		this._attr = attr || {'fill': 'rgba(255, 0, 0, 1)', 'stroke': '#f00', 'stroke-width': 3};
	},

	onRemove: function(map) {
		R.Layer.prototype.onRemove.call(this, map);
		
		if(this._path) this._path.remove();
	},

	projectLatLngs: function() {	
		if (this._path) this._path.remove();
		
		this._path = this._paper.path(this.getPathString())
			.attr(this._attr)
			.toBack();

		var p = this._path;

		var fadeIn = function() {
			p.animate({
				'fill-opacity': 0.25
			}, 1000, '<', fadeOut);
		};

		var fadeOut = function() {
			p.animate({
				'fill-opacity': 1
			}, 1000, '<', fadeIn);
		};

		fadeOut();
	},

	getPathString: function() {
		for(var i=0, len=this._latlngs.length, str=''; i<len; i++) {
			var p = this._map.latLngToLayerPoint(this._latlngs[i]);
			str += (i ? 'L' : 'M') + p.x + ' ' + p.y;
		}
		str += 'Z';

		return str;
	}
});

R.Bezier = R.Layer.extend({
	initialize: function(latlngs, attr, options) {
		R.Layer.prototype.initialize.call(this, options);

		this._latlngs = latlngs;
		this._attr = attr;
	},

	projectLatLngs: function() {
		if(this._path) this._path.remove();
		
		var start = this._map.latLngToLayerPoint(this._latlngs[0]),
			end = this._map.latLngToLayerPoint(this._latlngs[1]),
			cp = this.getControlPoint(start, end);

		this._path = this._paper.path('M' + start.x + ' ' + start.y + 'Q' + cp.x + ' ' + cp.y + ' ' + end.x + ' ' + end.y)
			.attr(this._attr)
			.toBack();

		this._set.push(this._path);
	},

	getControlPoint: function(start, end) {
		var cp = { x: 0, y: 0 };
		cp.x = start.x + (end.x - [start.x]) / 2;
		cp.y = start.y + (end.y - [start.y]) / 2;
		var amp = 0;

		if (this.closeTo(start.x, end.x) && !this.closeTo(start.y, end.y)) {
			amp = (start.x - end.x) * 1 + 15 * (start.x >= end.x ? 1 : -1);
			cp.x = Math.max(start.x, end.x) + amp;
		} else {
			amp = (end.y - start.y) * 1.5 + 15 * (start.y < end.y ? 1 : -1);
			cp.y = Math.min(start.y, end.y) + amp;
		}
		return cp;
	},

	closeTo: function(a, b) {
		var t = 15;
  		return (a - b > -t && a - b < t);
	}
});

R.BezierAnim = R.Layer.extend({
	initialize: function(latlngs, attr, cb, options) {
		R.Layer.prototype.initialize.call(this, options);

		this._latlngs = latlngs;
		this._attr = attr;
		this._cb = cb;
	},

	onRemove: function (map) {
		R.Layer.prototype.onRemove.call(this, map);
		
		if(this._path) this._path.remove();
		if(this._sub) this._sub.remove();
	},

	projectLatLngs: function() {
		if(this._path) this._path.remove();
		if(this._sub) this._sub.remove();
		
		var self = this,
			start = this._map.latLngToLayerPoint(this._latlngs[0]),
			end = this._map.latLngToLayerPoint(this._latlngs[1]),
			cp = this.getControlPoint(start, end),
			pathString="M"+start.x+" "+start.y+" L"+end.x+" "+end.y,
			line = this._paper.path(pathString).hide();

		this._paper.customAttributes.alongBezier = function(a) {
			var r = this.data('reverse');
			var len = this.data('pathLength');

			return {
				path: this.data('bezierPath').getSubpath(r ? (1-a)*len : 0, r ? len : a*len)
			};
		};

		var sub = this._sub = this._paper.path()
			.data('bezierPath', line)
			.data('pathLength', line.getTotalLength())
			.data('reverse', false)
			.attr({
				'stroke': '#BE1E2D',
				'alongBezier': 0,
				'stroke-width': 2
			});

		sub.stop().animate({
			alongBezier: 1
		}, 2000, function() {
			//self._cb();
			sub.data('reverse', true);
			// sub.stop().animate({
			// 	'alongBezier': 0
			// }, 500, function() { sub.remove(); });
		});
	},

	getControlPoint: function(start, end) {
		var cp = { x: 0, y: 0 };
		cp.x = start.x + (end.x - [start.x]) / 2;
		cp.y = start.y + (end.y - [start.y]) / 2;
		var amp = 0;

		if (this.closeTo(start.x, end.x) && !this.closeTo(start.y, end.y)) {
			amp = (start.x - end.x) * 1 + 15 * (start.x >= end.x ? 1 : -1);
			cp.x = Math.max(start.x, end.x) + amp;
		} else {
			amp = (end.y - start.y) * 1.5 + 15 * (start.y < end.y ? 1 : -1);
			cp.y = Math.min(start.y, end.y) + amp;
		}
		return cp;
	},

	closeTo: function(a, b) {
		var t = 15;
  		return (a - b > -t && a - b < t);
	}
});

R.FeatureGroup = L.FeatureGroup.extend({
	initialize: function(layers, options) {
		L.FeatureGroup.prototype.initialize.call(this, layers, options);
	},

	animate: function(attr, ms, easing, callback) {
		this.eachLayer(function(layer) {
			layer.animate(attr, ms, easing, callback);
		});
	},

	onAdd: function(map) {
		L.FeatureGroup.prototype.onAdd.call(this,map);

		this._set = this._map._paper.set();

		for(i in this._layers) {
			this._set.push(this._layers[i]._set);
		}
	},

	hover: function(h_in, h_out, c_in, c_out) {
		this.eachLayer(function(layer) {
			layer.hover(h_in, h_out, c_in, c_out);
		});

		return this;
	},

	attr: function(name, value) {
		this.eachLayer(function(layer) {
			layer.attr(name, value);
		});
		
		return this;
	}
});

/*
 * Contains L.MultiPolyline and L.MultiPolygon layers.
 */

(function () {
	function createMulti(Klass) {
		return R.FeatureGroup.extend({
			initialize: function (latlngs, options) {
				this._layers = {};
				this._options = options;
				this.setLatLngs(latlngs);
			},

			setLatLngs: function (latlngs) {
				var i = 0, len = latlngs.length;

				this.eachLayer(function (layer) {
					if (i < len) {
						layer.setLatLngs(latlngs[i++]);
					} else {
						this.removeLayer(layer);
					}
				}, this);

				while (i < len) {
					this.addLayer(new Klass(latlngs[i++], this._options));
				}

				return this;
			}
		});
	}

	R.MultiPolyline = createMulti(R.Polyline);
	R.MultiPolygon = createMulti(R.Polygon);
}());

R.GeoJSON = R.FeatureGroup.extend({
	initialize: function (geojson, options) {
		L.Util.setOptions(this, options);

		this._geojson = geojson;
		this._layers = {};
		
		if (geojson) {
			this.addGeoJSON(geojson);
		}
	},

	addGeoJSON: function (geojson) {
		var features = geojson.features,
		    i, len;

		if (features) {
			for (i = 0, len = features.length; i < len; i++) {
				this.addGeoJSON(features[i]);
			}
			return;
		}

		var isFeature = (geojson.type === 'Feature'),
		    geometry = isFeature ? geojson.geometry : geojson,
		    layer = R.GeoJSON.geometryToLayer(geometry, this.options.pointToLayer);

		this.fire('featureparse', {
			layer: layer,
			properties: geojson.properties,
			geometryType: geometry.type,
			bbox: geojson.bbox,
			id: geojson.id,
			geometry: geojson.geometry
		});

		this.addLayer(layer);
	}
});

L.Util.extend(R.GeoJSON, {
	geometryToLayer: function (geometry, pointToLayer) {
		var coords = geometry.coordinates,
		    layers = [],
		    latlng, latlngs, i, len, layer;

		switch (geometry.type) {
		case 'Point':
			latlng = this.coordsToLatLng(coords);
			return pointToLayer ? pointToLayer(latlng) : new R.Marker(latlng);

		case 'MultiPoint':
			for (i = 0, len = coords.length; i < len; i++) {
				latlng = this.coordsToLatLng(coords[i]);
				layer = pointToLayer ? pointToLayer(latlng) : new R.Marker(latlng);
				layers.push(layer);
			}
			return new R.FeatureGroup(layers);

		case 'LineString':
			latlngs = this.coordsToLatLngs(coords);
			return new R.Polyline(latlngs);

		case 'Polygon':
			latlngs = this.coordsToLatLngs(coords, 1);
			return new R.Polygon(latlngs);

		case 'MultiLineString':
			latlngs = this.coordsToLatLngs(coords, 1);
			return new R.MultiPolyline(latlngs);

		case "MultiPolygon":
			latlngs = this.coordsToLatLngs(coords, 2);
			return new R.MultiPolygon(latlngs);

		case "GeometryCollection":
			for (i = 0, len = geometry.geometries.length; i < len; i++) {
				layer = this.geometryToLayer(geometry.geometries[i], pointToLayer);
				layers.push(layer);
			}
			return new R.FeatureGroup(layers);

		default:
			throw new Error('Invalid GeoJSON object.');
		}
	},

	coordsToLatLng: function (coords, reverse) { // (Array, Boolean) -> LatLng
		var lat = parseFloat(coords[reverse ? 0 : 1]),
		    lng = parseFloat(coords[reverse ? 1 : 0]);

		return new L.LatLng(lat, lng, true);
	},

	coordsToLatLngs: function (coords, levelsDeep, reverse) { // (Array, Number, Boolean) -> Array
		var latlng,
		    latlngs = [],
		    i, len;

		for (i = 0, len = coords.length; i < len; i++) {
			latlng = levelsDeep ?
					this.coordsToLatLngs(coords[i], levelsDeep - 1, reverse) :
					this.coordsToLatLng(coords[i], reverse);
			latlngs.push(latlng);
		}

		return latlngs;
	}
});



}());