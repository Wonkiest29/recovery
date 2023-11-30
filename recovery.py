import os
import zipfile
from ftplib import FTP
from datetime import datetime
import fnmatch
import logging

def create_backup(source_directory, backup_dir, ignored_dirs):
    ignore_file = os.path.join(source_directory, ".ignore")
    if os.path.isfile(ignore_file):
        logging.info(f"Ignore file found in {source_directory}. Backup ignored.")
        return None

    today = datetime.now().strftime('%d.%m.%Y.%H:%M')
    backup_file = os.path.join(backup_dir, f"{today}.zip")

    with zipfile.ZipFile(backup_file, 'w') as zipf:
        for root, dirs, files in os.walk(source_directory):
            dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in ignored_dirs)]

            for file in files:
                if not any(fnmatch.fnmatch(file, pattern) for pattern in ignored_dirs):
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, source_directory))

    return backup_file

def upload_to_ftp(backup_file, ftp_host, ftp_user, ftp_pass, ftp_path):
    with FTP(ftp_host) as ftp:
        ftp.login(user=ftp_user, passwd=ftp_pass)
        ftp.cwd(ftp_path)

        with open(backup_file, 'rb') as file:
            ftp.storbinary(f"STOR {os.path.basename(backup_file)}", file)
            logging.info(f"Uploaded {os.path.basename(backup_file)} to FTP")

def main():
    source_directory = '/var/www/cookie_site/'
    backup_directory = '/home/misha/sites/'
    ignored_dirs = ['*.git*', '*phpmyadmin*']  # Adjust patterns to ignore here

    backup_file = create_backup(source_directory, backup_directory, ignored_dirs)

    if backup_file:
        ftp_host = '192.168.1.229'
        ftp_user = 'misha'
        ftp_pass = 'mi1352m'
        ftp_directory = '/home/misha/sites/'  # Change this to the desired directory in FTP

        upload_to_ftp(backup_file, ftp_host, ftp_user, ftp_pass, ftp_directory)
    else:
        logging.info("No backup created due to ignore file.")

if __name__ == "__main__":
    log_file = 'recovery_log.txt'
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    try:
        main()
        logging.info("Recovery process completed.")
        logging.info("--------------------------------------------------------")
    except Exception as e:
        logging.error(f"An error occurred during recovery: {str(e)}")
