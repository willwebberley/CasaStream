from flask import Flask, url_for, render_template, request, session, escape, redirect, g
import os, nmap, subprocess, signal, urllib2

app = Flask(__name__)


def search():
    nm = nmap.PortScanner()
    nm.scan(hosts='192.168.1.0-10', arguments='-p 9875')
   
    up_hosts = [] 
    for h in nm.all_hosts():
    #    print h,nm[h]['tcp'][9875]['state']
        if nm[h]['tcp'][9875]['state'] == 'open':
            up_hosts.append(str(h))

    zone_dict = {}
    for host in up_hosts:
        try:
            response = urllib2.urlopen('http://'+host+":"+str(9875)+"/info")
            zone = response.read()
            zone_dict[host] = zone
        except Exception as e:
            print "error:",host, e

    return zone_dict


def saveIds(mod1, mod2, pid):
    f = open("modules.txt", "w")
    f.write(str(mod1)+","+str(mod2)+","+str(pid))
    f.close()

def getIds():
    f = open("modules.txt", "r")
    contents = f.read()
    contents = contents.replace("\n", "")
    tokens = contens.split(",")
    return (int(tokens[0]),int(tokens[1]),int(tokens[2]))
    
def startStream():
    # enable the relevant PulseAudio modules

    # Create a sink to receive our sound
    create_sink_process = subprocess.Popen(["pactl","load-module", "module-null-sink","sink_name=casastream","format=s16be","channels=2","rate=44100"], stdout=subprocess.PIPE)
    out, err = create_sink_process.communicate()    

    # Instruct sink to forward the stream to localhost for encoding
    create_rtp_process = subprocess.Popen(["pactl","load-module","module-rtp-send","source=casastream.monitor","destination=127.0.0.1","port=46998","loop=1"], stdout = subprocess.PIPE)
    out2, err2 = create_rtp_process.communicate()

    # Use VLC to encode stream to MP3 and then broadcast through RTP
    start_vlc_encoder = subprocess.Popen(['cvlc', 'rtp://@127.0.0.1:46998', '":sout=#transcode{acodec=mp3,ab=256,channels=2}:duplicate{dst=rtp{dst=225.0.0.1,mux=ts,port=12345}}'])
    pid = start_vlc_encoder.pid

    # Save PA module IDs and the VLC process ID (so they can be killed later)
    saveIds(out, out2, pid)
        

def endStream():
    # Retrieve PA module IDs and the VLC process ID
    mod1, mod2, pid = getIds()
    
    # Kill PA modules
    subprocess.Popen(["pactl","unload-module",str(mod1)])
    subprocess.Popen(["pactl","unload-module",str(mod2)])

    # Kill VLC process
    os.kill(pid, signal.SIGTERM)


def redirectInputs():
    # First, get the id of the casastream RTP sink
    pa_sinks_process = subprocess.Popen(["pactl","list","short","sinks"], stdout = subprocess.PIPE)
    out1, err1 = pa_sinks_process.communicate()
    lines = out1.split("\n")
    sink_id = 0
    for line in lines:
        tokens = line.split()
        for token in tokens:
            if token == 'rtp':
                sink_id = tokens[0]


    # Next, get the IDs of all current inputs
    pa_inputs_process = subprocess.Popen(["pactl","list","short","sink-inputs"], stdout = subprocess.PIPE)
    out2, err2 = pa_inputs_process.communicate()
    lines = out2.split("\n")
    inputs = []
    for line in lines:
        tokens = line.split()
        if len(tokens) > 0:
            inputs.append(tokens[0])
    
    # Finally, move each input to our own sink
    for i in inputs:
        subprocess.Popen(["pactl","move-sink-input",str(i),str(sink_id)])
        


@app.route("/")
def home():
    return "test"

@app.route("/scan/", methods=["POST", "GET"])
def scan():
    zones = search()
    text = ""
    for zone in zones:
        text = text + zone + ":" + zones[zone]+"<br />"
    return text

@app.route("/start/", methods=["POST", "GET"])
def start():
    startStream()
    return "started"

@app.route("/stop/", methods=["POST", "GET"])
def stop():
    endStream()
    return "stopped"

@app.route("/sort-inputs/", methods=["POST", "GET"])
def stop():
    redirectInputs()
    return 1

@app.route("/enable-slave/<host>/")
def enable_slave(host):
    urllib2.urlopen('http://'+host+":"+str(9875)+"/start")
    return 1

@app.route("/disable-slave/<host>/")
def disable_slave(host):
    urllib2.urlopen('http://'+host+":"+str(9875)+"/stop")
    return 1


# Main code (if invoked from Python at command line for development server)
if __name__ == '__main__':
    app.debug = True 
    port = 9878
    app.run(host='0.0.0.0', port=port)
