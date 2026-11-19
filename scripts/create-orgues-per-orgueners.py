import os
import yaml


class OrguesPerOrgueners:
    def __init__(self):
        self.path = "_data/disposicions"
        self.info = {}

        with open("_data/orgues.yml", "r") as file:
            self.orgues = yaml.load(file, Loader=yaml.FullLoader)['orgues']

    def process(self):
        for dir_info in os.walk(self.path):
            if len(dir_info[2]) == 0:
                continue
            for file in dir_info[2]:
                self.__process_yml_file(dir_info[0], file)

        # Per facilitar la representació en HTML
        # Nombre d'orgues nous
        for orguener in self.info:
            self.info[orguener]['num_orgues_nous'] = len([1 for orgue in self.info[orguener]['orgues'] if orgue['actuacio'] == "N"])

        # SORT
        for orguener in self.info:
            self.info[orguener]['orgues'] = sorted(self.info[orguener]['orgues'], key=lambda x: x['sort-any'])

        # SORT inside YAML
        keys = sorted(list(self.info.keys()))
        sorted_info = {i: self.info[i] for i in keys}

        with open("_data/orgueners.yml", "w") as file:
            yaml.dump(sorted_info, file, encoding='utf-8', allow_unicode=True, sort_keys=True)

    def __process_yml_file(self, path, file):
        with open(os.path.join(path, file), "r") as tmp:
            data = yaml.load(tmp, Loader=yaml.FullLoader)

        if data is None or 'constructor' not in data or 'historic' in data or self.__is_wip(path, file):
            return

        self.__add_orguener(path, file, data['constructor'])
        if 'actuacions' in data:
            for orguener in data['actuacions']:
                self.__add_orguener(path, file, orguener)

    def __is_wip(self, path, file):
        """
        Donat el path de la disposició i el fitxer de disposició, esbrina si aquest orgue està marcat com a wip
        en el fitxer orgues.yml.
        :param path:
        :param file:
        :return:
        """
        # ['_data', 'disposicions', 'barcelona', 'maresme', 'cabrils']
        # ['_data', 'disposicions', 'barcelona', 'barcelones', 'barcelona', 'sant-felip-neri']
        elements = path.split(os.sep)
        provincia, comarca, poble = elements[2:5]
        if len(elements) > 5:
            edifici = elements[5]
            orgue = file.split(".")[0]
        else:
            edifici = file.split(".")[0]
            orgue = None

        data_provincia = list(filter(lambda x: x['link'] == provincia, self.orgues))[0]['comarques']
        data_comarca = list(filter(lambda x: x['link'] == comarca, data_provincia))[0]['poblacions']
        data_poble = list(filter(lambda x: x['link'] == poble, data_comarca))[0]['edificis']
        data_edifici = list(filter(lambda x: x['link'] == edifici, data_poble))[0]
        if 'wip' in data_edifici:
            return True

        if orgue is None:
            return False

        data_orgue = list(filter(lambda x: x['link'] == orgue, data_edifici.get('orgues', [])))[0]
        return data_orgue.get('wip', False)

    def __add_orguener(self, path, file, data):
        if 'sort-nom' in data:
            key_nom = data['sort-nom']
        elif 'nom' in data and data['nom'] is not None:
            key_nom = data['nom']
        else:
            # El nom no és a la base de dades
            return

        display_nom = self.__generate_nom(data)
        if key_nom not in self.info:
            self.info[key_nom] = {'nom': display_nom, 'orgues': []}

        self.info[key_nom]['orgues'].append({
            'any': self.__generate_any(data),
            'sort-any': self.__generate_sort_any(data),
            'poble': self.__generate_poble(path, file),
            'edifici': self.__generate_edifici(path, file),
            'link': self.__generate_page_link(path, file),
            'actuacio': data['actuacio'] if 'actuacio' in data else "N"
        })

    def __generate_page_link(self, path, file):
        elements = path.split('/')
        link = "orgues/"
        for element in elements[2:]:
            link = os.path.join(link, element)
        if len(elements[2:]) == 3:
            link = os.path.join(link, file.split(".")[0])

        return link

    def __generate_edifici(self, path, file):
        elements = path.split('/')
        provincia = elements[2]
        comarca = elements[3]
        poble = elements[4]
        if len(elements[2:]) == 3:
            edifici = file.split(".")[0]
        else:
            edifici = elements[5]

        data_provincia = list(filter(lambda x: x['link'] == provincia, self.orgues))[0]['comarques']
        data_comarques = list(filter(lambda x: x['link'] == comarca, data_provincia))[0]['poblacions']
        data_poblacions = list(filter(lambda x: x['link'] == poble, data_comarques))[0]['edificis']
        data_edifici = list(filter(lambda x: x['link'] == edifici, data_poblacions))[0]
        return data_edifici['nom']

    def __generate_poble(self, path, file):
        elements = path.split('/')
        provincia = elements[2]
        comarca = elements[3]
        poble = elements[4]

        data_provincia = list(filter(lambda x: x['link'] == provincia, self.orgues))[0]['comarques']
        data_comarques = list(filter(lambda x: x['link'] == comarca, data_provincia))[0]['poblacions']
        data_poblacions = list(filter(lambda x: x['link'] == poble, data_comarques))[0]
        return data_poblacions['nom']

    def __generate_nom(self, constructor):
        if 'sort-nom' in constructor:
            return constructor['nom']

        if constructor['nom'] is None:
            return "?"

        nom = reversed(constructor['nom'].split(',', maxsplit=1))
        return " ".join(nom).strip()

    def __generate_any(self, constructor):
        if 'any' not in constructor:
            return "?"
        if constructor['any'] is None:
            return "?"
        return constructor['any']

    def __generate_sort_any(self, constructor):
        if 'sort-any' in constructor:
            return constructor['sort-any']
        else:
            if isinstance(constructor['any'], int):
                return constructor['any']
            else:
                return 0


if __name__ == "__main__":
    a = OrguesPerOrgueners()
    a.process()
