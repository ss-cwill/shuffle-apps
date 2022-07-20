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
        apiusername,
        apipassword,
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
            'id': userid,
            'password': password,
            'full_name': fullname,
            'email': emailaddress,
            'role': role
        }
        headers = {"Accept": "application/json"}
        send_request = requests.post(url_base,headers=headers,auth=(apiusername,apipassword),params=querystring,verify=False).json()
        return send_request
         
    def delete_admin(
        self,
        apiusername,
        apipassword,
        server,
        port="10000",
        action=None,
        userid=None
    ):
        url_base = "https://" + server + ":" + port + "/rest/v1/administrator/" + userid
        headers = {"Accept": "application/json"}
        send_request = requests.delete(url_base,headers=headers,auth=(apiusername,apipassword),verify=False).json()
        return send_request

    def list_admins(
        self,
        apiusername,
        apipassword,
        server,
        port="10000",
        action=None
    ):
        url_base = "https://" + server + ":" + port + "/rest/v1/administrator"
        headers = {"Accept": "application/json"}
        send_request = requests.get(url_base,headers=headers,auth=(apiusername,apipassword),verify=False).json()
        return send_request

if __name__ == "__main__":
    ProofPoint.run()
