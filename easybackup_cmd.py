# ============================================================
#
#  Easy backup
#  Commandline Tool Version
#
#  author: Francisco Perdigon Romero
#  email: fperdigon88@gmail.com
#  github id: fperdigon
#
# ===========================================================

import argparse
from utils.cmd_credentials_management import create_backup_config_cmd, \
     list_backup_configs_cmd
from utils.easybackup_core import run_incremental_backup
from utils.logger import logger  # Import the shared logger

# This variable stores all the backup configurations
BACKUP_CONFIGS = {}

def main():
    parser = argparse.ArgumentParser(description="Backup Management Script")
    parser.add_argument("-cbc", "--create-backup", 
                        help="Create a new backup configuration.")
    parser.add_argument("-lbc", "--list-backups", action="store_true", 
                        help="List all backup configurations.")
    parser.add_argument("-rbc", "--run-backup", metavar="NAME", 
                        help="Run a backup configuration.")

    args = parser.parse_args()

    # DEBUG: Simulating run_backup entry
    class Args:
        #run_backup = "NAS No Key"
        run_backup = None
        create_backup = None
        # create_backup = True
        # list_backups = None
        list_backups = True

    args = Args()

    if args.create_backup:
        create_backup_config_cmd()

    elif args.list_backups:
        list_backup_configs_cmd()
        
    elif args.run_backup:
        #run_backup(args.run_backup)

        from utils.credentials_raw_testing_DO_NOT_ADD_TO_REPO import test_backup_config
        backup_conf_dict = test_backup_config["NAS No Key"]

        logger.info(f"Starting backup using configuration named: {backup_conf_dict['name']}")
        run_incremental_backup(local_path=backup_conf_dict["local_path"],
                               remote_path=backup_conf_dict["remote_path"],
                               ssh_user=backup_conf_dict["ssh_user"],
                               ssh_password=backup_conf_dict["ssh_password"],
                               remote_host=backup_conf_dict["remote_host"],
                               ssh_port=backup_conf_dict["ssh_port"],
                               keep_days=backup_conf_dict["keep_days"])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


