import yaml
import frontmatter
import os


class WriteOldUrlToRedirectFrom:
    def __init__(self):
        self.short_urls = set()

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
                            continue
                        if 'orgues' not in edifici:
                            core_path = os.path.join(provincia['link'], comarca['link'], poble['link'], edifici['link'])
                            self.__write_redirect_from(core_path)
                        else:
                            for orgue in edifici['orgues']:
                                if 'wip' in orgue:
                                    continue
                                core_path = os.path.join(provincia['link'], comarca['link'], poble['link'], edifici['link'], orgue['link'])
                                self.__write_redirect_from(core_path)

    def __write_redirect_from(self, core_path):
        with open(f"orgues/{core_path}.md", "r") as file:
            lines = file.readlines()
        for index, line in enumerate(lines):
            if 'redirect_from:' in line:
                lines.insert(index+1, f'  - pages/orgues/{core_path}\n')
                break
        with open(f"orgues/{core_path}.md", "w") as file:
            file.writelines(lines)


class WriteGreedyRedirectFrom:
    def __init__(self):
        self.short_urls = set()

    def compute(self):
        with open("_data/orgues.yml", "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        for provincia in data['orgues']:
            for comarca in provincia['comarques']:
                if 'poblacions' not in comarca:
                    continue
                for poble in comarca['poblacions']:
                    if len(poble['edificis']) == 1:
                        edifici = poble['edificis'][0]
                        if 'wip' in edifici:
                            continue
                        if 'orgues' not in edifici:
                            core_path = os.path.join(provincia['link'], comarca['link'], poble['link'], edifici['link'])
                            self.__write_redirect_from(core_path, poble['link'])
                        else:
                            for orgue in edifici['orgues']:
                                if 'wip' in orgue:
                                    continue
                                core_path = os.path.join(provincia['link'], comarca['link'], poble['link'], edifici['link'], orgue['link'])
                                self.__write_redirect_from(core_path, f"{poble['link']}-{orgue['link']}")
                    elif len(poble['edificis']) > 1:
                        for edifici in poble['edificis']:
                            if 'wip' in edifici:
                                continue
                            if 'orgues' not in edifici:
                                core_path = os.path.join(provincia['link'], comarca['link'], poble['link'], edifici['link'])
                                self.__write_redirect_from(core_path, f"{edifici['link']}-{poble['link']}")
                            else:
                                for orgue in edifici['orgues']:
                                    if 'wip' in orgue:
                                        continue
                                    core_path = os.path.join(provincia['link'], comarca['link'], poble['link'], edifici['link'], orgue['link'])
                                    self.__write_redirect_from(core_path, f"{edifici['link']}-{poble['link']}-{orgue['link']}")

    def __write_redirect_from(self, core_path, redirect):
        post = frontmatter.load(f"orgues/{core_path}.md")
        if 'redirect_from' not in post:
            with open(f"orgues/{core_path}.md", "r") as file:
                lines = file.readlines()
            for index, line in enumerate(lines):
                if 'layout: ' in line:
                    lines.insert(index+1, f'redirect_from:\n  - orgues/{redirect}/\n')
                    break
            with open(f"orgues/{core_path}.md", "w") as file:
                file.writelines(lines)


class TestDuplicatedRedirects:
    def __init__(self):
        self.short_urls = set()
        self.errors = 0

    def compute(self):
        with open("_data/orgues.yml", "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        for provincia in data['orgues']:
            for comarca in provincia['comarques']:
                if 'poblacions' not in comarca:
                    continue
                for poble in comarca['poblacions']:
                    # si només tenim un edifici, ho escrivim tot; si no, ho deixem en blanc
                    for edifici in poble['edificis']:
                        if 'wip' in edifici:
                            continue
                        if 'orgues' in edifici:
                            for orgue in edifici['orgues']:
                                if 'wip' in orgue:
                                    continue
                                core_path = os.path.join(provincia['link'], comarca['link'], poble['link'], edifici['link'], orgue['link'])
                                self.__count(core_path)
                        else:
                            core_path = os.path.join(provincia['link'], comarca['link'], poble['link'], edifici['link'])
                            self.__count(core_path)

        if self.errors == 0:
            print("All redirections are unique. GOOD!")

    def __count(self, core_path):
        post = frontmatter.load(f"orgues/{core_path}.md")

        if 'redirect_from' in post:
            if isinstance(post['redirect_from'], list):
                for element in post['redirect_from']:
                    if element not in self.short_urls:
                        self.short_urls.add(element)
                    else:
                        print(f"ERROR! {element} duplicated in {core_path}.")
                        self.errors += 1
            else:
                if post['redirect_from'] not in self.short_urls:
                    self.short_urls.add(post['redirect_from'])
                else:
                    print(f"ERROR! {post['redirect_from']} duplicated in {core_path}.")
                    self.errors += 1


if __name__ == "__main__":
    test = TestDuplicatedRedirects()
    # test = WriteGreedyRedirectFrom()
    # test = WriteOldUrlToRedirectFrom()
    test.compute()
