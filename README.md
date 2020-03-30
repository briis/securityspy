# SecuritySpy for Home Assistant

This is a Home Assistant Integration for [Ben Softwares](https://www.bensoftware.com) SecuritySpy Surveillance system.

Basically what this does, is integrating the Camera feeds from SecuritySpy in to Home Assistant, adds switches to adjust recording settings and adds Binary Motion Sensors to show if motion has occured.

**Note**: There is a know bug in the Python library *urllib3* which might show a Warning like the below in the Event Log:

`Failed to parse headers (url=http://192.168.x.x:8000/++eventStream?version=3&format=multipart&auth=ABCDEFGHIJKLMN): [StartBoundaryNotFoundDefect(), MultipartInvariantViolationDefect()], unparsed data: ''`

This warning can be ignored, and the Integration will still work as expected.

## Prerequisites

Before you install this Integration you need to ensure that the following settings are applied in SecuritySpy:

![Web Server Setup](https://github.com/briis/securityspy/blob/master/support_files/secspy_webserver.png) ![User Setup](https://github.com/briis/securityspy/blob/master/support_files/secspy_users.png) 

*To be updated...*

**This program is under development. The code in here might work. Once this message is removed, the code should be finished.**
