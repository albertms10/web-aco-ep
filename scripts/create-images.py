import argparse
import copy
import dataclasses
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import time
from threading import Thread, Lock

import PIL.Image
import frontmatter
import owncloud
import yaml

THUMB_SIZES = (320, 640, 768, 1024, 1366, 1600, 1920, 2560)

@dataclasses.dataclass
class Photo:
    # Atributs que vénen del post (manuals)
    nom: str = ""
    alt: str = ""
    caption: str = ""
    autor: str = ""
    portada: str = ""
    galeria: bool = True
    # Atributs durant la creació
    page_id: str = ""
    path:str = ""
    # Atributs automàtics provinents d'exif
    date: str = ""
    width: int = 0
    height: int = 0
    orientation: int = 0
    # altres
    link: str = ""
    srcset: str = ""
    sort_id: int = 0
    thumbs: dict = dataclasses.field(default_factory = lambda: {320: "", 640: "", 768: "", 1024: "", 1366: "", 1600: "", 1920: "", 2560: ""})

    @staticmethod
    def from_dict(photo):
        return Photo(**photo)

    @staticmethod
    def copy(photo: 'Photo'):
        return copy.deepcopy(photo)

    @staticmethod
    def to_dict(photo):
        return dataclasses.asdict(photo)


class Utils:
    @staticmethod
    def get_photos_from_posts():
        photos = []
        sort_id = 0
        for root, dirs, files in os.walk("orgues"):
            for file in files:
                if file.endswith("md"):
                    metadata = frontmatter.load(str(os.path.join(root, file)))
                    if 'fotos' not in metadata:
                        continue
                    for photo in metadata['fotos']:
                        p_dict = Photo.from_dict(photo)
                        p_dict.path = str(pathlib.Path(str(os.path.join(root, file))).relative_to('orgues')).rsplit('.', 1)[0]  # p/c/m/e o bé p/c/m/e/o
                        p_dict.page_id = f"/orgues/{p_dict.path}/"
                        p_dict.sort_id = sort_id
                        photos.append(p_dict)
                        sort_id += 1
        return photos

    @staticmethod
    def get_exif(filename):
        exif_process = subprocess.run(f"exiftool -s -FileModifyDate "
                                      f"-DateTimeOriginal -DateTime "
                                      f"-ImageWidth -ImageHeight "
                                      f"-Creator -Rights -Artist "
                                      f"-Orientation "
                                      f"\"{filename}\"", shell=True, stdout=subprocess.PIPE)
        exif_data = exif_process.stdout.decode("UTF-8", "ignore")

        file_time = None
        date_time = None
        width = 0
        height = 0
        orientation = 0
        artist = ""

        for line in exif_data.split('\n'):
            if "FileModifyDate" in line:
                file_time = line.split(':', 1)[1].strip()
                file_time = file_time.replace(':', '-', 2)

            if "DateTimeOriginal" in line:
                date_time = line.split(':', 1)[1].strip()
                date_time = date_time.replace(':', '-', 2)
            elif "DateTime" in line:  # alternative not preferred
                date_time = line.split(':', 1)[1].strip()
                date_time = date_time.replace(':', '-', 2)

            if "ImageWidth" in line:
                width = int(line.split(":", 1)[1].strip())
            if "ImageHeight" in line:
                height = int(line.split(":", 1)[1].strip())

            if "Orientation" in line:
                # Orientation                     : Rotate 90 CW
                # Orientation                     : Horizontal (normal)  -> this throw exception (expected)
                try:
                    orientation = int(line.split(":", 1)[1].strip().split(" ")[1])
                except (ValueError, IndexError):
                    orientation = 0

            if "Artist" in line or "Creator" in line:
                artist = line.split(":", 1)[1].strip()

        if width == 0 or height == 0:
            log.critical("ERROR! Image has 0 width or height!")
            sys.exit(-2)

        if orientation != 0 and orientation != 180 and width > height:
            width, height = height, width

        return ImageExif(file_time, width, height, date_time, orientation, artist)


    @staticmethod
    def add_size_to_filename(filename: str, size: int):
        last_dot = filename.rfind('.')
        return filename[0:last_dot] + "-" + str(size) + ".webp"

    @staticmethod
    def copy_exif(src, dst):
        subprocess.run(f"exiftool -overwrite_original -TagsFromFile {src} "
                       f"-Creator -Rights -Author -DateTimeOriginal {dst}",
                       shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @staticmethod
    def write_photos_yml(photos: list[Photo]):
        yaml_data = [Photo.to_dict(f) for f in photos]
        with open("_data/imatges.yml", "w") as file:
            yaml.dump(yaml_data, file, encoding='utf-8', allow_unicode=True)

    @staticmethod
    def read_photos_yml():
        with open("_data/imatges.yml", "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        return data


class ImageExif:
    # EXIF information and tags
    # https://exiftool.org/TagNames/EXIF.html

    def __init__(self, file_time, width, height, date_time, rotated=0, artist=""):
        self.file_time: str = file_time
        self.width: int = width
        self.height: int = height
        self.date_time: str = date_time
        self.rotated: int = rotated
        self.artist: str = artist


class ThumbnailCreator:
    # PORTADA
    PORTADA_W = 1228  # Modified Container to be 1260 px - 'px-3' (= 1rem x2 x16 px) = 1228 px
    PORTADA_H = 267  # Aspect ratio: 4.6
    ASPECT_RATIO = 4.6

    # És inviable pujar les imatges al núvol una a una, més havent de comprovar si existeixen. Passa quelcom amb la
    # llibreria `pyocclient` i la configuració del núvol que fa impossible comprovar ràpidament si un fitxer existeix
    # o no.
    # Per això, he decidit executar-ho tot en local tenint el client de nextcloud instal·lat amb la sincronització
    # activada. Quan acabi aquesta classe, pot començar la següent demanant enllaços. Manegar els fitxers en local
    # és molt més ràpid i còmode.
    def __init__(self):
        self.original_dir = "/home/berenguer/nc/aco/web/web/img/orgues"
        self.thumb_dir = "/home/berenguer/nc/aco/web/web/img/thumb-orgues"
        os.makedirs(self.thumb_dir, exist_ok=True)

        # Coming from posts
        self.photos = []  # type: list[Photo]
        # All the photos plus thumbnails
        self.all_photos = []  # type: list[Photo]
        self.work_queue = []

        self.threads = [Thread(target=self.__thread_function) for i in range(6)]
        self.photos_lock = Lock()

    def process(self):
        # 1. get the work
        self.photos = Utils.get_photos_from_posts()
        self.work_queue = self.photos[:]  # shallow copy. I will not modify; only remove references

        # 2. start the work
        for t in self.threads:
            t.start()
        for t in self.threads:
            t.join()

        # 3. write result
        Utils.write_photos_yml(self.all_photos)

    def __thread_function(self):
        # IS THREAD SAFE
        done = False
        while not done:
            with self.photos_lock:
                try:
                    photo = self.work_queue.pop()
                except IndexError:
                    done = True

            if not done:
                log.info(f"Processing {photo.path}/{photo.nom}")
                self.__process_photo(photo)

    def __process_photo(self, photo: Photo):
        # Thread function. IS THREAD SAFE
        # original ≃ /orgues/p/c/m/e/...  -> read_only
        # thumb ≃ /thumb-orgues/p/c/m/e/...  -> original + thumbs (tot en un sol lloc)
        portada_settings = ""

        original_changed = False
        original_file = os.path.join(self.original_dir, photo.path, photo.nom)
        original_exif = Utils.get_exif(original_file)

        # Update thumb_file
        thumb_file = os.path.join(self.thumb_dir, photo.path, photo.nom)
        if os.path.exists(thumb_file):
            thumb_exif = Utils.get_exif(thumb_file)
            if original_exif.file_time != thumb_exif.file_time:
                original_changed = True
                shutil.copy2(original_file, thumb_file)
        else:
            os.makedirs(os.path.join(self.thumb_dir, photo.path), exist_ok=True)
            shutil.copy2(original_file, thumb_file)
            original_changed = True

        # create the photo to put in yml (don't look in cache for exif because I already have the info)
        photo.autor = original_exif.artist if photo.autor == "" else photo.autor
        photo.date = original_exif.date_time
        photo.width = original_exif.width
        photo.height = original_exif.height
        photo.orientation = original_exif.rotated
        if photo.portada != "":  # si no és portada, serà "" (default). Si és portada, serà != ""
            portada_settings = str(photo.portada)
            photo.portada = ""

        # create thumbnails (will add info to photo!)
        self.__create_thumbnails(photo, original_changed)
        with self.photos_lock:
            self.all_photos.append(photo)

        if portada_settings != "":
            self.__process_portada(photo, portada_settings, original_changed)

    def __process_portada(self, photo: Photo, portada_settings, changed):
        # IS THREAD SAFE
        foto_portada = Photo.copy(photo)
        foto_portada.nom = photo.nom.rsplit('.',1)[0] + "_portada.webp"
        foto_portada.portada = portada_settings
        with self.photos_lock:
            self.all_photos.append(foto_portada)

        original_filename = os.path.join(self.original_dir, photo.path, photo.nom)
        portada_filename = os.path.join(self.thumb_dir, foto_portada.path, foto_portada.nom)

        if changed or not os.path.exists(portada_filename):
            # do crop
            image_file = PIL.Image.open(os.path.join(self.original_dir, photo.path, photo.nom))
            if photo.orientation == 90:
                # rotation CCW
                image_file = image_file.transpose(method=PIL.Image.Transpose.ROTATE_270)
            elif photo.orientation == 270:
                # rotation CCW
                image_file = image_file.transpose(method=PIL.Image.Transpose.ROTATE_90)

            # for this calculation, refer to the README
            width, height = image_file.size
            left = 0
            right = width
            if portada_settings != "" and portada_settings[-1] == '%':
                percentage = int(portada_settings[:-1]) / 100
                top = int(height * percentage - width / ThumbnailCreator.ASPECT_RATIO * percentage)
            else:
                top = int(portada_settings)
            bottom = int(width / ThumbnailCreator.ASPECT_RATIO + top)

            # generate images:
            portada_image = image_file.crop((left, top, right, bottom))
            portada_image.save(portada_filename, quality=85, method=6)
            Utils.copy_exif(original_filename, portada_filename)  # for legal reasons. They are not read

        self.__create_thumbnails(foto_portada, changed)

    def __create_thumbnails(self, photo: Photo, changed: bool):
        original_filename = os.path.join(self.thumb_dir, photo.path, photo.nom)
        pil_image = PIL.Image.open(original_filename)
        for size in THUMB_SIZES:
            thumb_name_sized = Utils.add_size_to_filename(photo.nom, size)
            thumb_file_sized = os.path.join(self.thumb_dir, photo.path, thumb_name_sized)
            if changed or not os.path.exists(thumb_file_sized):
                thumb_image = pil_image.copy()
                thumb_image.thumbnail(size=(size, size), resample=PIL.Image.Resampling.LANCZOS)
                thumb_image.save(thumb_file_sized, quality=85, method=6)
                Utils.copy_exif(original_filename, thumb_file_sized)  # for legal reasons. They are not read

class DatabaseCreator:
    def __init__(self):
        self.oc_user = os.environ["OC_USER"]
        self.oc_pass = os.environ["OC_PASSWORD"]
        self.oc_url = "https://nextcloud.acorgue.cat"
        self.oc_thumb_path = "web/img/thumb-orgues"

        self.all_photos = []  # type: list[Photo]
        self.unique_paths = {}

        self.get_links_threads = [Thread(target=self.__thread_get_links) for i in range(10)]
        self.get_links_queue = []
        self.get_links_queue_lock = Lock()

        self.assign_links_threads = [Thread(target=self.__thread_assign_links) for i in range(10)]
        self.assign_links_queue = []  # type: list[Photo]
        self.assign_links_queue_lock = Lock()
        self.all_photos_lock = Lock()

        log.info("Logging in")
        self.oc = owncloud.Client(self.oc_url)
        self.oc.login(self.oc_user, self.oc_pass)
        log.info("Logged in")

    def process(self):
        data = Utils.read_photos_yml()
        self.__get_share_links_in_bulk(data)
        self.__assign_link_to_each_photo()
        self.__fill_srcset_to_original()
        self.__write_yml()

    def __get_share_links_in_bulk(self, data):
        # Multithread
        # Reads yml data (-> get_links_queue) and fills assign_links_queue
        t1 = time.time()

        # prepare the dictionary to assign work to each thread easily
        for p in data:
            photo_ = Photo.from_dict(p)
            if photo_.path not in self.unique_paths:
                self.unique_paths[photo_.path] = None  # force the creation of the key in the dict. Each thread will populate it
            self.assign_links_queue.append(photo_)
        self.get_links_queue = list(self.unique_paths.keys())

        for th in self.get_links_threads:
            th.start()
        for th in self.get_links_threads:
            th.join()
        print("Time for prepare:", time.time()-t1)

    def __assign_link_to_each_photo(self):
        # Multithread
        # Reads assign_links_queue and fills all_photos. All photos with its link
        t1 = time.time()
        for th in self.assign_links_threads:
            th.start()
        for th in self.assign_links_threads:
            th.join()
        print("Time for links:", time.time()-t1)

    def __fill_srcset_to_original(self):
        # 1 Thread
        # Reads all_photos and completes information
        t1 = time.time()
        for photo in self.all_photos:
            srcset = ""
            for size in THUMB_SIZES:
                srcset += f"{photo.thumbs[size]} {size}w,"
            photo.srcset = srcset[:-1]  # remove last comma
        print("Time for srcset:", time.time()-t1)

    def __write_yml(self):
        self.all_photos.sort(key=lambda x: x.sort_id)
        Utils.write_photos_yml(self.all_photos)

    def __thread_get_links(self):
        # IS THREAD SAFE
        done = False
        while not done:
            with self.get_links_queue_lock:
                try:
                    path = self.get_links_queue.pop()
                except IndexError:
                    done = True
            if not done:
                links = self.__get_shared_links_in_folder(path)
                log.debug(f"Got shared links in {path}")
                self.unique_paths[path] = links  # every path is unique -> no need for locks

    def __thread_assign_links(self):
        # IS THREAD SAFE
        done = False
        while not done:
            with self.assign_links_queue_lock:
                try:
                    photo = self.assign_links_queue.pop()
                except IndexError:
                    done = True
            if not done:
                self.__thread_assign_links_task(photo)

    def __thread_assign_links_task(self, photo):
        # try to look in all the links in the folder (fast)
        for link in self.unique_paths[photo.path]:
            links_found = 0
            if link['nom'] == photo.nom:
                log.debug(f"Link found in folder share list for {photo.path}/{photo.nom}")
                photo.link = link['url']
                links_found += 1
            for size in THUMB_SIZES:
                thumb_name = Utils.add_size_to_filename(photo.nom, size)
                if link['nom'] == thumb_name:
                    log.debug(f"Link found in folder share list for {photo.path}/{thumb_name}")
                    photo.thumbs[size] = link['url']
                    links_found += 1
            if links_found == len(THUMB_SIZES) + 1:
                break

        # If link is not found, get a new link
        if photo.link == "":
            photo.link = self.__get_share_link(os.path.join(self.oc_thumb_path, photo.path, photo.nom))
        for size in THUMB_SIZES:
            if photo.thumbs[size] == "":
                thumb_name = Utils.add_size_to_filename(photo.nom, size)
                photo.thumbs[size] = self.__get_share_link(os.path.join(self.oc_thumb_path, photo.path, thumb_name))

        photo.link += "/download"
        for size in THUMB_SIZES:
            photo.thumbs[size] += "/download"

        with self.all_photos_lock:
            self.all_photos.append(photo)

    def __get_share_link(self, filename):
        if self.__is_shared(filename):
            link_ob = self.__get_shares(filename)
            log.debug(f"Reusing share for {filename}")
            if len(link_ob) < 1:
                return ""
            return link_ob[0].share_info['url']
        else:
            link_ob = self.__share_file(filename)
            log.debug(f"New share for {filename}")
            if link_ob is None:
                return ""
            return link_ob.share_info['url']

    def __is_shared(self, filename):
        try:
            return self.oc.is_shared(filename)
        except owncloud.HTTPResponseError as e:
            log.critical(f"ERROR! is_shared({filename}) failed. HTTPResponseError: {str(e)}")
            return False
        except Exception as e:
            log.critical(f"ERROR! is_shared({filename}) failed. Unknown exception: {str(e)}")
            return False

    def __get_shares(self, filename):
        try:
            return self.oc.get_shares(filename)
        except owncloud.HTTPResponseError as e:
            log.critical(f"ERROR! get_shares({filename}) failed. HTTPResponseError: {str(e)}")
            return []
        except Exception as e:
            log.critical(f"ERROR! get_shares({filename}) failed. Unknown exception: {str(e)}")
            return []

    def __get_shared_links_in_folder(self, path):
        """
        Llista de diccionaris. Cada diccionari és una foto compartida:
            [{'nom': a.jpg, 'url': https://...}, {'nom': b.jpg, 'url': https://..}, ...]
        """
        fotos_links = []
        try:
            links_ob = self.oc.get_shares(os.path.join(self.oc_thumb_path, path), subfiles=True)
            for link in links_ob:
                fotos_links.append({'nom': link.share_info['file_target'][1:], 'url': link.share_info['url']})
            return fotos_links
        except owncloud.OCSResponseError:
            log.warning(f"ERROR! {os.path.join(self.oc_thumb_path, path)} not found in server!")
            return []

    def __share_file(self, filename):
        try:
            return self.oc.share_file_with_link(filename)
        except owncloud.HTTPResponseError as e:
            log.critical(f"ERROR! share_file_with_link({filename}) failed. HTTPResponseError: {str(e)}")
            return None
        except Exception as e:
            log.critical(f"ERROR! share_file_with_link({filename}) failed. Unknown exception: {str(e)}")
            return None


if __name__ == "__main__":
    log = logging.getLogger('web')
    log.setLevel(level=logging.DEBUG)
    log.addHandler(logging.StreamHandler())

    ti = time.time()
    thumbnailCreator = ThumbnailCreator()
    thumbnailCreator.process()
    # TODO wait local client sync everything!
    databaseCreator = DatabaseCreator()
    databaseCreator.process()
    print(time.time() - ti)
