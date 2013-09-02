from flask import Flask, url_for, render_template, request, session, escape, redirect, g
import os

app = Flask(__name__)


@app.route("/stop/")
def stop():


# Main code (if invoked from Python at command line for development server)
if __name__ == '__main__':
    app.debug = True 
    port = int(os.environ.get('PORT', 9877))
    app.run(host='0.0.0.0', port=port)
