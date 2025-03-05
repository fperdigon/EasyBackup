# ============================================================
#
#  Easy backup
#  Command line Credentials Management 
#
#  author: Francisco Perdigon Romero
#  email: fperdigon88@gmail.com
#  github id: fperdigon
#
# ===========================================================

import getpass
from utils.credentials_management import load_backup_configs, save_backup_configs,\
     create_backup_config, BACKUP_FILE, delete_backup_config, \
     check_if_backup_config_exist
from utils.easybackup_core import run_incremental_backup
from utils.logger import logger

# TODO: Possible fix to avoid storing pass
# create key for the program
# ssh-keygen -t rsa -b 4096 -f ~/.ssh/easybackup_key -N ""
# ssh-copy-id -i ~/.ssh/easybackup_key.pub -p <ssh_port> <user>@<remote_host>
# or
# cat ~/.ssh/backup_key.pub | ssh -p <ssh_port> <user>@<remote_host> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
# test connection whithout a pasword
# ssh -i ~/.ssh/backup_key -p <ssh_port> <user>@<remote_host>

def create_backup_config_cmd():
    print("Creating a new backup configuration. Please enter the informations acordingly. Prass Ctrl+C at anytime to cancel.")

    name = input("Enter backup name: \n")
    local_path = input("Enter local path to be backed it up: \n")
    remote_path = input("Enter remote path where the backup will be stored: \n")
    ssh_user = input("Enter the ssh username: \n")

    while True:
        getpass1 = getpass.getpass("Enter the ssh password: ")
        getpass2 = getpass.getpass("Enter the ssh password again: ")
        if getpass1 == getpass2:
            ssh_password = getpass1
            print("Password received successfully.")
            break
        else:
            print("Passwords do not match try again.")
    
    remote_host = input("Enter shh backup remote host: \n")
    ssh_key = None # Not used for now
    ssh_port = input("Enter the port for the ssh backup remote host [22]: \n") or 22
    keep_days = input("Enter the oldest age in days for your files before start deleting [Enter nothing for infinite]: \n") or None
    active = True

    cmd_creation_flag = create_backup_config(name, local_path, remote_path, ssh_user,
                                             ssh_password, remote_host, ssh_key, 
                                             ssh_port, keep_days, active)
    if cmd_creation_flag:
        logger.debug("New config created sucessfully in cmd.")
    


def list_backup_configs_cmd():
    backup_configs = load_backup_configs(backup_file=BACKUP_FILE)
    if backup_configs:
        c = 0
        print(f"\nBackup configurations [Total {len(backup_configs)}]:\n")
        for key, value in backup_configs.items():            
            #print(f"Backup Name: {key}")
            for sub_key, sub_value in value.items():
                if sub_key == "ssh_password": 
                    sub_value = "***********"
                print(f"  {sub_key}: {sub_value}")
            
            c = c + 1
            if len(backup_configs) > 1 and c < len(backup_configs):
                print("\n#################################\n")

        print("\n")
            
    else:
        logger.info("Nothing to show. No backup configuration has been saved.")

    return backup_configs


def del_backup_configs_cmd():
    # Check if there is any configuration stored yet
    stored_backup_configs = load_backup_configs(backup_file=BACKUP_FILE)
    if stored_backup_configs:
        list_backup_configs_cmd()
        name_to_del = input("Enter the name of the backup configuration you wish to delete:\n")
        delete_backup_config(config_name=name_to_del)
    else:
        logger.info(f"Backup configurations vault is empty. Nothing to be deleted.")


def modify_backup_configs_cmd():
    # Check if there is any configuration stored yet
    stored_backup_configs = load_backup_configs(backup_file=BACKUP_FILE)
    if stored_backup_configs:
        list_backup_configs_cmd()
        name_to_modify = input("Enter the name of the backup configuration you wish to modify:\n")        
        stored_backup_configs = load_backup_configs(backup_file=BACKUP_FILE)    


        if check_if_backup_config_exist(name_to_modify):    
            config_to_be_modified = stored_backup_configs[name_to_modify]
            delete_backup_config(name_to_modify)  # Old config need to be removed 
            for sub_key, sub_value in config_to_be_modified.items():
                if sub_key == "ssh_password": 
                    sub_value = "***********"
                if sub_key == "ssh_key":
                    continue
                print(f"Current value for {sub_key}: {sub_value}")
                new_value = input(f"Enter a new value for [{sub_key}] or press enter to keep the current value [{sub_value}]: \n")
                if new_value:
                    config_to_be_modified[sub_key] = new_value

            stored_backup_configs[config_to_be_modified["name"]] = config_to_be_modified

            save_backup_configs(backups_configs=stored_backup_configs,
                                backup_file=BACKUP_FILE)

    else:
        logger.info(f"Backup configurations vault is empty. Nothing to be deleted.")

def run_backup(config_name):
    # Safe to use in non CMD functions 
    if check_if_backup_config_exist(config_name):
        stored_backup_configs = load_backup_configs(backup_file=BACKUP_FILE)        
        logger.info(f"Starting backup using configuration named: {stored_backup_configs[config_name]['name']}")
        config = stored_backup_configs[config_name]
        run_incremental_backup(local_path=config["local_path"],
                               remote_path=config["remote_path"],
                               ssh_user=config["ssh_user"],
                               ssh_password=config["ssh_password"],
                               remote_host=config["remote_host"],
                               ssh_port=config["ssh_port"],
                               keep_days=config["keep_days"]) 


def run_all_active_backups():
    # Safe to use in non CMD functions 
    stored_backup_configs = load_backup_configs(backup_file=BACKUP_FILE)   

    for backup_config in stored_backup_configs:
        if backup_config["active"]:
            run_backup(config_name=backup_config["name"])
    


# TODO: Add config modification functions
#def set_active_backup_config(backup_config_name):

