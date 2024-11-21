import os
import time
from pathlib import Path
from typing import List

import paramiko

from .Constants import SHARED_DIR

class RemoteSSHClient:
    # Function to establish an SSH connection
    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.__connect()

    def __connect(self):
        # Create an SSH client instance
        self.ssh_client = paramiko.SSHClient()

        # Automatically add the server's host key
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Connect to the server
            self.ssh_client.connect(self.server, username=self.username, password=self.password)
        except paramiko.AuthenticationException:
            print("Authentication failed, please check your credentials")

    def __del__(self):
        self.__close()

    def __close(self):
        self.ssh_client.close()

    def get_files(self, remote_files: List[str], destination_dir: str = "."):
        sftp_client = self.ssh_client.open_sftp()
        for remote_file in remote_files:
            filepath = Path(destination_dir) / Path(remote_file).name
            Path(filepath.parent).mkdir(parents=True, exist_ok=True)
            sftp_client.get(remote_file, self.__get_filepath(filepath))
            print(f"Downloaded {filepath}")
        sftp_client.close()

    def put_files(self, local_files: List[str], destination_dir: str = SHARED_DIR):
        sftp_client = self.ssh_client.open_sftp()
        for local_file in local_files:
            filepath = Path(destination_dir) / Path(local_file).name

            sftp_client.put(local_file, self.__get_filepath(filepath),
                            lambda x, y: print(f"Progress: {x / y * 100:.0f}%"))
            print(f"Uploaded {filepath}")
        sftp_client.close()

    def put_directory(self, local_dir: str, remote_dir: str):
        sftp_client = self.ssh_client.open_sftp()

        # Recursively traverse the local directory
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_file = self.__get_filepath(os.path.join(root, file))
                remote_file = self.__get_filepath(os.path.join(remote_dir, os.path.relpath(local_file, local_dir)))

                # Ensure the remote directory exists
                try:
                    sftp_client.stat(os.path.dirname(remote_file))
                except IOError:
                    self.execute_commands([f'mkdir -p {os.path.dirname(remote_file)}'])

                sftp_client.put(local_file, remote_file, lambda x, y: print(f"Progress: {x / y * 100:.0f}%"))
                print(f"Uploaded {remote_file}")

        sftp_client.close()

    def __get_filepath(self, filepath):
        return str(filepath).replace("\\", "/")

    def execute_commands(self, commands: List[str]) -> str:
        command = " && ".join(commands)
        try:
            # Execute a command (replace this with your script execution)
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            # Read the output
            output = stdout.read().decode('utf-8')
            print(f"{command=}")
            print(output)
            error = stderr.read().decode('utf-8')
            if error:
                print(f"Error: {error}")
            return output
        except Exception as e:
            print(f"Error: {e}")
            return ""

    def execute_commands_with_sudo(self, commands: List[str]) -> str:
        command = " && ".join(commands)
        try:
            # Open a new channel with a pseudo-terminal and run a shell
            shell = self.ssh_client.invoke_shell()
            # Send the sudo command
            # noinspection PyTypeChecker
            shell.send('sudo -S ' + command + '\n')
            # Wait for the password prompt
            print("about to sleep")
            time.sleep(2)
            print("slept a bit")
            while not shell.recv_ready():
                print("sleeping")
                time.sleep(0.1)
            print("awake")
            # Send the password
            shell.send(self.password + '\n')
            time.sleep(1)
            # Receive the output
            output = shell.recv(1024).decode('utf-8')
            print(f"{command=}")
            print(f"{output=}")
            return output
        except Exception as e:
            print(f"Error: {e}")
            return ""
