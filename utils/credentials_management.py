# ============================================================
#
#  Easy backup
#  Credentials Management 
#
#  author: Francisco Perdigon Romero
#  email: fperdigon88@gmail.com
#  github id: fperdigon
#
# ===========================================================

from utils.credentials_encryption import load_encrypted_json, save_encrypted_json,\
     generate_key
import os
from utils.logger import logger
from pathlib import Path

# TODO: Possible fix to avoid storing pass
# create key for the program
# ssh-keygen -t rsa -b 4096 -f ~/.ssh/easybackup_key -N ""
# ssh-copy-id -i ~/.ssh/easybackup_key.pub -p <ssh_port> <user>@<remote_host>
# or
# cat ~/.ssh/backup_key.pub | ssh -p <ssh_port> <user>@<remote_host> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
# test connection whithout a pasword
# ssh -i ~/.ssh/backup_key -p <ssh_port> <user>@<remote_host>


ENCRIPTION_KEY = generate_key()
BACKUP_FILE = Path.home() / ".easybackup_configs.enc"

def check_if_backup_config_exist(config_name):
    stored_backup_configs = load_backup_configs(backup_file=BACKUP_FILE)
    if bool(stored_backup_configs[config_name]):
        flag = True
    else:
        flag = False
        logger.info(f"Configuration {config_name} do not exist.")
    return flag

def create_backup_config(name, local_path, remote_path, ssh_user, ssh_password, 
                         remote_host, ssh_key, ssh_port, keep_days, active):

    new_config = {"name": name,
                  "local_path": local_path,
                  "remote_path": remote_path,
                  "ssh_user": ssh_user,
                  "ssh_password": ssh_password,
                  "remote_host": remote_host,
                  "ssh_key": ssh_key,
                  "ssh_port": ssh_port,
                  "keep_days": keep_days,
                  "active": active}
    stored_backup_configs = load_backup_configs(backup_file=BACKUP_FILE)
    # Using remote host as name in case that no name has been provided
    if new_config["name"] == "":
        new_config["name"] = new_config["remote_host"]
    stored_backup_configs[new_config["name"]] = new_config
    save_flag = save_backup_configs(backups_configs=stored_backup_configs, backup_file=BACKUP_FILE)
    if save_flag:
        logger.debug("New config was sucessfully created.")

    return save_flag


def load_backup_configs(backup_file="./easybackup_configs.enc"):
    logger.debug("Loading stored backup configurations.")
    stored_backup_configs = {}
    if os.path.exists(backup_file):
        logger.debug("Stored backup configurations exist.")
        stored_backup_configs = load_encrypted_json(file_path=backup_file, key=ENCRIPTION_KEY)
        logger.debug("Stored backup configurations loaded sucesfully.")
    else:
        logger.debug("Stored backup configurations do not exist.")

    return stored_backup_configs


def save_backup_configs(backups_configs, backup_file="./easybackup_configs.enc"):
    try:
        save_encrypted_json(file_path=backup_file, data=backups_configs, key=ENCRIPTION_KEY)
        logger.debug("Backup configurations stored sucessfully.")
        flag = True
    except:
        logger.debug("Was not possible to store backup configurations.")
        flag = False

    # save_encrypted_json(file_path=backup_file, data=backups_configs, key=ENCRIPTION_KEY)
    # flag = True   

    return flag


def delete_backup_config(config_name):
    stored_backup_configs = load_backup_configs(backup_file=BACKUP_FILE)    
    if check_if_backup_config_exist(config_name=config_name):
        stored_backup_configs.pop(config_name, None)  # Using .pop( its safer than .del())
        save_backup_configs(backups_configs=stored_backup_configs, backup_file=BACKUP_FILE)
        logger.info(f"Configuration {config_name} deleted sucesfully.") 