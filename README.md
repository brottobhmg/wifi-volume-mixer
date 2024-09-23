# wifi-volume-mixer
Python script to control the volume of audio applications in Windows using a flutter app.



## How it works
**Python script** assign to the network interface a mDNS to bind with the App in all the networks.
It launch one thread (webserver) to manage the request from the app, one thread to send data using UDP to the App and one thread to handle the update name and volume of the sliders.

The App show the sliders and allow the user to interact with them. It also have a demo screen accessible with the 'play' icon on the appbar.


