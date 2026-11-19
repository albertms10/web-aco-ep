// config map
let config = {
  minZoom: 5,
  maxZoom: 18,
  scrollWheelZoom: false,
};

var mapDOM = document.getElementById("map");
var lat = parseFloat(mapDOM.getAttribute("data-latitud"));
var long = parseFloat(mapDOM.getAttribute("data-longitud"));
var zoom = mapDOM.getAttribute("data-zoom");
if (zoom) {
  zoom = parseFloat(zoom);
} else {
  zoom = 17;
}
var adreca = mapDOM.getAttribute("data-adreca");

const map = new L.Map("map", config).setView([lat, long], zoom);
//map.on('click', function() { map.scrollWheelZoom.enable(); });
//map.on('mouseout', function() { map.scrollWheelZoom.disable(); });

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

// Trobat a ull
L.Icon.Default.prototype.options.iconSize = [20, 30];
L.Icon.Default.prototype.options.iconAnchor = [10, 30];
L.Icon.Default.prototype.options.shadowSize = [25, 30];
L.Icon.Default.prototype.options.shadowAnchor = [10, 30];

var marker = L.marker([lat, long]).addTo(map);
marker.bindPopup(adreca);
