CasaStream
=================


TL;DR
------

**To install:**
* Install dependencies (see below)
* Clone repository (install scripts are in the works...)

**Run the slave server (on as many devices as you like):**
* Navigate to `slave/` directory
* run `$ python2 server.py`

**Run the master server:**
* Navigate to `master/` directory
* run `$ python2 server.py`
* Navigate to [localhost:9878](http://localhost:9878) (or master's network address) and enable CasaStream
* Play your music!
* Enable from the master's web interface and select desired sound sources



About
------

CasaStream is a zoned music streamer designed for broadcasting music around a local area network. The system utilises RTP and is designed for use in homes and allows simultaneous playing of sound playing from one master server to any number of slave servers with audio output.

CasaStream runs on top of PulseAudio and can therefore stream sound from any applications captured by PulseAudio (which is usually all sound input). When running, the master server will scan for slave servers on the network and allow remote controlling of slaves so that they can be enabled and disabled when desired. A slave will start outputting sound as soon as it is enabled by the master.

The system allows for a selection of audio sources, allowing many applications to have their sound streamed simultaneously, if desired.



Deploying the servers
------------------------

The CasaStream slave servers are best deployed on always-on devices, and the server has been successfully tested on low-powered devices, such as the Raspberry Pi, to help enable this (so that you don't have to wait for devices to boot up before playing your music).

The master server requires slightly more power (due to the necessary audio encoding), so is better suited to a desktop/laptop-type machine. However, it does *kinda* work on the Raspberry Pi (with a bit of dodgy sound every now and again) - but hopefully I can try an improve this in future iterations.

All servers must be connected through a wired network. Streaming is not reliable over WLAN.




Software and Platform
----------------------

Although CasaStream itself is written in Python, and is therefore cross-platform, it is effecively only a wrapper for PulseAudio and VLC. OS X and Windows implementations of PulseAudio do exist, but it tends to be more popular on GNU/Linux systems, and thus CasaStream is designed for use on these..



Installation and running
--------------------------

Simply clone the repository, grab the dependencies (see below), navigate to either the `slave/` or `master/` directory, and run ` $ python2 server.py`.



Configuration
---------------

CasaStream is designed to work without configuration (unless you want to). Once dependencies are installed and the system is running, it should be self-organising.



Usage
------

Once the master is running, navigate to [localhost:9878](http://localhost:9878) (or use the network address if yout master server is headless) and you will be presented with the CasaStream controller. From here, you can enable CasaStream, scan for slave servers and enable the ones you want to use, and select the sound sources you want to broadcast.



Dependencies
--------------

**Master server**

* General dependencies
    * Python (designed for Python 2, untested on Python 3) - install `python2` through your system's package manager
    * `nmap` (for discovering slave servers) - install through your system's package manager (e.g. `pacman -S nmap`)
    * PulseAudio (for obvious reasons)
    * VLC (for audio encoding and RTP streaming)


* Python dependencies
    * `python-nmap` (for interfacing with `nmap`) - install through pip - e.g. `pip install python-nmap`
    * `flask` (the web server) - install through pip - e.g. `pip install flask`


**Slave server**

* General dependencies
    * Python (designed for Python2, untested on Python 3)
    * VLC (for audio playing)

* Python dependencies
    * `flask` (the web server) - install through pip - e.g. `pip install flask`
