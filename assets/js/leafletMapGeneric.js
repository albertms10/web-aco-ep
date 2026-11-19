---
---

// config map
let config = {
  minZoom: 5,
  maxZoom: 18,
  zoomSnap: 0.25
//  scrollWheelZoom: false,
};

var mapDOM = document.getElementById('map');
var top_right_corner = L.latLng(
    parseFloat(mapDOM.getAttribute('data-top-right-lat')),
    parseFloat(mapDOM.getAttribute('data-top-right-long')));
var bottom_left_corner = L.latLng(
    parseFloat(mapDOM.getAttribute('data-bottom-left-lat')),
    parseFloat(mapDOM.getAttribute('data-bottom-left-long')));
var limits = L.latLngBounds(top_right_corner, bottom_left_corner);

const map = new L.Map("map", config).setView([0, 0], 0);
map.fitBounds(limits);


L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

var data = document.querySelectorAll(".orgues-ul [data-adreca]");

var width = 25;
var height = 41;
var iconSettings = {
    shadowUrl: '{% link assets/img/markers/shadow.png %}',
    iconSize:     [width, height], // size of the icon
    shadowSize:   [height, height], // size of the shadow
    iconAnchor:   [width/2, height], // point of the icon which will correspond to marker's location
    shadowAnchor: [width/2, height],  // the same for the shadow
    popupAnchor:  [0, -height-8] // point from which the popup should open relative to the iconAnchor
}

icons = {};
icons['active'] = L.icon(Object.assign({}, { iconUrl: "{% link assets/img/markers/blau-clar.png %}"}, iconSettings));
icons['inactive'] = L.icon(Object.assign({}, { iconUrl: "{% link assets/img/markers/vermell.png %}"}, iconSettings));

var markers = [];
for (let i = 0, len = data.length; i < len; i++) {
    if (data[i].hasAttribute("data-latitud") && data[i].hasAttribute("data-longitud") && data[i].hasAttribute("data-html")) {
        // els enllaços d'orgues que estan en edificis amb més d'un orgue no tenen dades de localització; les té l'edifici que els conté
        let marker = L.marker(
            [data[i].getAttribute("data-latitud"), data[i].getAttribute("data-longitud")],
            {icon: icons['inactive'] }
        ).addTo(map);
        marker.bindPopup(data[i].getAttribute("data-html"));
        data[i].addEventListener("mouseover", (event) => {
          marker.setIcon(icons['active']);
        });
        data[i].addEventListener("mouseleave", (event) => {
          marker.setIcon(icons['inactive']);
        });
        markers.push(marker);
    }
}

var geojson = mapDOM.getAttribute('data-geojson');

if (geojson != "") {
    fetch(geojson).then(response => response.json()).then(json => {
        L.geoJSON(json, {
            style: function(geoJsonFeature) {
                return {fill: false}
            }
        }).addTo(map);
    });

}
