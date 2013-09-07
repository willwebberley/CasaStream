# Copyright 2013 Will Webberley.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# The full text of the License is available from 
# http://www.gnu.org/licenses/gpl.html


from flask import Flask, url_for, render_template, request, session, escape, redirect, g
import os, subprocess, signal, json

app = Flask(__name__)
config_file = "config.json"

# Load the configuration from file
def getConfig():
    config = None
    try:
        config = open(config_file, "r").read()
        config = json.loads(config)
        name = str(config['name'])
    except Exception as e:
        print "Could not parse config file. You may need to restart the server. Writing new..."
        config = initConfig()
    return config
              
def writeConfig(config):
    f = open(config_file, "w")
    f.write(json.dumps(config))
    print "written config"
    f.close()

def initConfig():
    config = {"name":"Un-named zone"}
    writeConfig(config)
    return config

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
    if isEnabled():
            pid = getId()
            os.kill(pid, signal.SIGTERM)
            try:
                os.remove("pid.txt")
            except:
                print "pid.txt does not exist"
            return "stopped"
    return "unable to stop"

@app.route("/start/")
def start():
    if not isEnabled():
        process = subprocess.Popen(["cvlc", "rtp://@225.0.0.1:12345"])
        pid = process.pid
        saveId(pid)
        return "started"
    return "unable to start"

@app.route("/rename/<name>/")
def rename(name):
    config = getConfig()
    config['name'] = name
    writeConfig(config)
    return "success"

@app.route("/info/")
def info():
    config = getConfig()
    sys_info = os.uname()
    name = config['name']
    enabled = isEnabled()
    return json.dumps({"zone":name,"enabled":enabled,"info":sys_info})

# Main code (if invoked from Python at command line for development server)
if __name__ == '__main__':
    try:
        os.remove("pid.txt")
    except:
        print "pid.txt does not exist"
    app.debug = True 
    port = 9875
    app.run(host='0.0.0.0', port=port)
