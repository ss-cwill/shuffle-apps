import json
import requests
#from telnetlib import TLS


from walkoff_app_sdk.app_base import AppBase

class ProofPoint(AppBase):
    __version__ = "1.0.0"
    app_name = "SS - Proofpoint Admins"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    def create_admin(
        self,
        username,
        password,
        server,
        port="10000",
        action=None,
        userid=None,
        password=None,
        fullname=None,
        emailaddress=None,
        role=None
    ):
        url_base = "https://" + server + ":" + port + "/rest/v1/administrator"
        querystring = {
            'action': action,
            'id': userid,
            'password': password,
            'full_name': fullname,
            'email': emailaddress,
            'role': role
        }
        headers = {"Accept": "application/json"}
        return requests.get(url_base,headers=headers,auth=(username,password),params=querystring,verify=False).json()

if __name__ == "__main__":
    ProofPoint.run()
