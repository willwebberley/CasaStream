from flask import Flask, url_for, render_template, request, session, escape, redirect, g
import os, subprocess, signal, json

app = Flask(__name__)


def saveId(pid):
    f = open("pid.txt", "w")
    f.write(str(pid))
    f.close()

def getId():
    f = open("pid.txt", "r")
    contents = f.read()
    contents = contents.replace("\n", "")
    return int(contents)

def isEnabled():
    return os.path.isfile('pid.txt')


@app.route("/stop/")
def stop():
    pid = getId()
    os.kill(pid, signal.SIGTERM)
    try:
        os.remove("pid.txt")
    except:
        print "pid.txt does not exist"
    return "stopped"

@app.route("/start/")
def start():
    process = subprocess.Popen(["cvlc", "rtp://@225.0.0.1:12345"])
    pid = process.pid
    saveId(pid)
    return str(pid)


@app.route("/info/")
def info():
    enabled = isEnabled()
    return json.dumps({"zone":"living room","enabled":enabled})

# Main code (if invoked from Python at command line for development server)
if __name__ == '__main__':
    try:
        os.remove("pid.txt")
    except:
        print "pid.txt does not exist"
    app.debug = True 
    port = 9875
    app.run(host='0.0.0.0', port=port)
