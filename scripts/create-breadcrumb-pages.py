"""
Si us plau, executa aquest script cada vegada que afegeixis un orgue nou. Crearà per tu les pàgines del breadcrumb.
"""
import os

import yaml


def main():
    with open("_data/orgues.yml", "r") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    base_path = "orgues/"
    text_provincia = "---\nlayout: base/bc-provincia\n---\n"
    for provincia in data['provincies']:
        # text_provincia = f"---\nlayout: base/bc-provincia\nredirect_from:\n  - pages/orgues/{provincia['link']}\n---\n"
        filename = base_path+provincia['link']+".md"
        if not os.path.exists(filename):
            with open(filename, "w") as file:
                file.write(text_provincia)

    text_comarca = "---\nlayout: base/bc-comarca\n---\n"
    for comarca in data['comarques']:
        # text_comarca = f"---\nlayout: base/bc-comarca\nredirect_from:\n  - pages/orgues/{comarca['provincia']}/{comarca['link']}\n---\n"
        filename = base_path+comarca['provincia']+"/"+comarca['link']+".md"
        if not os.path.exists(filename):
            with open(filename, "w") as file:
                file.write(text_comarca)

    text_municipi = "---\nlayout: base/bc-municipi\n---\n"
    for provincia in data['orgues']:
        for comarca in provincia['comarques']:
            if 'poblacions' in comarca:
                comarca_path = os.path.join(base_path, provincia['link'], comarca['link'])
                if not os.path.exists(comarca_path):
                    os.mkdir(comarca_path)
                for municipi in comarca['poblacions']:
                    # text_municipi = f"---\nlayout: base/bc-municipi\nredirect_from:\n  - pages/orgues/{provincia['link']}/{comarca['link']}/{municipi['link']}\n---\n"
                    filename = base_path+provincia['link']+"/"+comarca['link']+"/"+municipi['link']+".md"
                    if not os.path.exists(filename):
                        with open(filename, "w") as file:
                            file.write(text_municipi)


if __name__ == "__main__":
    main()
