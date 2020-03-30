# SecuritySpy for Home Assistant

This is a Home Assistant Integration for [Ben Softwares](https://www.bensoftware.com) SecuritySpy Surveillance system.

Basically what this does, is integrating the Camera feeds from SecuritySpy in to Home Assistant, adds switches to adjust recording settings, adds Binary Motion Sensors to show if motion has occured and Sensors that show the current Recording Settings pr. camera.

**Note**: There is a know bug in the Python library *urllib3* which might show a Warning like the below in the Event Log:
`Failed to parse headers (url=http://192.168.x.x:8000/++eventStream?version=3&format=multipart&auth=ABCDEFGHIJKLMN): [StartBoundaryNotFoundDefect(), MultipartInvariantViolationDefect()], unparsed data: ''`

This warning can be ignored, and the Integration will still work as expected.

## Prerequisites

Before you install this Integration you need to ensure that the following settings are applied in SecuritySpy:


**This program is under development and no working code is currently available**
