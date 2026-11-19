---
---

// config map
let config = {
    minZoom: 5,
    maxZoom: 18,
    zoomSnap: 0.25,
//  scrollWheelZoom: false,
};

/*
 * https://www.idescat.cat/indicadors/?id=aec&n=15178
 *              orient est      occident est    orient nord     occident nord
 * Catalunya 	3° 19' 59,94" 	0° 9' 41,69" 	42° 51' 45,97" 	40° 31' 27,56"
 */
var top_right_corner = L.latLng(42.8625528, 3.328247222222222);
var bottom_left_corner = L.latLng(40.5243222, 0.16158055555555556);
var limits_catalans = L.latLngBounds(top_right_corner, bottom_left_corner);

const map = new L.Map("map", config).setView([0, 0], 0);
map.fitBounds(limits_catalans);
//map.on('click', function() { map.scrollWheelZoom.enable(); });
//map.on('mouseout', function() { map.scrollWheelZoom.disable(); });

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

/*
 * This gets all the elements without taking into account the hierarchy
*/
var markers = document.getElementById('markers');
var items = markers.getElementsByTagName("li");

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

var bisbats_icons = {};
{% for bisbat in site.data.orgues.bisbats %}
    bisbats_icons['{{bisbat.link}}'] = L.icon(Object.assign({}, { iconUrl: "{% link assets/img/markers/{{bisbat.marker}}.png %}"}, iconSettings));
{% endfor %}
var civil = L.icon(Object.assign({}, { iconUrl: "{% link assets/img/markers/gris.png %}"}, iconSettings));


for (var i = 0, len = items.length; i < len; i+=5 ) {
    // bisbat/civil (4)
    if (items[i+4].textContent == "civil") {
        var marker = L.marker(
            // latitud (1), longitud (2)
            [parseFloat(items[i+1].textContent), parseFloat(items[i+2].textContent)],
            { icon: civil }
        ).addTo(map);
    } else {
        var currentIcon = bisbats_icons[items[i+4].textContent];
        var marker = L.marker(
            // latitud (1), longitud (2)
            [parseFloat(items[i+1].textContent), parseFloat(items[i+2].textContent)],
            { icon: currentIcon }
        ).addTo(map);
    }

    // enllaç (3)
    marker.bindPopup(items[i+3].innerHTML);
}

markers.remove();

