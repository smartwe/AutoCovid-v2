from sanic import Sanic
from sanic import response
import jinja2
import asyncio
import config
import motor.motor_asyncio
import logging
import datetime
import base64
from bson.objectid import ObjectId
import hashlib
import random
import aiohttp
import hcskr
import json
import pymongo.errors

# Make custom Sanic Object
class AutoCovid_v2(Sanic):
    def __init__(self):
        super().__init__(__name__)
        self.dbclient=None
        self.db = None
        self.templateEnv = jinja2.Environment(loader=jinja2.FileSystemLoader('./web/'))

# Init Sanic App
app = AutoCovid_v2 ()
app.config['JSON_AS_ASCII'] = False
app.static('/assets', './web')
fixcors = {"Access-Control-Allow-Origin":"*"}

def md5hash(string: str):
    enc = hashlib.md5()
    enc.update(string.encode("utf8"))
    return enc.hexdigest()

# Load Database Server
@app.listener('before_server_start')
async def notify_server_started(app, loop):
    app.dbclient = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://{config.mongo_host}:{config.mongo_port}",io_loop=loop)
    app.db = app.dbclient.AutoCovid_v2
    await app.db.temp.insert_one({"TEMP":"VALUE"})
    print('Server Started!')


# Render Homepage
@app.route('/')
async def route_root(request):
    data={"mode":"normal"}
    template = app.templateEnv.get_template('index.html')
    return response.html(template.render(data))

@app.route("/RegisterHCS", methods=["POST"])
async def route_RegisterHCS(request):
    responseTexts = {
        "SUCCESS": "성공적으로 등록되었습니다!\n 매일 KST 오전 7:30분에 자동으로 자가진단을 수행합니다!\n등록 해제는 밑의 버튼을 눌러주세요!",
        "FORMET": "찾을수 없는 학교입니다.\n 교육청과 학교명을 올바르게 입력했는지 \n다시 한번 확인해 주세요.",
        "NOSTUDENT": "학생정보가 올바르지 않습니다.\n 학교정보는 올바르나, 학생인증에 실패하였습니다.\n 다시 한번 확인해 주세요.",
        "PASSWORD": "비밀번호가 올바르지 않거나, 너무 많이 틀렸습니다.\n 다시 한번 확인후 입력해 주세요."
        }

    post_data = request.form
    studentname = post_data.get("name")
    birthday = post_data.get("birthday")
    region = post_data.get("region")
    schoolname = post_data.get("schoolname")
    schoollevel = post_data.get("level")
    hcspassword = post_data.get("password")

    phonenumber = post_data.get("phonenumber")

    hcsdata = await hcskr.asyncGenerateToken(studentname, birthday, region, schoolname, schoollevel, hcspassword)
    if hcsdata.get("error"):
        return response.json(hcsdata)
    usermeta = {"name":studentname,"schoolname":schoolname,"birthday":birthday}
    userid = md5hash(json.dumps(usermeta))
    try:
        insert_result = await app.db.hcsdata.insert_one({"user":userid, "token": hcsdata.get("token")})
    except pymongo.errors.DuplicateKeyError as e:
        return response.json({"error": True, "code": "ALREADY", "message": "이미 등록되어 있는 정보입니다! 등록해제는 아래의 등록해제 버튼을 눌러주세요!"})
    return response.json("error": False, "code": "SUCCESS", "message": "성공적으로 등록하였습니다!")


@app.route('/test', methods = ['POST',"GET"])
async def testroute(request):
    request_headers = dict(request.headers)
    await app.db.temp.insert_one({"TEST":"ROUTE"})
    return response.json(request_headers)
@app.route('/ip', methods = ['POST',"GET"])
async def iproute(request):
    return response.text(request.ip)

app.run(host="0.0.0.0",port=12345, debug=True)