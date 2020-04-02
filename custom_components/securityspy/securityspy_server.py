"""Wrapper to retrieve and Update Camera and Sensor data
   from a SecuritySpy Surveillance Server
   Specifically developed to wotk with Home Assistant
   Developed by: @briis
   Github: https://github.com/briis/securityspy
   License: MIT
"""

from datetime import datetime
import requests
import urllib.parse
import threading
import logging
import xml.etree.ElementTree as ET
from base64 import b64encode

TRIGGER_TYPE = {
    1: "Video motion detection",
    2: "Audio detection",
    4: "AppleScript",
    8: "Camera event",
    16: "Web server event",
    32: "Triggered by another camera",
    64: "Manual trigger",
    128: "Human",
    256: "Vehicle",
}

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
        self.start_event_listner()

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
                            "motion_last_trigger": None,
                            "motion_on": False,
                            "motion_trigger_type": None,
                            "motion_last_recording": None,
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
            message = "Error Code: " + str(response.status_code) + " - Error Status: " + response.reason
            logging.debug(message)
            return None

    def set_camera_recording(self, camera_id, new_mode):
        """ Sets the camera recoding mode to what is supplied with '_newmode'.
            Valid inputs for modes: never, motion, always and action
        """
        if new_mode == "motion":
            schedule = 1
            capturemode = "M"
        elif new_mode == "always":
            schedule = 1
            capturemode = "C"
        elif new_mode == "action":
            schedule = 1
            capturemode = "A"
        else:
            schedule = 0
            capturemode = "CMA"

        cam_uri = "http://%s:%s/++setSchedule?cameraNum=%s&schedule=%s&mode=%s&auth=%s" % (self._host, self._port, camera_id, schedule, capturemode, self._auth)

        response = self.req.get(cam_uri)
        if response.status_code == 200:
            self.device_data[camera_id]["recording_mode"] = new_mode
            return True
        else:
            message = "Error Code: " + str(response.status_code) + " - Error Status: " + response.reason
            logging.debug(message)
            return None

    def _event_listner(self):
        """ Threaded Event Listner """

        url = "http://%s:%s/++eventStream?version=3&format=multipart&auth=%s" % (self._host, self._port, self._auth)
        events = requests.get(url, headers=None, stream=True)
        
        if events.status_code == 200:
        
            while self.running:
                try:                
                    for line in events.iter_lines(chunk_size=200):
                        if not self.running:
                            break

                        if line:
                            data = line.decode()
                            if data[:14].isnumeric():
                                event_arr = data.split(" ")
                                camera_id = event_arr[2]
                                if event_arr[3] == "TRIGGER_M" and camera_id != "X":
                                    trigger_type = TRIGGER_TYPE[int(event_arr[4])]
                                    time_raw = event_arr[0]
                                    time_text = time_raw[:-10] + "-" + time_raw[4:-8] + "-" + time_raw[6:-6] + " " + time_raw[8:-4] + ":" + time_raw[10:-2] + ":" + time_raw[12:]
                                    self.device_data[camera_id]["motion_last_trigger"] = time_text
                                    self.device_data[camera_id]["motion_on"] = True
                                    self.device_data[camera_id]["motion_trigger_type"] = trigger_type

                                elif event_arr[3] == "FILE" and camera_id != "X":
                                    year = datetime.now().year
                                    filename = ""
                                    for x in range(4, len(event_arr)):
                                        filename = filename + event_arr[x] + " "
                                    filename = filename.rstrip()
                                    pos = filename.find("/" + str(year))
                                    webfile = urllib.parse.quote_plus(filename[pos + 1 :], safe='/')
                                    weburl = "http://%s:%s/++getfilehb/%s/%s?auth=%s" % (self._host, self._port, camera_id, webfile, self._auth)
                                    self.device_data[camera_id]["motion_last_recording"] = weburl
                                    self.device_data[camera_id]["motion_on"] = False
                                
                except Exception as ex:
                    """ Do Nothing """
                    logging.debug(ex)
                    pass

        else:
            message = "Error Code: " + str(events.status_code) + " - Error Status: " + events.reason
            logging.debug(message)
            pass                    
            
    def start_event_listner(self):
        """ Call this to start the receiver thread """
        self.running = True
        self.thread = threading.Thread(target = self._event_listner)
        self.thread.start()

    def stop_event_listner(self):
        """ Call this to stop the receiver """
        self.running = False
