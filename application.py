import os, requests, json, boto3

from flask import flash, Flask, session, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_session import Session
from werkzeug.utils import secure_filename
from config import AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
bucket_name = 'thesis-image'

Session(app)

s3 = boto3.client(
    "s3",
    aws_access_key_id = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY
)


bucket_resource = s3

channels=dict()

@app.route("/")
def index():
    global channels
    if 'channel' in session:
        achannel = session['channel']
        ch_mess = channels[achannel]
        name = session['user']
        return render_template("chat.html",ch_mess=ch_mess,achannel=achannel,name=name)
    else:
        return render_template("index.html")

@app.route("/signin")
def signin():
    return render_template("index.html")

@app.route("/channel", methods=["POST"])
def channel():
    name = request.form.get("name")
    if name and (not name.isspace()):
        session["user"] = name
        return render_template("channel.html", name=name,channels=channels)
    else:
        return render_template("errorname.html", message="invalid name")

@app.route('/upload_file', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        bucket_resource.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file.content_type
            }
        )
        return redirect('/')

@app.route("/newchannel", methods=["GET", "POST"])
def newchannel():
    global channels
    if request.method == "POST":
        newchannel = request.form.get("newchannel")
        for achannel in channels:
            if achannel == newchannel:
                return render_template("errorchannel.html", message="existing channel")
        print(newchannel)
        channels[newchannel] = dict()
        print(channels)
        name = session['user']
        return render_template("channel.html", name=name,channels=channels)
    else:
        name = session['user']
        return render_template("channel.html", name=name,channels=channels)

@app.route("/chat/<achannel>")
def chat(achannel):
    global channels
    session['channel']=achannel
    ch_mess = channels[achannel]
    name = session['user']
    return render_template("chat.html",ch_mess=ch_mess,achannel=achannel,name=name)

totalnum = 3

@socketio.on("submit mess")
def message(data):
    global num
    global totalnum
    global channels
    content = data["content"]
    time = data["time"]
    name = session['user']
    channel = data["channel"]

    if len(channels[channel]) < totalnum:
        num = len(channels[channel]) + 1
        channels[channel][num] = {}
        channels[channel][num][name] = {}
        channels[channel][num][name][time] = {}
        channels[channel][num][name][time] = content
    else:
        ite = 1
        while ite < totalnum:
            del channels[channel][ite]
            channels[channel][ite] = {}
            n1 = list(channels[channel][ite+1])[0]
            channels[channel][ite][n1] = {}
            t1 = list(channels[channel][ite+1][n1])[0]
            channels[channel][ite][n1][t1] = {}
            channels[channel][ite][n1][t1] = channels[channel][ite+1][n1][t1]
            ite = ite +1
        del channels[channel][totalnum]
        channels[channel][totalnum] = {}
        channels[channel][totalnum][name] = {}
        channels[channel][totalnum][name][time] = {}
        channels[channel][totalnum][name][time] = content
    emit("mess totals", channels[channel], broadcast=True)
