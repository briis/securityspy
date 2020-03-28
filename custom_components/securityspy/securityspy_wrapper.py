"""Wrapper to retrieve and Update Camera and Sensor data
   from a SecuritySpy Surveillance Server
   Specifically developed to wotk with Home Assistant
   Developed by: @briis
   Github: https://github.com/briis/securityspy
   License: MIT
"""

from datetime import datetime
import requests
import xml.etree.ElementTree as ET
from base64 import b64encode

class securityspySvr:
    """ Main Class to retrieve data from the SecuritySpy Server """

    def __init__(self, Host, Port, User, Pass, ssl):
        super().__init__()
        self._host = Host
        self._port = Port
        self._user = User
        self._pass = Pass
        self._ssl = ssl
        self._error = None
        self.device_data = {}

        self._auth = b64encode(bytes(self._user + ":" + self._pass,"utf-8")).decode()
        self.req = requests.session()
        self.update()

    @property
    def devices(self):
        """ Returns a JSON formatted list of Devices. """
        return self.device_data

    def update(self):
        """Updates the status of devices."""
        self._get_camera_list()

    def _get_camera_list(self):
        """ Retrieves a list of all Cameras on the Server """

        url = 'http://%s:%s/++systemInfo&auth=%s' % (self._host, self._port, self._auth)
        print(url)

        response = self.req.get(url)
        if response.status_code == 200:
            decoded_content = response.content.decode("utf-8")
            cameras = ET.fromstring(decoded_content)

            for item in cameras.iterfind('cameralist/camera'):
                uid = item.findtext("number")
                # Get if camera is online
                if item.findtext("connected") == "yes":
                    online = True
                else:
                    online = False
                name = item.findtext("name")
                image_width = item.findtext("width")
                image_height = item.findtext("height")
                mdsensitivity = item.findtext("mdsensitivity")
                mode = item.findtext("mode")
                mode_c = item.findtext("mode_c")
                mode_m = item.findtext("mode-m")
                mode_a = item.findtext("mode-a")
                live_image = "http://%s:%s/++video?cameraNum=%s&auth=%s" % (self._host, self._port, uid, self._auth)
                still_image = "http://%s:%s/++image?cameraNum=%s&auth=%s" % (self._host, self._port, uid, self._auth)

                if uid not in self.device_data:
                    item = {
                        str(uid): {
                            "name": name,
                            "online": online,
                            "live_image:": live_image,
                            "still_image": still_image,
                            "mode": mode,
                            "mode_c": mode_c,
                            "mode_m": mode_m,
                            "mode_a": mode_a,
                            "motion_sensitivity": mdsensitivity,
                            "image_width": image_width,
                            "image_height": image_height,
                        }
                    }
                    self.device_data.update(item)
                else:
                    camera_id = item.findtext('number')
                    self.device_data[camera_id]["online"] = online
                    self.device_data[camera_id]["mode_a"] = mode_a
                    self.device_data[camera_id]["mode_c"] = mode_c
                    self.device_data[camera_id]["mode_m"] = mode_m

