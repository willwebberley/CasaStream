from flask import Flask, url_for, render_template, request, session, escape, redirect, g
import os, nmap

app = Flask(__name__)


def search():
    nm = nmap.PortScanner()
    nm.scan(hosts='192.168.1.4', arguments='-p 9875')
    hosts_list = [(x, nm[x]['status']['state']) for x in nm.all_hosts()]
    
    for host, status in hosts_list:
        print('{0}:{1}'.format(host, status))
    return hosts_list

@app.route("/")
def home():
    stuff = search()
    return "test"


# Main code (if invoked from Python at command line for development server)
if __name__ == '__main__':
    app.debug = True 
    port = int(os.environ.get('PORT', 9878))
    app.run(host='0.0.0.0', port=port)
