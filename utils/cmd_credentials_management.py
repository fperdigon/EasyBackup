import getpass
from utils.credentials_management import load_backup_configs, save_backup_configs,\
     create_backup_config
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

    create_backup_config(name, local_path, remote_path, ssh_user, ssh_password, 
                         remote_host, ssh_key, ssh_port, keep_days, active)

    
    logger.debug("New config created sucessfully in cmd.")
    


def list_backup_configs_cmd():
    backup_configs = load_backup_configs()

    if backup_configs:
        c = 0
        print("\nBackup configurations:\n")
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


# TODO: Add config modification functions
#def set_active_backup_config(backup_config_name):

