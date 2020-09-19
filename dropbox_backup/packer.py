import os
import tarfile
import shutil
from .logger import get_logger


def dir_size(root_path):
    total = 0
    for path, dirs, files in os.walk(root_path):
        for file in files:
            filepath = os.path.join(path, file)
            total += os.path.getsize(filepath)
    return total


class BackupPacker:
    def __init__(self, pack_from: str, pack_to: str, basename):
        self.logger = get_logger(__name__)
        self.pack_from = pack_from
        self.pack_to = pack_to
        self.backup_basename = basename
        self.temp_path = '/tmp/origin'

    def copy_origin(self) -> None:
        self.logger.info('coping original file...')
        shutil.copytree(self.pack_from, self.temp_path)
        for file in os.listdir(self.temp_path):
            os.chown(os.path.join(self.temp_path, file), uid=1000, gid=1000)
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
        self.logger.info(
            'pack {0} → {1} byte'.format(
                tarinfo.name,
                size
            )
        )
        return tarinfo

    def run(self):
        self.copy_origin()
        self.make_tar()
