# Dropbox Backup

Create tar.gz archive and upload to Dropbox.

## Usage

### Build
<code>
docker build -t noxowl/dropbox-backup:latest .
</code>

### Run
<code>
docker run --rm -it --name dropbox-backup -e DROPBOX_BACKUP_ACCESS_TOKEN="YOUR_TOKEN" -e DROPBOX_BACKUP_LOG_FOR_HUMAN="true" -e DROPBOX_BACKUP_TO="YOUR_DROPBOX_APP_FOLDER_PATH" -v [ORIGIN_PATH]:/srv/origin noxowl/dropbox-backup:latest
</code>
