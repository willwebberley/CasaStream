from flask import Flask, url_for, render_template, request, session, escape, redirect, g
import os, nmap, subprocess, signal

app = Flask(__name__)


def search():
    nm = nmap.PortScanner()
    nm.scan(hosts='192.168.1.4', arguments='-p 9875')
    hosts_list = [(x, nm[x]['status']['state']) for x in nm.all_hosts()]
    
    for host, status in hosts_list:
        print('{0}:{1}'.format(host, status))
    return hosts_list


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
    #first, get the id of the casastream RTP sink:
    
 
@app.route("/")
def home():
#    stuff = search()
    startStream()
    return "test"




# Main code (if invoked from Python at command line for development server)
if __name__ == '__main__':
    app.debug = True 
    port = int(os.environ.get('PORT', 9878))
    app.run(host='0.0.0.0', port=port)
