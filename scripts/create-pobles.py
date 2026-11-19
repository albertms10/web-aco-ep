import yaml


def find_provcincia_nom(data, link):
    for provincia in data['provincies']:
        if provincia['link'] == link:
            return provincia['nom']


def find_comarca_nom(data, link):
    for comarca in data['comarques']:
        if comarca['link'] == link:
            return comarca['nom']


def find_bisbat_nom(data, link):
    for bisbat in data['bisbats']:
        if bisbat['link'] == link:
            return bisbat['nom']


def main():
    with open("_data/orgues.yml", "r") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    pobles = []
    edificis = []
    for provincia in data['orgues']:
        for comarca in provincia['comarques']:
            if 'poblacions' in comarca:
                for poble in comarca['poblacions']:
                    pobles.append({
                        'nom': poble['nom'],
                        'de_nom': poble['de_nom'] if 'de_nom' in poble else "de " + poble['nom'],
                        'link': poble['link'],
                        'bisbat': poble['bisbat'] if 'bisbat' in poble else "",
                        'comarca': comarca['link'],
                        'provincia': provincia['link'],
                        'edificis': sorted(poble['edificis'], key=lambda x: x['nom'])
                    })
                    for edifici in poble['edificis']:
                        if ('geolocalitzacio' not in edifici) or ('latitud' not in edifici['geolocalitzacio']) or ('longitud' not in edifici['geolocalitzacio']):
                            print(f"WARNING: {provincia['link']}/{comarca['link']}/{poble['link']}/{edifici['link']}/{orgue['link']} has no geolocation")
                            continue
                        if 'orgues' in edifici:
                            for orgue in edifici['orgues']:
                                edificis.append({
                                    'pageID': f"/orgues/{provincia['link']}/{comarca['link']}/{poble['link']}/{edifici['link']}/{orgue['link']}/",
                                    'de': edifici['de'],
                                    'nomPoble': poble['nom'],
                                    'de_nomPoble': poble['de_nom'] if 'de_nom' in poble else "de " + poble['nom'],
                                    'linkPoble': poble['link'],  # to sort
                                    'nomComarca': find_comarca_nom(data, comarca['link']),
                                    'linkComarca': comarca['link'],
                                    'nomProvincia': find_provcincia_nom(data, provincia['link']),
                                    'linkProvincia': provincia['link'],
                                    'nomEdifici': edifici['nom'],
                                    'linkEdifici': edifici['link'],
                                    'nomOrgue': orgue['nom'],
                                    'de_nomOrgue': orgue['de_nom'],
                                    'latitud': edifici['geolocalitzacio']['latitud'],
                                    'longitud': edifici['geolocalitzacio']['longitud'],
                                    'adreca': edifici['adreca'],
                                    'bisbat': find_bisbat_nom(data, poble['bisbat']),
                                    'civil': edifici['civil'] if 'civil' in edifici else None,
                                    'wip': 'wip' in edifici or 'wip' in orgue
                                })
                        else:
                            edificis.append({
                                'pageID': f"/orgues/{provincia['link']}/{comarca['link']}/{poble['link']}/{edifici['link']}/",
                                'de': edifici['de'],
                                'nomPoble': poble['nom'],
                                'de_nomPoble': poble['de_nom'] if 'de_nom' in poble else "de " + poble['nom'],
                                'linkPoble': poble['link'],  # to sort
                                'nomComarca': find_comarca_nom(data, comarca['link']),
                                'linkComarca': comarca['link'],
                                'nomProvincia': find_provcincia_nom(data, provincia['link']),
                                'linkProvincia': provincia['link'],
                                'nomEdifici': edifici['nom'],
                                'linkEdifici': edifici['link'],
                                'latitud': edifici['geolocalitzacio']['latitud'],
                                'longitud': edifici['geolocalitzacio']['longitud'],
                                'adreca': edifici['adreca'],
                                'bisbat': find_bisbat_nom(data, poble['bisbat']),
                                'civil': edifici['civil'] if 'civil' in edifici else None,
                                'wip': 'wip' in edifici
                            })

    pobles.sort(key=lambda x: x['link'])
    edificis.sort(key=lambda x: x['linkPoble'])

    with open("_data/pobles.yml", "w") as file:
        yaml.dump(pobles, file, encoding='utf-8', allow_unicode=True)
    with open("_data/edificis.yml", "w") as file:
        yaml.dump(edificis, file, encoding='utf-8', allow_unicode=True)


if __name__ == "__main__":
    main()
