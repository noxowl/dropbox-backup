import os
import dropbox
from tqdm import tqdm
from .logger import get_logger

mode = {
    'add': 'add',
    'overwrite': 'overwrite',
    'update': 'update'
}


class DropboxTransporter:
    def __init__(self, access_token: str, write_mode: str, autorename: bool):
        self.logger = get_logger(__name__)
        self.access_token = access_token
        self.dropbox_session = dropbox.Dropbox(self.access_token)
        self.autorename = autorename
        self.chunk_size = 4 * 1024 * 1024
        try:
            self.write_mode = dropbox.files.WriteMode(mode[write_mode])
        except KeyError:
            self.logger.error('Please input the correct Write Mode. [add/overwrite/update]')
            raise KeyError

    def upload(self, file, file_to) -> None:
        self.logger.info('initiate dropbox upload.')
        with open(file, 'rb') as f:
            size = os.path.getsize(file)
            if size <= self.chunk_size:
                self.logger.info(
                    self.dropbox_session.files_upload(
                        f.read(),
                        file_to,
                        mode=self.write_mode,
                        autorename=self.autorename)
                )
            else:
                with tqdm(total=size) as progress:
                    upload_session = self.dropbox_session.files_upload_session_start(
                        f.read(self.chunk_size),
                    )
                    progress.update(self.chunk_size)
                    cursor = dropbox.dropbox.files.UploadSessionCursor(
                        session_id=upload_session.session_id,
                        offset=f.tell()
                    )
                    upload_commit = dropbox.dropbox.files.CommitInfo(
                        path=file_to,
                        mode=self.write_mode
                    )
                    while f.tell() < size:
                        if (size - f.tell()) <= self.chunk_size:
                            self.logger.info(
                                self.dropbox_session.files_upload_session_finish(
                                    f.read(self.chunk_size), cursor, upload_commit
                                )
                            )
                        else:
                            self.dropbox_session.files_upload_session_append_v2(
                                f.read(self.chunk_size),
                                cursor
                            )
                            cursor.offset = f.tell()
                        progress.update(self.chunk_size)
        self.logger.info('dropbox upload finished.')

    def connection_check(self) -> None:
        payload = 'ping'
        echo = self.dropbox_session.check_user(payload)
        self.logger.debug(echo)
        if echo.result != payload:
            self.logger.error('Dropbox connection failed.')
            raise ConnectionError
        else:
            self.logger.error('Dropbox connection success.')
