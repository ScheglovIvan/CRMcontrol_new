from fast_bitrix24 import Bitrix
import requests
import json
import time
from datetime import datetime, date

from gsh import AddOrderSheet, UpdateOrderSheet

webhook = "https://altair.bitrix24.ua/rest/1/pq4jor2ovao54xbi/"
b = Bitrix(webhook)

def days_count(date):
    date = datetime.strptime(date.split("T")[0]+ " 00:00:00.0", '%Y-%m-%d %H:%M:%S.%f')

    day = date.day
    month = date.month
    year =date.year

    end = datetime(day=day, month=month, year=year)
    start = datetime(day=30, month=12, year=1899)
    countdown = end - start

    return countdown.days




def NovaPoshtaGetOrderByTTN(TTN):
    url = 'https://api.novaposhta.ua/v2.0/json/'

    payload = {
        "apiKey": "ffde97724b90d89cdf0ecb016625716c",
        "modelName": "TrackingDocument",
        "calledMethod": "getStatusDocuments",
        "methodProperties": {
            "CheckWeightMethod": "",
            "CalculatedWeight": "",
            "Documents": [
                {
                    "DocumentNumber": TTN,
                    "Phone": ""
                }
            ]
        }
    }

    r = requests.get(url=url, data=json.dumps(payload))

    try:
        return r.json()['data'][0]
    except Exception as err:
        print(err)
        print("Новая почта ошибка!!!!")
        return False

def BitrixGetDeal(filter):

    deals = b.get_all(
        'crm.deal.list',
        params={
            'select': ['*', 'UF_*'],
            'filter': filter
    })

    return deals

def BitrixChangeStage(deal_id, stage_id):
    method = 'crm.deal.update'
    params = {'ID': deal_id, 'fields': {'STAGE_ID': stage_id}}
    b.call(method, params)


def BitrixControlStatus(order_id, status_code, stage_id):
    status_keys = {
            "7": "C29:UC_BJRWKU",
            "9": "C29:WON",
            "102": "C29:LOSE",
            "103": "C29:LOSE",
        }


    if stage_id != status_keys[status_code]:
        BitrixChangeStage(order_id, status_keys[status_code])


def gshControlStatus(order_id, status_code):

    status_keys = {
            "7": "Прибыл на отделение",
            "9": "Получил",
            "102": "Отказался",
            "103": "Отказался",
        }

    UpdateOrderSheet(order_id, {"C": status_keys[status_code]})


def NewOrder(deal):

    contact = b.get_all(
        'crm.contact.list',
        params={
            'select': ['Name', 'PHONE', "*"],
            'filter': {'ID': deal["CONTACT_ID"]}
    })[0]

    try:
        order_id = int(deal["ID"])
    except:
        order_id = ""

  
    order_date = days_count(deal["BEGINDATE"])

    order_status = "На отправку"

    try:
        order_prepayment = int(deal["UF_CRM_1633275701280"])
    except:
        order_prepayment = ""
    
    try:
        order_sum = int(float(deal["OPPORTUNITY"]))
    except:
        order_sum = ""

    order_discount = 0

    try:
        order_count = int(deal["UF_CRM_1649747064818"][0])
    except:
        order_count = ""

    try:
        order_adress = str(deal["UF_CRM_1633274704683"])
    except:
        order_adress = ""

    try:
        order_phone = str(contact["PHONE"][0]["VALUE"])
    except:
        order_phone = ""
    
    try:
        order_holdername = str(contact["NAME"])
    except:
        order_holdername = ""

    try:
        order_ttn = str(deal["UF_CRM_1645092420180"])
    except:
        order_ttn = ""

    # try:
    #     if deal["UF_CRM_1650966063918"] == '45':
    #         order_item = "Бронежелет MARK IV"
    # except:
    order_item = "Бронежелет MARK IV"

    print(order_id)
    
    AddOrderSheet(
        order_id,
        order_date,
        order_status,
        order_prepayment,
        order_sum,
        order_discount,
        order_count,
        order_item,
        order_adress,
        order_phone,
        order_holdername,
        order_ttn)

def ControlOrderStatus():
    filter = {
        'CATEGORY_ID': 29,
        'UF_CRM_1645092420180': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }

    deals = BitrixGetDeal(filter)
    
    print(len(deals))
    for deal in deals:
        if deal["STAGE_ID"] == "C29:LOSE" and deal['UF_CRM_1645092420180'] == "":
            continue


        iter = 0
        while True:
            iter+=1
            try:
                NewOrder(deal)

                order = NovaPoshtaGetOrderByTTN(deal['UF_CRM_1645092420180'])

                if order:
                    order_id = deal["ID"]
                    status_code = order["StatusCode"]
                    stage_id = deal["STAGE_ID"]

                    gshControlStatus(order_id, status_code)
                    BitrixControlStatus(order_id, status_code, stage_id)

                break

            except Exception as err:
                if iter >= 5:
                    break
     
                time.sleep(2)

        time.sleep(1)
        print("__________________")
        
# ControlOrderStatus()
order = NovaPoshtaGetOrderByTTN("20450528582881")

if order:
    order_id = "10151"
    status_code = order["StatusCode"]
    stage_id = "test"

    gshControlStatus(order_id, status_code)
    BitrixControlStatus(order_id, status_code, stage_id)

    print(status_code)