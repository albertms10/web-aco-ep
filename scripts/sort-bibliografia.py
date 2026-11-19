import yaml


class SortBibliografia:
    def compute(self):
        with open("_data/llibres.yml", "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        data['llibres'] = self.__sort(data['llibres'])
        data['llibrets'] = self.__sort(data['llibrets'])
        data['general'] = self.__sort(data['general'])
        data['cd'] = self.__sort(data['cd'])

        with open("_data/bibliografia.yml", "w") as file:
            yaml.dump(data, file, encoding='utf-8', allow_unicode=True)

    def __sort(self, data):
        # sort autors primer
        for llibre in data:
            llibre['autors'] = sorted(llibre['autors'], key=lambda x: x['cognoms'])
            for autor in llibre['autors']:
                if len(autor['nom'].split(' ')) > 1:
                    ac = ""
                    for n in autor['nom'].split(' '):
                        if n == "de" or n == "la":
                            ac += n + " "
                        else:
                            ac += n[0] + ". "
                    autor['nom'] = ac[:-1]  # treu l'últim espai
                else:
                    autor['nom'] = autor['nom'][0] + "."

        # sort llibres
        return sorted(data, key=lambda x: [autor['cognoms'] for autor in x['autors']])


if __name__ == "__main__":
    sorter = SortBibliografia()
    sorter.compute()

