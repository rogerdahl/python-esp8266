## python-esp8266

A very thin wrapper (150 lines of code) for sending AT commands to an ESP8266 WiFi module from Python. Tested on a Raspberry Pi.

I'm using this for broadcasting UDP packages.

### General

- sendCmd(): Send an AT command with automatic retries. If retries are exhausted, the final exception is forwarded to the client. If successful, the response lines are returned in a list.
- sendBuffer(): Make a TCP or UDP connection and send a buffer. Reuses an existing connection if possible. Disconnects from old host and reconnects to new host if necessary.

### Access Point
- scanForAccessPoints()
- connectToAccessPoint(): Call is ignored if already connected to the given access point. If already connected to another access point, the old access point is automatically disconnected first.
- disconnectFromAccessPoint()
- getConnectedAccessPoint()

### CIP

- startCip()
- getCipStatus()
- closeCip()

### Device Mode

- getDeviceMode()
- setDeviceMode()

### Misc
- getIPAddress()
