# ============================================================
#
#  Easy backup
#  Command line Tool Version
#
#  author: Francisco Perdigon Romero
#  email: fperdigon88@gmail.com
#  github id: fperdigon
#
#  DEBIAN apt install rsync openssh-client sshpass openssl
#  UBUNTU apt install rsync open-ssh sshpass openssl
# ===========================================================

import argparse
from utils.cmd_credentials_management import create_backup_config_cmd, \
     list_backup_configs_cmd, del_backup_configs_cmd, modify_backup_configs_cmd,\
     run_backup, run_all_active_backups
# from utils.easybackup_core import run_incremental_backup
from utils.logger import logger  # Import the shared logger

def main():
    parser = argparse.ArgumentParser(description="Backup Management Script")
    parser.add_argument("-cbc", "--create-backup", action="store_true", 
                        help="Create a new backup configuration.")
    parser.add_argument("-lbc", "--list-backups", action="store_true", 
                        help="List all backup configurations.")
    parser.add_argument("-rbc", "--run-backup", metavar="NAME", 
                        help="Run a backup configuration."),
    parser.add_argument("-dbc", "--del-backup", action="store_true", 
                        help="Delete a backup configuration.")
    parser.add_argument("-mbc", "--modify-backup", action="store_true", 
                        help="Modify a backup configuration.")                

    args = parser.parse_args()

    ######################################
    # DEBUG: Simulating run_backup entry
    # class Args:
    #     #run_backup = "NAS No Key"
    #     run_backup = None
    #     create_backup = None
    #     # create_backup = True
    #     list_backups = None
    #     # list_backups = True
    #     del_backup = None
    #     modify_backup = None

    # args = Args()
    ######################################

    if args.create_backup:
        create_backup_config_cmd()

    elif args.list_backups:
        list_backup_configs_cmd()

    elif args.del_backup:
        del_backup_configs_cmd()

    elif args.modify_backup:        
        modify_backup_configs_cmd()        
        
    elif args.run_backup:                
        run_backup(config_name=args.run_backup)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


