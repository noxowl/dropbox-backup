import os
import sys
import logging
from .packer import BackupPacker
from .transporter import DropboxTransporter
from .logger import get_logger


def is_true(value) -> bool:
    return value.lower() == 'true'


class DropboxBackup:
    def __init__(self):
        self.backup = None
        self.dropbox = None
        self.is_debug = is_true(os.environ['DROPBOX_BACKUP_DEBUG_MODE'])
        logging.basicConfig(
            filename='logs/backup.log',
            level=logging.DEBUG if self.is_debug else logging.INFO)
        self.logger = get_logger(__name__)
        self.is_test = is_true(os.environ['DROPBOX_BACKUP_TEST_MODE'])
        self.access_token = os.environ['DROPBOX_BACKUP_ACCESS_TOKEN']
        self.dropbox_write_mode = os.environ['DROPBOX_BACKUP_WRITE_MODE']
        self.backup_from = os.environ['DROPBOX_BACKUP_FROM']
        self.backup_to = os.environ['DROPBOX_BACKUP_TO']
        self.is_log_for_human = is_true(os.environ['DROPBOX_BACKUP_LOG_FOR_HUMAN'])
        self.backup_basename = os.path.basename(self.backup_to)
        self.pack_to = '/tmp/{0}.tar.gz'.format(self.backup_basename)

    def initialize(self):
        self.logger.info('Dropbox Backup Initialize Started.')
        self.backup = BackupPacker(
            pack_from=self.backup_from,
            pack_to=self.pack_to,
            basename=self.backup_basename,
            for_human=self.is_log_for_human
        )
        self.dropbox = DropboxTransporter(
            access_token=self.access_token,
            write_mode=self.dropbox_write_mode,
            autorename=False
        )
        self.dropbox.connection_check()
        self.logger.info('Dropbox Backup Initialized.')

    def dry_run(self):
        self.backup.run()

    def run(self):
        self.backup.run()
        self.dropbox.upload(self.pack_to, self.backup_to + '.tar.gz')

    def execute(self):
        self.initialize()
        if self.is_test:
            self.dry_run()
        else:
            self.run()
        self.logger.info('Job finished. Exit.')
        sys.exit()


app = DropboxBackup()
