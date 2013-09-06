from flask import Flask, url_for, render_template, request, session, escape, redirect, g
import os, nmap, subprocess, signal, urllib2, json

app = Flask(__name__)


def search():
    nm = nmap.PortScanner()
    nm.scan(hosts='192.168.1.0-20', arguments='-p 9875')
   
    up_hosts = [] 
    for h in nm.all_hosts():
    #    print h,nm[h]['tcp'][9875]['state']
        if nm[h]['tcp'][9875]['state'] == 'open':
            up_hosts.append(str(h))

    zone_list = []
    for host in up_hosts:
        try:
            response = urllib2.urlopen('http://'+host+":"+str(9875)+"/info")
            zone = response.read()
            zone_info = json.loads(zone)
            zone_dict = {}
            zone_dict['host'] = host
            zone_dict['zone'] = zone_info['zone']
            zone_dict['enabled'] = zone_info['enabled']
            zone_list.append(zone_dict)
        except Exception as e:
            print "error:",host, e

    return zone_list


def saveIds(mod1, mod2, pid):
    f = open("modules.txt", "w")
    f.write(str(mod1)+","+str(mod2)+","+str(pid))
    f.close()

def getIds():
    f = open("modules.txt", "r")
    contents = f.read()
    contents = contents.replace("\n", "")
    tokens = contents.split(",")
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
    start_vlc_encoder = subprocess.Popen(['cvlc', 'rtp://@127.0.0.1:46998', ':sout=#transcode{acodec=mp3,ab=256,channels=2}:duplicate{dst=rtp{dst=225.0.0.1,mux=ts,port=12345}}'])
    pid = start_vlc_encoder.pid
    
    print "started PA modules and encoder"
    #redirectAllInputs()

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

    try:
        os.remove("modules.txt")
    except:
        print "settings file does not exist"


def getCasaStreamSinkId():
    pa_sinks_process = subprocess.Popen(["pactl","list","short","sinks"], stdout = subprocess.PIPE)
    out1, err1 = pa_sinks_process.communicate()
    lines = out1.split("\n")
    sink_id = 0
    for line in lines:
        tokens = line.split()
        for token in tokens:
            if token == 'casastream':
                return int(tokens[0])
 

def redirectAllInputs():
    # First, get the id of the casastream RTP sink
    sink_id = getCasaStreamSinkId()    

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


def redirectInputs(inputs_to_redirect):
    # First, get the id of the casastream RTP sink
    sink_id = getCasaStreamSinkId()  

    # Get all inputs (not just those selected)
    all_inputs = getAllInputs()
    
    # Calculate which sink to send sources to which ARENT chosen:
    standard_sink = 0
    if sink_id == 0:
        standard_sink = 1    

    # Finally, move each requested input to our own sink and others to the standard_sink
    for input in all_inputs:
        id = input['id']
        if id in inputs_to_redirect:
	    print "moving input "+str(input)+" to sink "+str(sink_id)
            subprocess.Popen(["pactl","move-sink-input",str(input['id']),str(sink_id)])
        else:
            print "moving input "+str(input)+" to sink "+str(standard_sink)
            subprocess.Popen(["pactl","move-sink-input",str(input['id']),str(standard_sink)])


def getAllInputs():
    pa_sinks_process = subprocess.Popen(["pactl","list","sink-inputs"], stdout = subprocess.PIPE)
    out1, err1 = pa_sinks_process.communicate()
    lines = out1.split("\n")
    inputs = []
    current_id = 1
    current_correct_sink = False
    sink_id = getCasaStreamSinkId()
    for line in lines:
        if "Sink Input" in line:
            tokens = line.split()
            for token in tokens:
                if "#" in token:            
                    current_id = int(token.replace("#",""))
        if "application.name" in line:
            tokens = line.split('"')
            name = tokens[1].replace('"','')
            if not "vlc" in name.lower():
                inputs.append({"id":current_id,"name":name,"casastream":current_correct_sink})
        if "Sink: " in line:
            tokens = line.split()
            if int(tokens[1]) == sink_id:
                current_correct_sink = True
            else:
                current_correct_sink == False            

    return inputs
                
    
   
def isEnabled():
    return os.path.isfile('modules.txt')

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/scan/", methods=["POST", "GET"])
def scan():
    zones = search()
    return json.dumps(zones)

@app.route("/start/", methods=["POST", "GET"])
def start():
    startStream()
    return json.dumps({"started":True})

@app.route("/stop/", methods=["POST", "GET"])
def stop():
    endStream()
    return json.dumps({'stopped':True})

@app.route("/status/", methods=["POST", "GET"])
def status():
    enabled = isEnabled()
    inputs = getAllInputs()
    return json.dumps({'enabled':enabled, "inputs":inputs})

@app.route("/sort-inputs/")
def remove_inputs():
	input_list = []
	redirect_inputs(input_list)
	return json.dumps({'success':'true'})

@app.route("/sort-inputs/<inputs>/", methods=["POST", "GET"])
def sort_inputs(inputs):
    tokens = inputs.split(",")
    input_list = []
    for token in tokens:
        input_list.append(int(token))
    redirectInputs(input_list)
    return json.dumps({'success': 'true'})


@app.route("/enable-slave/<host>/")
def enable_slave(host):
    urllib2.urlopen('http://'+host+":"+str(9875)+"/start")
    return json.dumps({'success': 'true'})

@app.route("/disable-slave/<host>/")
def disable_slave(host):
    urllib2.urlopen('http://'+host+":"+str(9875)+"/stop")
    return json.dumps({'success': 'true'})



# Main code (if invoked from Python at command line for development server)
if __name__ == '__main__':
    try:
        os.remove("modules.txt")
    except:
        print "settings file does not exist" 
    app.debug = True 
    port = 9878
    app.run(host='0.0.0.0', port=port)
