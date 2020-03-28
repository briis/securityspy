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
                camera_model = item.findtext("devicename")
                mode_c = item.findtext("mode_c")
                mode_m = item.findtext("mode-m")
                mode_a = item.findtext("mode-a")
                recording_mode = "never"
                if mode_c == "armed":
                    recording_mode = "always"
                elif mode_m == "armed":
                    recording_mode = "motion"
                rtsp_video = "rtsp://%s:%s@%s:%s/++stream?cameraNum=%s" % (self._user, self._pass, self._host, self._port, uid)
                still_image = "http://%s:%s/++image?cameraNum=%s&auth=%s" % (self._host, self._port, uid, self._auth)

                if uid not in self.device_data:
                    item = {
                        str(uid): {
                            "name": name,
                            "online": online,
                            "rtsp_video": rtsp_video,
                            "still_image": still_image,
                            "camera_model": camera_model,
                            "recording_mode": recording_mode,
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
                    self.device_data[camera_id]["recording_mode"] = recording_mode
                    self.device_data[camera_id]["mode_a"] = mode_a
                    self.device_data[camera_id]["mode_c"] = mode_c
                    self.device_data[camera_id]["mode_m"] = mode_m


    def get_snapshot_image(self, camera_id):
        """ Returns a Snapshot image from a Camera. """

        img_uri = "http://%s:%s/++image?cameraNum=%s&auth=%s" % (self._host, self._port, camera_id, self._auth)
        response = self.req.get(img_uri)
        if response.status_code == 200:
            return response.content
        else:
            print(
                "Error Code: "
                + str(response.status_code)
                + " - Error Status: "
                + response.reason
            )
            return None

    def set_camera_recording(self, camera_id, mode):
        """ Sets the camera recoding mode to what is supplied with 'mode'.
            Valid inputs for mode: never, motion, always
        """
        if mode == "motion":
            schedule = 1
            capturemode = "M"
        elif mode == "always":
            schedule = 1
            capturemode = "C"
        else:
            schedule = 0
            capturemode = "M"

        cam_uri = "http://%s:%s/++setSchedule?cameraNum=%s&schedule=%s&mode=%s&auth=%s" % (self._host, self._port, camera_id, schedule, capturemode, self._auth)

        response = self.req.get(cam_uri)
        if response.status_code == 200:
            self.device_data[camera_id]["recording_mode"] = mode
            return True
        else:
            print(
                "Error Code: "
                + str(response.status_code)
                + " - Error Status: "
                + response.reason
            )
            return None
