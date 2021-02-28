from sanic import Sanic
from sanic import response
import jinja2
import asyncio
import config
import motor.motor_asyncio
import logging
import hashlib
import random
import aiohttp
import hcskr
import json
import pymongo.errors
import datetime
import aiocron
# Make custom Sanic Object
class AutoCovid_v2(Sanic):
    def __init__(self):
        super().__init__(__name__)
        self.dbclient=None
        self.db = None
        self.templateEnv = jinja2.Environment(loader=jinja2.FileSystemLoader('./web/'))

# Init Sanic App
app = AutoCovid_v2()
app.config['JSON_AS_ASCII'] = False
app.static('/assets', './web')
fixcors = {"Access-Control-Allow-Origin":"*"}

def md5hash(string: str):
    enc = hashlib.md5()
    enc.update(string.encode("utf8"))
    return enc.hexdigest()

# Init cron and Database
@app.listener('before_server_start')
async def notify_server_started(app, loop):
    app.dbclient = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://{config.mongo_host}:{config.mongo_port}",io_loop=loop)
    app.db = app.dbclient.AutoCovid_v2
    #cron = aiocron.crontab("* * * * *",run_autohcs,loop=loop)
    cron = aiocron.crontab("0 7 * * MON-FRI",run_autohcs,loop=loop)
    print(datetime.datetime.now())
    await app.db.hcsdata.create_index("token",unique=True)
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
        "PASSWORD": "비밀번호가 올바르지 않거나, 너무 많이 틀렸습니다.\n 다시 한번 확인후 입력해 주세요.",
        "ALREADY": "이미 등록되어 있는 정보입니다!\n매일 KST 오전 7:30분에 자동으로 자가진단을 수행합니다!\n등록 해제는 밑의 버튼을 눌러주세요!"
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
    hcsdata.update({"message": responseTexts.get(hcsdata.get("code"),hcsdata.get("message"))})
    if hcsdata.get("error"):
        return response.json(hcsdata)
    usermeta = {"name":studentname,"password":hcspassword,"birthday":birthday}
    userid = md5hash(json.dumps(usermeta))
    try:
        insert_result = await app.db.hcsdata.insert_one({"user":userid, "token": hcsdata.get("token"), "phonenumber": phonenumber})
    except pymongo.errors.DuplicateKeyError as e:
        return response.json({"error": True, "code": "ALREADY", "message": responseTexts.get("ALREADY")})
    del hcsdata['token']
    return response.json(hcsdata)

@app.route("/UnregisterHCS", methods = ["POST"])
async def route_UnregisterHCS(request):
    responseTexts = {
        "NOUSER": "유저정보를 찾을수 없습니다.\n 등록되지 않은 유저이거나,\n `생년월일, 이름, 비밀번호`를 잘못 입력하였습니다\n 다시 시도하십시오.",
        "SUCCESS": "유저의 모든 정보를\nDB에서 삭제하였습니다.\n\n 앞으로는 7:30분에 \n자가진단이 수행되지 않습니다."
    }
    post_data = request.form
    studentname = post_data.get("name")
    birthday = post_data.get("birthday")
    hcspassword = post_data.get("password")
    
    usermeta = {"name":studentname,"password":hcspassword,"birthday":birthday}
    userid = md5hash(json.dumps(usermeta))

    found_data = await app.db.hcsdata.find_one({"user":userid})
    if not found_data:
        return response.json({"error": True, "code": "NOUSER", "message": responseTexts.get("NOUSER")})
    await app.db.hcsdata.find_one_and_delete({"user":userid})
    del found_data['_id']
    found_data.update({"UnregisterTime": datetime.datetime.now()})
    await app.db.archivedhcsdata.insert_one(found_data)
    return response.json({"error": False, "code": "SUCCESS", "message": responseTexts.get("SUCCESS")})

@app.route('/headertest', methods = ['POST',"GET"])
async def testroute(request):
    request_headers = dict(request.headers)
    return response.json(request_headers)
@app.route("/runnow")
async def route_runnow(request):
    try:
        auth = request.args.get("auth")
    except:
        return response.json({"error":"Unauthorized"}, 401)
    if auth == config.authcode:
        data=await run_autohcs()
        return response.json({"result":data})
    else:
        return response.json({"error":"Forbidden"}, 403)

#@aiocron.crontab("0 0 7 ? * MON-FRI *")
#@aiocron.crontab("0 41 21 1/1 * ? *")
async def run_autohcs():
    cursor = app.db.hcsdata.find({})
    for document in await cursor.to_list(length=5000):
        try:
            hcsdata = await hcskr.asyncTokenSelfCheck(document.get("token"))
            if hcsdata.get("error"):
                print(f"ERROR!: {document.get('userid')}, {document.get('phonenumber')}, {hcsdata}")
            print(hcsdata)
        except:
            print(document)
            continue
    return True
app.run(host="0.0.0.0",port=8080, debug=True)