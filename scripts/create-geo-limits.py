"""
Calcula les bounding boxes de totes les entitats territorials per centrar-les correctament amb els mapes Leaflet.
"""

import json
import os
import logging

import yaml
from OSMPythonTools.overpass import Overpass

my_log = logging.getLogger('web')
my_log.setLevel(level=logging.INFO)
fh = logging.StreamHandler()
my_log.addHandler(fh)

overpass = Overpass()


def get_limits(geojson):
    top_right_long = -180  # find max
    top_right_lat = -180  # find max
    bottom_left_long = 180  # find min
    bottom_left_lat = 180  # find min

    coordinates = []
    if geojson['type'] == 'Polygon':
        for polygon in geojson['coordinates']:
            coordinates += polygon
    elif geojson['type'] == 'MultiPolygon':
        for polygon in geojson['coordinates']:
            for sub_polygon in polygon:
                coordinates += sub_polygon

    for coordinate in coordinates:
        if coordinate[0] > top_right_long:
            top_right_long = coordinate[0]
        if coordinate[0] < bottom_left_long:
            bottom_left_long = coordinate[0]
        if coordinate[1] > top_right_lat:
            top_right_lat = coordinate[1]
        if coordinate[1] < bottom_left_lat:
            bottom_left_lat = coordinate[1]

    return [top_right_lat, top_right_long, bottom_left_lat, bottom_left_long]


def process_data():
    # read relations from yml
    with open("_data/orgues.yml", "r") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    limits = {'provincies': [], 'comarques': [], 'municipis': []}
    for provincia in data['provincies']:
        if 'relation' in provincia:
            my_log.debug("Processant " + provincia['link'])
            path = f"assets/geojson/provincies/{provincia['link']}.geojson"
            if not os.path.exists(path):
                my_log.error(f"  geojson file does not exist. skipping. File: {path}")
            else:
                with open(path) as file:
                    geojson = json.load(file)
                boundary = get_limits(geojson)
                limits['provincies'].append({'link': provincia['link'], 'limits': boundary})

    for comarca in data['comarques']:
        if 'relation' in comarca:
            my_log.debug("Processant " + comarca['link'])
            path = f"assets/geojson/comarques/{comarca['relation_link'] if 'relation_link' in comarca else comarca['link']}.geojson"
            if not os.path.exists(path):
                my_log.error(f"  geojson file does not exist. skipping. File: {path}")
            else:
                with open(path) as file:
                    geojson = json.load(file)
                boundary = get_limits(geojson)
                limits['comarques'].append({'link': comarca['link'], 'limits': boundary})

    for provincia in data['orgues']:
        for comarca in provincia['comarques']:
            if 'poblacions' in comarca:
                for municipi in comarca['poblacions']:
                    if 'relation' in municipi:
                        my_log.debug("Processant " + municipi['link'])
                        path = f"assets/geojson/municipis/{municipi['link']}.geojson"
                        if not os.path.exists(path):
                            my_log.error(f"  geojson file does not exist. skipping. File: {path}")
                        else:
                            with open(path) as file:
                                geosjon = json.load(file)
                            boundary = get_limits(geosjon)
                            limits['municipis'].append({'link': municipi['link'], 'limits': boundary})

    with open("_data/limits-geografics.yml", "w") as file:
        yaml.dump(limits, file, encoding='utf-8', allow_unicode=True)


if __name__ == "__main__":
    process_data()

