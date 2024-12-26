from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from utils import hash_password, verify_password
from core.db import connect
from models.masterApiModel import db_select, db_Insert
from datetime import datetime
import datetime as dt
# import ssl

app = FastAPI()

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# ssl_context.load_cert_chain('./certificate/certificate.pem', keyfile='./certificate/key.pem')

if __name__ == "__main__":
#    uvicorn.run("main:app", host="0.0.0.0", port=3001, ssl=ssl_context, reload=True)
   uvicorn.run("main:app", host="0.0.0.0", port=3005, reload=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get('/gen_pass')
def generatePassword(string):
    haspass=hash_password(string)
    return {"pass": haspass}

class UserLogin(BaseModel):
    user_id:str
    password:str

@app.post('/login')
async def login(data:UserLogin):
    print('I am here')
    print(data)
    res_dt = {}

    select = "a.*"
    schema = "md_user a"
    where = f"a.user_id='{data.user_id}'"
    order = ""
    flag = 0
    
    result = await db_select(select, schema, where, order, flag)
    # print(result['msg']['password'], 'PWDD STRING')
    if(result['suc'] > 0 and result['suc'] < 2):
        # print(verify_password(data.password, result['msg']['password']), 'CHECK PASSWOD')
        if(verify_password(data.password, result['msg']['password'])):
            res_dt = {"suc": 1, "msg": result['msg']}
        else:
            res_dt = {"suc": 2, "msg": "Please check your userID or password"}
    elif(result['suc'] == 2):
        res_dt = {"suc": 2, "msg": "Please check your userID or password"}
    else:
        res_dt = {"suc": 0, "msg": "No Data Found"}

    return res_dt

class FromEntry(BaseModel):
    dc_no:str
    trader_id:str
    farmer_id:str
    site:str
    sup_name:str
    schedule_no:str
    date:str
    scale_no:str
    vehicle_no:str
    driver_name:str
    slip_no:str
    lot_no:str
    start_dt:str
    end_dt:str

class BirdWeight(BaseModel):
    qty:str
    weight:str

class Bill(BaseModel):
    net_qty:str
    net_weight:str
    avg_weight:str
    remarks:str

class Collection(BaseModel):
    form_dt: FromEntry
    birdWeight: list[BirdWeight]
    lameBirdWeight: list[BirdWeight]
    bill: Bill

@app.post('/collection')
async def save_collection(data: Collection):
    # print(data.form_dt.dc_no)
    current_datetime = datetime.now()
    curr_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    entry_dt_obj = datetime.strptime(data.form_dt.date, "%d/%m/%Y")
    entry_dt = entry_dt_obj.strftime("%Y-%m-%d")
    # print(entry_dt, 'LALALALALA')

    start_dt_obj = datetime.strptime(data.form_dt.start_dt, "%Y-%m-%d %H:%M:%S.%f")
    start_dt = start_dt_obj.strftime("%Y-%m-%d %H:%M:%S")

    # print(start_dt, 'LULULULULU')

    table_name= 'td_collection'
    fields= 'dc_no, trader_id, farmer_id, site_id, super_id, schedule_no, entry_date, scale_no, vehicle_no, driver_id, slip_no, lot_no, str_dt, end_dt, net_qty, net_weight, avg_weight, remarks, created_by, created_dt'
    values= f"'{data.form_dt.dc_no}', '{data.form_dt.trader_id}', '{data.form_dt.farmer_id}', '{data.form_dt.site}', '{data.form_dt.sup_name}', '{data.form_dt.schedule_no}', '{entry_dt}', '{data.form_dt.scale_no}', '{data.form_dt.vehicle_no}', '{data.form_dt.driver_name}', '{data.form_dt.slip_no}', '{data.form_dt.lot_no}', '{start_dt}', '{curr_date}', '{data.bill.net_qty}', '{data.bill.net_weight}', '{data.bill.avg_weight}', '{data.bill.remarks}', 'admin', '{curr_date}'"
    whr= ''
    flag = 0
    result = await db_Insert(table_name, fields, values, whr, flag)

    if(result['suc'] > 0):
        # print(data.birdWeight)
        if(len(data.birdWeight) > 0):
            i = 1
            for dt in data.birdWeight:
                weight = dt.weight.split(' ')
                print(weight, 'LELELE')
                table_name= 'td_bird_count'
                fields= 'dc_no, schedule_no, sl_no, nob, weight, created_by, created_dt'
                values= f"'{data.form_dt.dc_no}', '{data.form_dt.schedule_no}', '{i}', '{dt.qty}', '{weight[0]}', 'admin', '{curr_date}'"
                whr= ''
                flag = 0
                result1 = await db_Insert(table_name, fields, values, whr, flag)
                i += 1

        if(len(data.lameBirdWeight) > 0):
            i = 1
            for dt in data.lameBirdWeight:
                weight = dt.weight.split(' ')
                print(weight, 'LELELE')
                table_name= 'td_lame_bird_count'
                fields= 'dc_no, schedule_no, sl_no, nob, weight, created_by, created_dt'
                values= f"'{data.form_dt.dc_no}', '{data.form_dt.schedule_no}', '{i}', '{dt.qty}', '{weight[0]}', 'admin', '{curr_date}'"
                whr= ''
                flag = 0
                result1 = await db_Insert(table_name, fields, values, whr, flag)
                i += 1
    # print(data)
    return result

@app.get('/get_collection_list/{dc_no}')
async def get_collection(dc_no:int):
    
    select = "a.*, b.trader_name, c.farmer_name"
    schema = "td_collection a, md_trader b, md_farmer c"
    where = f"dc_no = '{dc_no}'" if dc_no > 0 else 'a.trader_id=b.id AND a.farmer_id=c.id'
    order = 'ORDER BY a.str_dt'
    flag = 0 if dc_no > 0 else 1
    # print(dc_no, 'LALALA DC_NO', flag)
    result = await db_select(select, schema, where, order, flag)

    return result

@app.get('/get_bird_weight/{dc_no}/{sch_no}/{entry_dt}')
async def get_collection(dc_no:int, sch_no:int, entry_dt:str):
    select = "*"
    schema = "td_bird_count"
    where = f"dc_no = '{dc_no}' AND schedule_no = '{sch_no}' AND DATE(created_dt) = '{entry_dt}'"
    order = 'ORDER BY sl_no'
    flag = 1
    
    result = await db_select(select, schema, where, order, flag)

    return result

@app.get('/get_lame_bird_weight/{dc_no}/{sch_no}/{entry_dt}')
async def get_collection(dc_no:int, sch_no:int, entry_dt:str):
    select = "*"
    schema = "td_lame_bird_count"
    where = f"dc_no = '{dc_no}' AND schedule_no = '{sch_no}' AND DATE(created_dt) = '{entry_dt}'"
    order = 'ORDER BY sl_no'
    flag = 1
    
    result = await db_select(select, schema, where, order, flag)

    return result

@app.get('/chk_ucrc_user/{ucrc_no}')
async def check_ucrc_user(ucrc_no):
    print(ucrc_no)
    select = "a.id, a.ucrc, a.name, a.no_of_user, (SELECT COUNT(b.id) FROM md_user b WHERE b.comp_id = a.id AND user_type = 'U' AND active_flag = 'Y') tot_user"
    schema = "md_company a"
    where = f"a.ucrc = '{ucrc_no}'"
    order = ''
    flag = 0
    
    result = await db_select(select, schema, where, order, flag)

    return result

@app.get('/send_otp/{phone_no}')
async def send_otp(phone_no):
    return {'suc': 1, 'msg': 'OTP Send', 'otp': 1234}

class CreateUser(BaseModel):
    comp_id: str
    password: str
    user_name: str
    phone_no: str

@app.post('/create_user')
async def create_user_comp(data: CreateUser):
    select = "id"
    schema = "md_user"
    where = f"user_id = '{data.phone_no}'"
    order = ''
    flag = 0
    
    result = await db_select(select, schema, where, order, flag)
    print(result['suc'])
    if(result['suc'] > 1):
        current_datetime = datetime.now()
        curr_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        # print(hash_password(data.password))
        hashPass = hash_password(data.password)

        table_name= 'md_user'
        fields= 'comp_id, user_type, user_name, phone, user_id, password, first_login, created_by, created_dt'
        values= f"'{data.comp_id}', 'U', '{data.user_name}', '{data.phone_no}', '{data.phone_no}', '{hashPass}', 'N', '{data.user_name}', '{curr_date}'"
        whr= ''
        flag = 0
        result = await db_Insert(table_name, fields, values, whr, flag)
        return result
    elif(result['suc'] > 0 and result['suc'] < 2):
        return {'suc': 2, 'msg': 'User ID already exist'}
    else:
        return result

class CompId(BaseModel):
    comp_id:str

@app.post('/get_farmer_list')
async def get_farmer_list(data: CompId):
    select = "*"
    schema = "md_farmer"
    where = f"comp_id = {data.comp_id}"
    order = ''
    flag = 1
    
    result = await db_select(select, schema, where, order, flag)

    return result

@app.post('/get_trader_list')
async def get_trader_list(data: CompId):
    select = "*"
    schema = "md_trader"
    where = f"comp_id = {data.comp_id}"
    order = ''
    flag = 1
    
    result = await db_select(select, schema, where, order, flag)

    return result