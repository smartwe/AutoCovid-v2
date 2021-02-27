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


# Make custom Sanic Object
class AutoCovid_v2(Sanic):
    def __init__(self):
        super().__init__(__name__)
        self.dbclient=None
        self.db = None
        self.templateEnv = jinja2.Environment(loader=jinja2.FileSystemLoader('src/web/'))

# Init Sanic App
app = AutoCovid_v2 ()
app.config['JSON_AS_ASCII'] = False
app.static('/assets', 'src/web')
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
async def root_route(request):
    data={"mode":"normal"}
    template = app.templateEnv.get_template('index.html')
    return response.html(template.render(data))

# Manual update cache
@app.route("/update_cache")
async def update_cache_route(request):
    await update_cache()
    return response.json({"cache":True}, headers=fixcors)

# Returns domain cache(json)
@app.route('/domains')
async def domains_route(request):
    domains = []
    for domain in app.user_cache:
        domains.append(domain.get("domain","ERROR"))
    return response.json(domains, headers=fixcors)

# Returns if email address exisiting
@app.route("/check_existing")
async def check_existing(request):
    data = request.args
    try:
        id = data['id'][0]
        domain = data['domain'][0]
        email_add = id+domain
        if email_add in app.email_cache:
            return response.json({"existing":True}, headers=fixcors)
        return response.json({"existing":False}, headers=fixcors)
    except:
        return response.json({"existing":False}, headers=fixcors)

# Returns if Promo vaild
@app.route("/check_promo", methods=["POST"])
async def check_promo(request):
    data = request.form
    if not data.get("promo"):
            return response.json({"vaild": None}, headers=fixcors)
    try:
        promo = data['promo'][0]
        promo = ObjectId(promo)
        dbdata = await app.db.promo.find_one({"_id":promo})
        if dbdata["vaild"]:
            return response.json({"vaild": dbdata['vaild'],"other":dbdata.get("other",None)}, headers=fixcors)
        else:
            return response.json({"vaild": dbdata['vaild']}, headers=fixcors)
    except: 
        return response.json({"vaild": None}, headers=fixcors)

# Makes Promo Code
@app.route("/manage_promo", methods=["POST"])
async def manage_promo(request):
    data = request.form
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://{config.domain}/admin/me",headers={"Authorization":f"Basic {data.get('auth',None)}"}) as res:
                json = await res.json()
                print(json)
                if json.get("status",None) == "ok":
                    if "admin" in json.get("privileges",[None]):
                        if data.get("mode",None) == "add":
                            other = data.get("other",None)
                            if not len(str(other)) > 4:
                                other = None
                            result=await app.db.promo.insert_one({"vaild": True,"other":other})
                            data = await app.db.promo.find_one({"_id":result.inserted_id})
                            return response.json({"promo":str(data.get("_id",None)),"vaild":data.get("vaild",None),"other":data.get("other",None)})
                        elif data.get("mode",None) == "list":
                            cursor = app.db.promo.find()
                            promos = await cursor.to_list(length=2000)
                            returndata = list()
                            for promo in promos:
                                returndata.append({"promo":str(promo.get("_id",None)),"vaild":promo.get("vaild",None),"other":promo.get("other",None)})
                            return response.json(returndata)
                    else:
                        return response.json({"error":"Forbidden"},403)
                else:
                    return response.json({"error":"Unauthorized"}, 401)
    except Exception as e:
        return response.json({"error":"Unauthorized", "Exception": e}, 401)

# Make order number, save to db
@app.route("/make_order", methods=["POST"])
async def make_order(request):
    data = request.form
    isBilling = True if data['isBilling'][0] == "true" else False
    isPromo = True if data['isPromo'][0] == "true" else False
    email = data['email'][0]
    password = data['password'][0]
    contact_email = data['contact_email'][0]
    promo = None
    if isPromo:
        promo = data['promo']
    orderId = str(datetime.datetime.now().microsecond)+str(hash(email)).replace("-","")+str(random.randint(1111,9999))
    enc_password = jwt.encode({"password":password},config.api_key)
    #jwt.decode(enc_password, config.api_key, algorithms="HS256")
    userId = md5hash(f"{contact_email}:{email}")

    await app.db.made_orders.insert_one({"userId":userId, "orderId":orderId,"email":email,"password":enc_password, "contact_email": contact_email, "isBilling": isBilling, "isPromo": isPromo, "promo": promo, "billing_amount":config.billing_amount})

    head='''
    <html>
        <head>
            <title>결제하기: My eMail Fit</title>
            <script src="https://js.tosspayments.com/v1"></script>
        </head>
        <script>
            var clientKey = '{tosspay_clientKey}';
            var tossPayments = TossPayments(clientKey);
            
    '''.format(tosspay_clientKey=config.tosspay_clientKey)
    if isBilling:
        initline = "tossPayments.requestBillingAuth('카드', {"
        body = """
                    customerKey: '{userId}',
                    successUrl: window.location.origin + '/billingProceed',
                    failUrl: window.location.origin + '/payFail',
        """.format(userId=userId)
    else:
        initline="tossPayments.requestPayment('카드', {"
        body='''
                amount: {amount},
                orderId: '{orderId}',
                orderName: '{ordername}',
                customerName: '{customer}',
                successUrl: window.location.origin + '/payProceed',
                failUrl: window.location.origin + '/payFail',
        '''.format(amount=5900, orderId = orderId, ordername=f"마이 이메일 핏: {email}", customer=contact_email)
    end="""
            });
        </script>
        <style>
        footer{
            position:absolute;
            bottom:0;
            width:100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            align-items: center;
            align-self: center;
        }
        </style>
        <footer>
        &copy; <a href="https://leok.kr">Leok.kr</a>. All Rights Reserved<br />
        상호명: 레오케이서비스(LeoK Service) 대표자: 김동현 사업자등록번호:
        225-37-00847 <br />
        유선번호: 05054061234 사업장주소: 서울특별시 강남구 압구정로 113<br />
        </footer>
    </html>
    """
    html = head+initline+body+end
    return response.html(html)
    

async def register_user(orderId):
    dbdata = await app.db.made_orders.find_one({"orderId":orderId})
    email = dbdata['email']
    password_enc = dbdata['password']
    password = jwt.decode(password_enc, config.api_key, algorithms="HS256")['password']
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://{config.domain}/admin/mail/users/add", headers={"Authorization":config.api_key}, data={"email":email,"password":password}) as res:
            text = await res.text()
            print(text)
            if "added" in text:
                return True
            return False

@app.route("/payProceed")
async def pay_proceed(request):
    data = request.args
    orderId = data["orderId"][0]
    paymentKey = data['paymentKey'][0]
    amount = data['amount'][0]
    tossApiKey = "Basic " + base64.b64encode(f"{config.tosspay_secretKey}:".encode()).decode()
    header = {"Authorization": tossApiKey, "Content-Type":"application/json"}
    data = {"orderId":orderId, "amount":amount}
    dbdata = await app.db.made_orders.find_one({"orderId":orderId})
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://api.tosspayments.com/v1/payments/{paymentKey}",headers=header, json=data) as res:
            json = await res.json()
            json.update({"contact_email":dbdata.get("contact_email",None),"email":dbdata.get("email",None), "userId":dbdata.get("userId",None)})
            await app.db.one_time_pay_report.insert_one(json)
            if json.get("status",None) == "DONE":
                if await register_user(orderId):
                    return response.redirect(f"https://{config.domain}/success/?code={dbdata['_id']}")

@app.route("/billingProceed")
async def billing_proceed(request):
    data = request.args
    userId = data['customerKey'][0]
    authKey = data['authKey'][0]
    tossApiKey = "Basic " + base64.b64encode(f"{config.tosspay_secretKey}:".encode()).decode()
    header = {"Authorization": tossApiKey, "Content-Type":"application/json"}
    db_made_orders = await app.db.made_orders.find_one({"userId":userId})
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://api.tosspayments.com/v1/billing/authorizations/{authKey}",headers=header, json={"customerKey":userId}) as res:
            json = await res.json()
            assert res.status == 200, "잘못된 빌링키 요청입니다. 홈페이지로 돌아가 다시 시도하십시오."
            json.update({"authenticatedAt":datetime.datetime.now()})
            print(json)
            await app.db.billing_data.insert_one(json)
            orderId = str(datetime.datetime.now().microsecond)+str(hash(db_made_orders['email'])).replace("-","")+str(random.randint(1111,9999))
            data = {"amount":db_made_orders['billing_amount'],"customerKey":userId, "orderId":orderId, "customerEmail": db_made_orders['contact_email'], "customerName": db_made_orders['contact_email'], "orderName": "마이 이메일 핏 정기결제"}
            async with session.post(f"https://api.tosspayments.com/v1/billing/{json['billingKey']}",headers=header, json=data) as res:
                json = await res.json()
                json.update({"contact_email":db_made_orders['contact_email'],"email":db_made_orders['email'],"userId":db_made_orders['userId']})
                await app.db.billing_report.insert_one(json)
                if json.get("status",None) == "DONE":
                    if await register_user(db_made_orders['orderId']):
                        return response.redirect(f"https://{config.domain}/success/?code={db_made_orders['_id']}")
@app.route("/payFail")
async def pay_fail(request):
    return response.json(request.args, headers=fixcors)
            
@app.route("/find_result",methods=["POST"])
async def find_result(request):
    data = request.form
    try:
        objid = ObjectId(data['code'][0])
        data = await app.db.made_orders.find_one({"_id":objid})
        return response.json({"orderId":data['orderId'],"email":data['email'],"contact_email":data['contact_email']}, headers=fixcors)
    except:
        return response.json({"error":"No matching success code"}, headers=fixcors)
    


@app.route('/test', methods = ['POST',"GET"])
async def testroute(request):
    request_headers = dict(request.headers)
    await app.db.temp.insert_one({"TEST":"ROUTE"})
    return response.json(request_headers)
@app.route('/ip', methods = ['POST',"GET"])
async def iproute(request):
    return response.text(request.ip)

app.run(host="0.0.0.0",port=12345, debug=True)