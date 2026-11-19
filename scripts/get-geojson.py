"""
ATENCIÓ: Tot i semblar incongruent, cal utilitzar l'script manage-nuvol.py per baixar tot el que hi ha al núvol abans
d'executar aquest script. Ja que aquest script utilitza els fitxers existents per no tornar a demanar les dades amb
l'API perquè és molt lent.

Aquest script obté la informació geogràfica dels límits territorials (municipis, comarques i províncies) d'Internet. Sap
on trobar-los gràcies a l'etiqueta "relation" de cada entitat geogràfica del fitxer /_data/orgues.yml. Utilitza una API
d'Open Street Maps (OSM). És lent. Molt lent. Per això, guarda les coordenades en local. Cal utilitzar l'script
manage-nuvol.py per pujar les dades al núvol abans de llençar el build de CI.
"""

import json
import os
import logging

import yaml
from OSMPythonTools.overpass import Overpass


overpass = Overpass()

my_log = logging.getLogger('web')
my_log.setLevel(level=logging.INFO)
fh = logging.StreamHandler()
my_log.addHandler(fh)


def fetch_relation_coords(relation):
    rel = overpass.query('rel(%s); (._;>;); out;' % relation)
    all_relations_geojson = rel.relations()[0].geometry()
    return all_relations_geojson


def get_osm_relations():
    """
    Només es baixa les relacions dels servidors d'OSM si no troba el fitxer corresponent al directori de la web, que
    utilitza com a memòria cau. Guarda les dades al directori local de la web.
    """
    with open("_data/orgues.yml", "r") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    for provincia in data['provincies']:
        if 'relation' in provincia and 'relation' != "":
            my_log.debug("Processant " + provincia['link'])
            path = f"assets/geojson/provincies/{provincia['link']}.geojson"
            if os.path.exists(path):
                my_log.debug("El fitxer ja existeix. Continuo.")
            else:
                coordinates = fetch_relation_coords(provincia['relation'])
                json_string = json.dumps(coordinates)
                with open(path, "w") as file:
                    file.writelines(json_string)
        else:
            my_log.error("ERROR: província sense relation! " + provincia['link'])

    print()
    for comarca in data['comarques']:
        if 'relation' in comarca and 'relation' != "":
            my_log.debug("Processant " + comarca['link'])
            path = f"assets/geojson/comarques/{comarca['link']}.geojson"
            if os.path.exists(path):
                my_log.debug("El fitxer ja existeix. Continuo.")
            else:
                coordinates = fetch_relation_coords(comarca['relation'])
                json_string = json.dumps(coordinates)
                with open(path, "w") as file:
                    file.writelines(json_string)
        else:
            my_log.error("ERROR: comarca sense relation! " + comarca['link'])

    print()
    for provincia in data['orgues']:
        for comarca in provincia['comarques']:
            if 'poblacions' in comarca:
                for municipi in comarca['poblacions']:
                    if 'relation' in municipi and 'relation' != "":
                        my_log.debug("Processant " + municipi['link'])
                        path = f"assets/geojson/municipis/{municipi['link']}.geojson"
                        if os.path.exists(path):
                            my_log.debug("El fitxer ja existeix. Continuo.")
                        else:
                            coordinates = fetch_relation_coords(municipi['relation'])
                            json_string = json.dumps(coordinates)
                            with open(path, "w") as file:
                                file.writelines(json_string)
                    else:
                        my_log.error("ERROR: municipi sense relation! " + municipi['link'])


if __name__ == "__main__":
    get_osm_relations()
