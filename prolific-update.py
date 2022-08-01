from typing import List
import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime
import time
import os
from plyer import notification  # for getting notification on your PC
import webbrowser
import argparse
import json

class ProlificUpdater:
    def __init__(self, bearer, participantId):
        self.bearer = bearer
        self.oldResults = list()
        self.participantId = participantId

    def getRequestFromProlific(self):
        url = "https://internal-api.prolific.co/api/v1/studies/?current=1"
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json, text/plain, */*"
        headers["Authorization"] = self.bearer
        return requests.get(url, headers=headers)

    def reservePlace(self, id):
        url = "https://internal-api.prolific.co/api/v1/submissions/reserve/"
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = self.bearer
        postObj = {"study_id": id, "participant_id": self.participantId}
        return requests.post(url, headers=headers, data = postObj)

    def getResultsFromProlific(self):
        try:
            response = self.getRequestFromProlific()
        except:
            print("network error")
            notification.notify(
                # title of the notification,
                title="Prolific update error {}".format(datetime.now().strftime("%H:%M:%S")),
                app_name="Prolific updater",
                # the body of the notification
                message="Network error!",
                # creating icon for the notification
                # we need to download a icon of ico file format
                app_icon="Paomedia-Small-N-Flat-Bell.ico",
                # the notification stays for 50sec
                timeout=50
            )
            return list()
        if response.status_code == 200:
            return response.json()['results']
        else:
            print("Response error {}".format(response.status_code))
            print("Response error {}".format(response.reason))
            notification.notify(
                # title of the notification,
                title="Prolific update error {}".format(datetime.now().strftime("%H:%M:%S")),
                app_name="Prolific updater",
                # the body of the notification
                message="Bearer error!",
                # creating icon for the notification
                # we need to download a icon of ico file format
                app_icon="Paomedia-Small-N-Flat-Bell.ico",
                # the notification stays for 50sec
                timeout=50
            )
            return list()


    def saveToFile(self, toWrite):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filePath = dir_path + '/prolific.log'
        with open(filePath, 'a+') as file:
            current_time = datetime.now().strftime("%H:%M:%S")
            print("saving to ", filePath)
            file.write(current_time)
            file.write('\n')
            file.write(toWrite)
            file.write('\n\n')


    def executeCycle(self):
        results = self.getResultsFromProlific()
        if results:
            if results != self.oldResults:
                self.reservePlace(results[0]["id"])
                notification.notify(
                    # title of the notification,
                    title="Prolific update {}".format(datetime.now().strftime("%H:%M:%S")),
                    app_name="Prolific updater",
                    # the body of the notification
                    message="New studies available!",
                    # creating icon for the notification
                    # we need to download a icon of ico file format
                    app_icon="Paomedia-Small-N-Flat-Bell.ico",
                    # the notification stays for 50sec
                    timeout=50
                )
                a_website = "https://app.prolific.co/studies"  # TODO: open url in results
                webbrowser.open_new_tab(a_website)
            self.saveToFile(json.dumps(results))
        
        self.oldResults = results
        
        if results:
            return True
        else:
            return False

def parseArgs():
    parser = argparse.ArgumentParser(description='Keep updated with Prolific')
    parser.add_argument('-b', '--bearer', type=str, help='bearer token')
    parser.add_argument('-i', '--id', type=str, help='participant id')
    args = parser.parse_args()
    return {"bearer": "Bearer " + args.bearer, "id": args.id}

myArguments = parseArgs()

p_updater = ProlificUpdater(bearer=myArguments["bearer"], participantId=myArguments["id"])

while (True):
    updateTime = 5
    if(p_updater.executeCycle()):
        updateTime = 15
    else:
        updateTime = 5
    # sleep for 5 sec
    time.sleep(updateTime)
