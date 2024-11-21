from dotenv import dotenv_values

DEFAULT_NODE = "gl4"


class CredentialManager:
    env_values = dotenv_values("../.env")

    @classmethod
    def get_credentials_for_node(cls, node) -> (str, str, str):
        server_ip = cls.env_values.get(f"{node.upper()}-SERVER_IP")
        username = cls.env_values.get("USERNAME")
        password = cls.env_values.get("PASSWORD")
        return server_ip, username, password
