import yaml
import frontmatter
import os


class OrguesCounter:
    def __init__(self):
        self.orgues_inventariats = 0
        self.orgues_coneguts = 0
        self.orgues_totals = 0
        self.fotos = 0  # total de fotos
        self.foto = [0, 0]  # amb, sense
        self.no_foto = []

        self.teclats = 0
        self.pedalers = 0
        self.registres = 0  # que no jocs. Tiradors, entrades a la bd
        self.registres_pedal = 0

        # història
        self.no_constructor = []

        # tècnica
        self.no_diapaso = []
        self.no_temperament = []
        self.no_estat = []
        self.no_emplacament = []
        self.no_transmissio = []

        # disposició
        self.no_composicio = []

    def compute(self):
        with open("_data/orgues.yml", "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        for provincia in data['orgues']:
            for comarca in provincia['comarques']:
                if 'poblacions' not in comarca:
                    continue
                for poble in comarca['poblacions']:
                    for edifici in poble['edificis']:
                        if 'wip' in edifici:
                            self.orgues_coneguts += 1
                            continue
                        if 'orgues' in edifici:
                            for orgue in edifici['orgues']:
                                if 'wip' in orgue:
                                    self.orgues_coneguts += 1
                                    continue
                                core_path = os.path.join(provincia['link'], comarca['link'], poble['link'], edifici['link'], orgue['link'])
                                self.__count(core_path)
                        else:
                            core_path = os.path.join(provincia['link'], comarca['link'], poble['link'], edifici['link'])
                            self.__count(core_path)

    def write(self):
        comptadors = {
            'orgues-inventariats': self.orgues_inventariats,
            'orgues-coneguts': self.orgues_coneguts,
            'total-orgues': self.orgues_inventariats + self.orgues_coneguts,
            'orgues-amb-foto': self.foto[0],
            'orgues-sense-foto': {'count': len(self.no_foto), 'orgues': self.no_foto},
            'no_emplacament': {'count': len(self.no_emplacament), 'orgues': self.no_emplacament},
            'no_transmissio': {'count': len(self.no_transmissio), 'orgues': self.no_transmissio},
            'no_diapaso': {'count': len(self.no_diapaso), 'orgues': self.no_diapaso},
            'no_composicio': {'count': len(self.no_composicio), 'orgues': self.no_composicio},
            'no_estat': {'count': len(self.no_estat), 'orgues': self.no_estat},
            'no_temperament': {'count': len(self.no_temperament), 'orgues': self.no_temperament},
            'no_constructor': {'count': len(self.no_constructor), 'orgues': self.no_constructor},
            'altres': {
                'registres': {
                    'total': self.registres + self.registres_pedal,
                    'manual': self.registres,
                    'pedal': self.registres_pedal
                },
                'manuals': self.teclats,
                'pedalers': self.pedalers,
                'fotos': self.fotos,
            }

            # TODO. comptar poblacions amb orgue, per exemple
        }
        with open("_data/comptadors.yml", "w") as file:
            yaml.dump(comptadors, file, encoding='utf-8', allow_unicode=True)

    def __count(self, core_path):
        self.__count_on_post(core_path)
        self.__count_on_disposicions(core_path)

    def __count_on_post(self, core_path):
        post = frontmatter.load(f"orgues/{core_path}.md")
        if 'fotos' in post:
            self.foto[0] += 1
            self.fotos += len(post['fotos'])
        else:
            self.foto[1] += 1
            self.no_foto.append(' '.join(core_path.split('/')[::-1]))

    def __count_on_disposicions(self, core_path):
        yml_file = f"_data/disposicions/{core_path}.yml"
        if os.path.exists(yml_file):
            # 1 disposició per orgue
            with open(yml_file, "r") as file:
                ym_data = yaml.load(file, Loader=yaml.FullLoader)
            self.__count_on_orgue(ym_data, core_path)
        else:
            # més d'1 disposició per un orgue (palau nacional amb dues disposicions)
            dir_path = f"_data/disposicions/{core_path}"
            for file in os.listdir(dir_path):
                yml_file = os.path.join(dir_path, file)
                with open(yml_file, "r") as f:
                    yml_data = yaml.load(f, Loader=yaml.FullLoader)
                self.__count_on_orgue(yml_data, core_path)

    def __count_on_orgue(self, data, path):
        # TODO ser més precís. Què falta?
        if 'historic' in data:
            return

        self.orgues_inventariats += 1

        for teclat in data['teclats']:
            self.teclats +=1
            self.registres += len(teclat['registres'])

        if 'pedal' in data:
            self.pedalers += 1
            self.registres_pedal += len(data['pedal']['registres'])

        if not 'constructor' in data:
            self.no_constructor.append(' '.join(path.split('/')[::-1]))
        if not 'diapaso' in data:
            self.no_diapaso.append(' '.join(path.split('/')[::-1]))
        if not 'temperament' in data:
            self.no_temperament.append(' '.join(path.split('/')[::-1]))
        if not 'estat' in data:
            self.no_estat.append(' '.join(path.split('/')[::-1]))
        if not 'transmissio' in data:
            self.no_transmissio.append(' '.join(path.split('/')[::-1]))
        if not 'emplacament' in data:
            self.no_emplacament.append(' '.join(path.split('/')[::-1]))
        if not 'composicio' in data:
            self.no_composicio.append(' '.join(path.split('/')[::-1]))


if __name__ == "__main__":
    orguesCounter = OrguesCounter()
    orguesCounter.compute()
    orguesCounter.write()
