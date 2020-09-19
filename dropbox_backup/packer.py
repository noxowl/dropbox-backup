import os
import math
import tarfile
import shutil
from .logger import get_logger


def size_converter(filesize, for_human):
    size_unit = ['Byte', 'KB', 'MB', 'GB', 'TB', 'PB']
    digit = 0
    if for_human:
        if filesize != 0:
            digit = int(math.floor(math.log(filesize, 1024)))
            filesize = round(filesize / math.pow(1024, digit), 2)
    filesize_result = '{0} {1}'.format(filesize, size_unit[digit])
    return filesize_result


def dir_size(root_path):
    total = 0
    for path, dirs, files in os.walk(root_path):
        for file in files:
            filepath = os.path.join(path, file)
            total += os.path.getsize(filepath)
    return total


class BackupPacker:
    def __init__(self, pack_from: str, pack_to: str, basename: str, for_human: bool):
        self.logger = get_logger(__name__)
        self.pack_from = pack_from
        self.pack_to = pack_to
        self.backup_basename = basename
        self.is_for_human = for_human
        self.temp_path = '/tmp/origin'

    def copy_origin(self) -> None:
        self.logger.info('coping original file...')
        shutil.copytree(self.pack_from, self.temp_path)
        for path, dirs, files in os.walk(self.temp_path):
            for file in files:
                os.chown(os.path.join(path, file), uid=1000, gid=1000)
        self.logger.info('original file copied.')
        self.logger.debug(os.listdir(self.temp_path))

    def make_tar(self) -> None:
        self.logger.info('initiate packing.')
        with tarfile.open(self.pack_to, "w:gz") as tar:
            for file in os.listdir(self.temp_path):
                tar.add(
                    '{0}/{1}'.format(self.temp_path, file),
                    arcname='{0}/{1}'.format(self.backup_basename, os.path.basename(file)),
                    recursive=True,
                    filter=self._filter
                )
        if not os.path.exists(self.pack_to):
            self.logger.error('Packed file not exist. abort.')
            raise FileNotFoundError
        else:
            self.logger.info('Packed file {0} is successfully created in {1} → {2} byte'.format(
                self.backup_basename,
                self.pack_to,
                os.path.getsize(self.pack_to)
            ))

    def _filter(self, tarinfo: tarfile.TarInfo):
        size = tarinfo.size
        if tarinfo.isdir():
            size = dir_size(os.path.join(self.temp_path, os.path.basename(tarinfo.name)))
        size = size_converter(size, self.is_for_human)
        self.logger.info(
            'pack {0} → {1}'.format(
                tarinfo.name,
                size
            )
        )
        return tarinfo

    def run(self):
        self.copy_origin()
        self.make_tar()
