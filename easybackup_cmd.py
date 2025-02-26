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

from utils.easybackup_core import run_incremental_backup
from utils.logger import logger  # Import the shared logger


if __name__ == "__main__":    
    # Example Usage:
    # incremental_backup("/local/source/", "/backup", "user", "remote.server.com", ssh_password="your_password")
    
    # TODO: Possible fix to avoid storing pass
    # create key for the program
    # ssh-keygen -t rsa -b 4096 -f ~/.ssh/easybackup_key -N ""
    # ssh-copy-id -i ~/.ssh/easybackup_key.pub -p <ssh_port> <user>@<remote_host>
    # or
    # cat ~/.ssh/backup_key.pub | ssh -p <ssh_port> <user>@<remote_host> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
    # test connection whithout a pasword
    # ssh -i ~/.ssh/backup_key -p <ssh_port> <user>@<remote_host>

    # Adding credentials stored infile for testing

    
    
    from utils.credentials_raw_testing_DO_NOT_ADD_TO_REPO import connections_dict
    connection_dict = connections_dict["NAS No Key"]

    run_incremental_backup(src=connection_dict["src"],
                           dest=connection_dict["dest"],
                           user=connection_dict["user"],
                           ssh_password=connection_dict["ssh_password"],
                           remote_host=connection_dict["remote_host"],
                           ssh_port=connection_dict["ssh_port"],
                           keep_days=connection_dict["keep_days"])
