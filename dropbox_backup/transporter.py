import dropbox
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
        try:
            self.write_mode = dropbox.files.WriteMode(mode[write_mode])
        except KeyError:
            self.logger.error('Please input the correct Write Mode. [add/overwrite/update]')
            raise KeyError

    def upload(self, file, file_to) -> None:
        self.logger.info('initiate dropbox upload.')
        with open(file, 'rb') as f:
            self.dropbox_session.files_upload(
                f.read(),
                file_to,
                mode=self.write_mode,
                autorename=self.autorename)
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
