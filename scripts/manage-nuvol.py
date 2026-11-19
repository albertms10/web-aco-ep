import argparse
import logging
import os
import owncloud

class Cloud:
    def __init__(self):
        self.oc_user = os.environ["OC_USER"]
        self.oc_pass = os.environ["OC_PASSWORD"]
        self.oc_url = "https://nextcloud.acorgue.cat"
        log.info("Logging in")
        self.oc = owncloud.Client(self.oc_url)
        self.oc.login(self.oc_user, self.oc_pass)
        log.info("Logged in")

    def download_file(self, remote, local):
        try:
            self.oc.get_file(remote, local)
        except owncloud.HTTPResponseError as e:
            log.critical(
                f"ERROR! get_file({remote}, {local}) failed. Maybe file doesn't exist. HTTPResponseError: {str(e)}")
            return None
        except Exception as e:
            log.critical(f"ERROR! get_file({remote}, {local}) failed. Unknown exception: {str(e)}")
            return None

    def upload_file(self, remote, local):
        try:
            self.oc.put_file(remote, local)
        except owncloud.HTTPResponseError as e:
            log.critical(f"ERROR! put_file({remote}, {local}) failed. HTTPResponseError: {str(e)}")
        except Exception as e:
            log.critical(f"ERROR! put_file({remote}, {local}) failed. Unknown exception: {str(e)}")

    def mkdir(self, remote):
        try:
            self.oc.mkdir(remote)
        except owncloud.HTTPResponseError as e:
            log.critical(f"ERROR! mkdir({remote}) failed. HTTPResponseError: {str(e)}")
        except Exception as e:
            log.critical(f"ERROR! mkdir({remote}) failed. Unknown exception: {str(e)}")

    def list(self, remote, depth):
        try:
            return self.oc.list(remote, depth)
        except owncloud.HTTPResponseError as e:
            log.critical(f"ERROR! list({remote}) failed. HTTPResponseError: {str(e)}")
        except Exception as e:
            log.critical(f"ERROR! list({remote}) failed. Unknown exception: {str(e)}")

    def file_exists(self, remote):
        try:
            self.oc.file_info(remote)
            return True
        except owncloud.HTTPResponseError as e:
            if e.res == 404:
                return False


def download_geojson(cloud):
    if not os.path.exists("assets/geojson"):
        os.mkdir("assets/geojson")

    contents = cloud.list("/web/geojson/", depth=2)
    for content in contents:
        if content.is_dir():
            if not os.path.exists("assets/geojson/" + content.get_name()):
                log.info("Making dir " + content.get_name() + "...")
                os.mkdir("assets/geojson/" + content.get_name())
        else:
            remote_path = content.get_path() + "/" + content.get_name()  # type: str
            local_path = remote_path.replace("/web", "assets")
            if not os.path.exists(local_path):
                log.info("Downloading file " + local_path)
                cloud.download_file(remote_path, local_path)

def upload_geojson(cloud):
    for root, dirs, files in os.walk("assets/geojson/"):
        base_path = root.split("assets")[1]  # assets/geojson/comarques -> /geojson/comarques
        for dir in dirs:
            directory = str(os.path.join(base_path, dir))
            if not cloud.file_exists("/web" + directory):
                log.info("  - Creating directory /web/" + directory)
                cloud.mkdir("/web" + directory)
            else:
                log.info(f"  + Skipping /web{directory}. Already exists")
        for file in files:
            filename = str(os.path.join(base_path, file))
            if not cloud.file_exists("/web" + filename):
                log.info("  - Uploading file " + filename)
                cloud.upload_file("/web" + filename, os.path.join(root, file))
            else:
                log.info(f"  + Skipping /web{filename}. Already exists")

def main():
    parser = argparse.ArgumentParser(
        prog='ManageNúvol',
        description="Baixa i puja informació estàtica del i des del núvol. Quan es treballa en local, les imatges, les"
                    "coordenades GPS s'actualitzen, però com que és un procés costós, no es vol que el faci CI. Per "
                    "això, durant el desenvolupament es calculen i després es pugen. El núvol se les baixa. "
                    "Quan es comença a desenvolupar la pàgina per primera vegada, es poden baixar també.")
    parser.add_argument('-u', '--upload',
                        action='store_true',
                        help='uploads the database to the cloud (after being created/updated)')
    parser.add_argument('-d', '--download',
                        action='store_true',
                        help='downloads the database from the cloud')

    args = parser.parse_args()

    cloud = Cloud()
    if args.upload:
        cloud.upload_file("web/img/thumb-orgues/imatges.yml", "_data/imatges.yml")
        upload_geojson(cloud)
    elif args.download:
        cloud.download_file("web/img/thumb-orgues/imatges.yml", "_data/imatges.yml")
        download_geojson(cloud)
    else:
        parser.print_help()


if __name__ == "__main__":
    log = logging.getLogger('web')
    log.setLevel(level=logging.DEBUG)
    log.addHandler(logging.StreamHandler())

    main()

