from flask import Flask, url_for, render_template, request, session, escape, redirect, g
import os, subprocess, signal

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

@app.route("/stop/")
def stop():
    pid = getId()
    os.kill(pid, signal.SIGTERM)
    return "stopped"

@app.route("/start/")
def start():
#    process = subprocess.Popen(["cvlc", "rtp://@225.0.0.1:12345"])
    process = subprocess.Popen(["ls", "."])
    pid = process.pid
    saveId(pid)
    return str(pid)

@app.route("/info/")
def info():
    return "living room"

# Main code (if invoked from Python at command line for development server)
if __name__ == '__main__':
    app.debug = True 
    port = int(os.environ.get('PORT', 9876))
    app.run(host='0.0.0.0', port=port)
