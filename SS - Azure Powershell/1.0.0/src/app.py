import socket
import asyncio
import time
import random
import json
import subprocess
import base64

from walkoff_app_sdk.app_base import AppBase

# 1. Generate the api.yaml based on downloaded files
# 2. Add a way to choose the rule and the target platform for it
# 3. Add the possibility of translating rules back and forth

# 4. Make it so you can start with Mitre Att&ck techniques 
# and automatically get the right rules set up with your tools :O
class exchange_powershell(AppBase):
    __version__ = "1.0.0"
    app_name = "exchange-powershell"  

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        self.filename = "replacementfile.ps1"
        super().__init__(redis, logger, console_logger)

    def cleanup(self, item):
        newlines = []
        record = False
        skipped = 0
        for line in item.split("\n"):
            if line.startswith("{") or line.startswith("["):
                record = True

            if not record and not line.startswith("{") and not line.startswith("["):
                skipped += 1
        
            if record:
                newlines.append(line)
        
            #if "SHFFL_START" in line:
            #    record = True

        self.logger.info(f"SKIPPED {skipped} lines")
        if len(newlines) == 0:
            return item

        item = "\n".join(newlines)

        return item

    def replace_and_run(self, password, app_id, organization, command):
        data = ""
        with open(self.filename, "r") as tmp:
            data = tmp.read()

        if len(data) == 0:
            return ""

        data = data.replace("{PASSWORD}", password)
        data = data.replace("{APP_ID}", app_id)
        data = data.replace("{ORGANIZATION}", organization)
        data = data.replace("{COMMAND}", command)

        with open(self.filename, "w+") as tmp:
            tmp.write(data)

        command = f"pwsh -file {self.filename}" 
        self.logger.info(f"PRE POPEN: {command}")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,  # nosec
        )
        self.logger.info("POST STDOUT")
        stdout = process.communicate()
        self.logger.info(f"STDOUT: {stdout}")
        item = ""
        if len(stdout[0]) > 0:
            item = stdout[0]
            self.logger.info("Succesfully ran bash. Stdout: %s" % item)
        else:
            item = stdout[1]
            self.logger.info("FAILED to run bash. Stdout: %s!" % item)
            #return item

        try:
            new_cleanup = self.cleanup(item)
            if len(new_cleanup) > 0:
                item = new_cleanup
        except Exception as e:
            pass

        try:
            return item.decode("utf-8")
        except Exception as e:
            return item

        return item 



    def handle_filewriting(self, certificate):
        filedata = self.get_file(certificate)
        if filedata["success"] == False:
            return filedata

        cert = "cert.pfx"
        self.logger.info("Writing cert to file %s" % cert)
        with open(cert, "wb+") as tmp:
            tmp.write(filedata["data"])

        return filedata

    def run_custom(self, certificate, password, app_id, organization, command):
        self.logger.info("Getting: %s %s %s %s" % (certificate, password, app_id, organization))
        filedata = self.handle_filewriting(certificate)
        if filedata["success"] == False:
            return filedata

        parsed_command = command
        #if "convertto-json" not in parsed_command.lower():
        #    parsed_command = parsed_command + "| ConvertTo-Json -Depth 9"

        ret = self.replace_and_run(password, app_id, organization, parsed_command)
        return ret 

    # Write your data inside this function
    def release_quarantine_message(self, certificate, password, app_id, organization, message_id):
        self.logger.info("Getting: %s %s %s %s" % (certificate, password, app_id, organization))
        filedata = self.handle_filewriting(certificate)
        if filedata["success"] == False:
            return filedata

        parsed_command = f"Release-QuarantineMessage -Identity {message_id} | ConvertTo-Json"

        ret = self.replace_and_run(password, app_id, organization, parsed_command)
        return ret 

    # Write your data inside this function
    def preview_quarantine_message(self, certificate, password, app_id, organization, message_id):
        self.logger.info("Getting: %s %s %s %s" % (certificate, password, app_id, organization))
        filedata = self.handle_filewriting(certificate)
        if filedata["success"] == False:
            return filedata

        parsed_command = f"Preview-QuarantineMessage -Identity {message_id} | ConvertTo-Json"

        ret = self.replace_and_run(password, app_id, organization, parsed_command)
        return ret 

    # Write your data inside this function
    def export_quarantine_message(self, certificate, password, app_id, organization, message_id, skip_upload="false"):
        self.logger.info("Getting: %s %s %s %s" % (certificate, password, app_id, organization))
        filedata = self.handle_filewriting(certificate)
        if filedata["success"] == False:
            return filedata

        parsed_command = f"Export-QuarantineMessage -Identity {message_id} | ConvertTo-Json"

        ret = self.replace_and_run(password, app_id, organization, parsed_command)
        print("RET: %s" % ret)
        try:
            ret = json.loads(ret)
        except json.decoder.JSONDecodeError:
            return ret

        file_eml = ret["Eml"]
        if skip_upload == "true":
            return file_eml

        message_bytes = base64.b64decode(file_eml)
        
        fileinfo = self.set_files({
            "filename": f"{message_id}.eml", 
            "data": message_bytes 
        })

        if len(fileinfo) == 1:
            return {
                "success": True,
                "file_id": fileinfo[0]
            }
        return fileinfo

    # Write your data inside this function
    def delete_quarantine_message(self,  certificate, password, app_id, organization, message_id):
        self.logger.info("Getting: %s %s %s %s" % (certificate, password, app_id, organization))
        filedata = self.handle_filewriting(certificate)
        if filedata["success"] == False:
            return filedata

        parsed_command = f"Delete-QuarantineMessage -Identity {message_id} | ConvertTo-Json"

        ret = self.replace_and_run(password, app_id, organization, parsed_command)
        return ret 

    # Write your data inside this function
    def get_quarantine_message(self,  certificate, password, app_id, organization, message_id):
        self.logger.info("Getting: %s %s %s %s" % (certificate, password, app_id, organization))
        filedata = self.handle_filewriting(certificate)
        if filedata["success"] == False:
            return filedata

        parsed_command = f"Get-QuarantineMessage {message_id} | ConvertTo-Json"

        ret = self.replace_and_run(password, app_id, organization, parsed_command)
        return ret 

    # Write your data inside this function
    def get_quarantine_messages(self, certificate, password, app_id, organization, time_from, time_to):
        self.logger.info("Getting: %s %s %s %s" % (certificate, password, app_id, organization))
        filedata = self.handle_filewriting(certificate)
        if filedata["success"] == False:
            return filedata

        #parsed_command = f"Get-QuarantineMessage -StartReceivedDate {time_from} -EndReceivedDate {time_to} | ConvertTo-Json"
        #parsed_command = f"Get-QuarantineMessage -StartReceivedDate {time_from} -EndReceivedDate {time_to}"
        parsed_command = f"Get-QuarantineMessage -PageSize 50 -Page 1"


        ret = self.replace_and_run(password, app_id, organization, parsed_command)
        return ret 

    # Write your data inside this function
    def get_quarantine_messageheaders(self, certificate, password, app_id, organization, message_id):
        self.logger.info("Getting: %s %s %s %s" % (certificate, password, app_id, organization))
        filedata = self.handle_filewriting(certificate)
        if filedata["success"] == False:
            return filedata

        parsed_command = f"Get-QuarantineMessageHeader {message_id} | ConvertTo-Json"

        ret = self.replace_and_run(password, app_id, organization, parsed_command)
        return ret 

if __name__ == "__main__":
    exchange_powershell.run()