# TODO: Possible fix to avoid storing pass
# create key for the program
# ssh-keygen -t rsa -b 4096 -f ~/.ssh/easybackup_key -N ""
# ssh-copy-id -i ~/.ssh/easybackup_key.pub -p <ssh_port> <user>@<remote_host>
# or
# cat ~/.ssh/backup_key.pub | ssh -p <ssh_port> <user>@<remote_host> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
# test connection whithout a pasword
# ssh -i ~/.ssh/backup_key -p <ssh_port> <user>@<remote_host>

def create_backup_config(BACKUP_CONFIGS):
    pass