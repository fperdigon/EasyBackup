# apt install rsync open-ssh sshpass openssl

import subprocess
import datetime
import re
from utils.logger import logger  # Import the shared logger


def test_ssh_connection_with_sshpass(host, port=22, username=None, password=None, timeout=5):
    """
    Test SSH connection using sshpass for password authentication and subprocess.

    Args:
    - host (str): The remote server's hostname or IP address.
    - port (int, optional): SSH port (default is 22).
    - username (str): SSH username.
    - password (str): SSH password for authentication.
    - timeout (int, optional): Connection timeout in seconds.

    Returns:
    - bool: True if connection is successful, False otherwise.
    - str: Error message if connection fails.
    """
    if not password:
        return False, "Password is required when using sshpass."

    # Create the sshpass command using password and ssh
    ssh_command = [
        "sshpass", "-p", password, "ssh", "-o", f"ConnectTimeout={timeout}", "-p", str(port),
        f"{username}@{host}", "exit"
    ]

    try:
        # Run SSH command with sshpass
        result = subprocess.run(ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)

        if result.returncode == 0:
            return True, "SSH connection successful."
        else:
            # If returncode is non-zero, check for authentication or other errors
            if "Permission denied" in result.stderr or "Authentication failed" in result.stderr:
                return False, "Authentication failed: Incorrect username or password."
            else:
                return False, f"SSH connection failed: {result.stderr.strip()}"

    except subprocess.TimeoutExpired:
        return False, "SSH connection timed out."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def parse_rsync_current_file(line):
    """
    Extract the filename from a line of rsync output.
    
    Args:
    - line: A line of output from rsync, e.g. "file1.txt" or "          100 100%    0.00kB/s    0:00:00 (xfr#1, to-chk=9/10)"
    
    Returns:
    - filename: The extracted filename, or None if no filename is found.
    """
    # Regex to match lines that look like filenames (e.g., containing a dot)
    filename_match = re.match(r"^\s*([^\s]+\.\S+)$", line)  # Match lines with a dot (e.g., file extensions)
    
    if filename_match:
        return filename_match.group(1).strip()  # Remove leading/trailing whitespace
    return None


def parse_rsync_progress(line):
    """
    Parse a single line of rsync progress output to extract transferred bytes, percentage,
    and incremental recursion check (ir-chk).
    
    Args:
    - line: A line of output from rsync, e.g. "10,220,696   0%  522.43kB/s    0:00:19 (xfr#1772, ir-chk=1389/18955)"
    
    Returns:
    - transferred: The transferred bytes as an integer.
    - percent: The progress percentage as an integer.
    - ir_chk_current: The current file number (int).
    - ir_chk_total: The total number of files (int).
    """
    # Regex to match the transferred bytes, percentage, and ir-chk values
    match = re.match(r"\s*(\d[\d,]*)\s+(\d+)%\s+([\d.]+[kMG]?B/s)\s+([\d:]+)\s+\(xfr#(\d+),\s*ir-chk=(\d+)/(\d+)\)", line)
    out_dict = None
    if match:
        out_dict = {
            "Bytes Transferred": match.group(1).replace(",", ""),  # Remove commas
            "Percentage": match.group(2),
            "Speed": match.group(3),
            "Time": match.group(4),
            "Xfr Number": match.group(5),
            "IR-Chk Numerator": match.group(6),
            "IR-Chk Denominator": match.group(7)
        }
    return out_dict


def run_incremental_backup(src, dest, user, remote_host, ssh_password, ssh_port=22, keep_days=None):
    """
    Perform incremental backups using rsync with SSH password authentication and show overall progress.

    Parameters:
        src (str): Local source directory.
        dest (str): Remote backup directory.
        user (str): SSH username.
        remote_host (str): Remote server address.
        ssh_password (str): SSH password for authentication.
        ssh_port (int): SSH port.
        keep_days (int): Number of days to keep old backups.
    """

    success, message = test_ssh_connection_with_sshpass(host=remote_host, port=ssh_port, username=user, password=ssh_password)

    if success:
        logger.info("SSH connection sucessful")

        date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        new_backup = f"{dest}/{date_str}"
        latest = f"{dest}/latest"

        # SSH command with password authentication using sshpass
        ssh_cmd = f"sshpass -p '{ssh_password}' ssh -p {ssh_port}"

        # Find the previous backup
        get_prev_cmd = f"{ssh_cmd} {user}@{remote_host} 'readlink {latest}'"
        try:
            prev_backup = subprocess.check_output(get_prev_cmd, shell=True, text=True).strip() 
        except subprocess.CalledProcessError:
            prev_backup = ""

        logger.info(f"Previous backup found: {prev_backup}")    

        # Create new backup directory on remote server
        process = subprocess.run(f"{ssh_cmd} {user}@{remote_host} 'mkdir -p {new_backup}'", shell=True, check=True)        

        # Rsync command with password authentication and progress tracking
        rsync_base = "rsync -a --delete --info=progress2 --progress"
        rsync_ssh = f"-e 'sshpass -p \"{ssh_password}\" ssh -p {ssh_port}'"
        
        if prev_backup:
            rsync_cmd = f"{rsync_base} --link-dest={prev_backup} {rsync_ssh} {src} {user}@{remote_host}:{new_backup}"
        else:
            rsync_cmd = f"{rsync_base} {rsync_ssh} {src} {user}@{remote_host}:{new_backup}"

        logger.info(f"Used rsync command: {rsync_cmd.replace(ssh_password, '********')}")

        # Run rsync with real-time progress tracking
        process = subprocess.Popen(rsync_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        for line in process.stdout:
            # sys.stdout.write(line)
            # sys.stdout.flush()
            logger.debug(f"process.stdout: {line}")            
            
            # Parse currrent file
            parsed_rsync_current_file = parse_rsync_current_file(line)

            # Parse transferred bytes, percentage, and ir-chk from each rsync line
            parsed_rsync_progress = parse_rsync_progress(line)

            if parsed_rsync_current_file is not None:
                logger.debug(f"Current file: {parsed_rsync_current_file}")

            if parsed_rsync_progress is not None:            
                logger.debug(f"Overall Progress: {parsed_rsync_progress['Percentage']}% "
                            f"Speed: {parsed_rsync_progress['Speed']} "
                            f"Bytes Transferred: ({parsed_rsync_progress['Bytes Transferred']} bytes) | "
                            f"File {parsed_rsync_progress['IR-Chk Numerator']}/"
                            f"{parsed_rsync_progress['IR-Chk Denominator']}")
              
        # Wait for rsync to finish
        process.wait()

        # Update the "latest" symlink
        update_symlink_cmd = f"{ssh_cmd} {user}@{remote_host} 'rm -f {latest} && ln -s {new_backup} {latest}'"
        subprocess.run(update_symlink_cmd, shell=True, check=True)

        # Optional: Delete old backups
        if keep_days:
            delete_old_cmd = f"{ssh_cmd} {user}@{remote_host} 'find {dest} -maxdepth 1 -type d -mtime +{keep_days} -exec rm -rf {{}} \;'"
            subprocess.run(delete_old_cmd, shell=True, check=True)

        logger.info("Backup completed!")

    else:
        logger.info("SSH connection unsucesfull")


# Example Usage:
# incremental_backup("/local/source/", "/backup", "user", "remote.server.com", "your_password")



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
    
    from credentials_raw_testing_DO_NOT_ADD_TO_REPO import connections_dict
    connection_dict = connections_dict["NAS No Key"]

    run_incremental_backup(src=connection_dict["src"],
                           dest=connection_dict["dest"],
                           user=connection_dict["user"],
                           ssh_password=connection_dict["ssh_password"],
                           remote_host=connection_dict["remote_host"],
                           ssh_port=connection_dict["ssh_port"],
                           keep_days=connection_dict["keep_days"])

    
