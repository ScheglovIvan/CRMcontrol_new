import gspread
import time


gc = gspread.service_account(filename='creds.json')


def AddOrderSheet(*args, **kwargs):
    sh = gc.open("Orders")
    sheet = sh.sheet1

    order_id = [*args][0]
    cell = sheet.find(str(order_id))

    if cell == None:
        sheet.append_row([*args])

        time.sleep(1)

    

def UpdateOrderSheet(order_id, *args, **kwargs):
    sh = gc.open("Orders")
    update_arr=[*args][0]


    worksheet = sh.sheet1

    cell = worksheet.find(str(order_id))

    if cell:
        row = cell.row
        col = cell.col


        for key in update_arr:
            value = update_arr[key]
            worksheet.update(key+str(row), value)
        



# AddOrderSheet("test1", "test2", "test3")
# UpdateOrderSheet(10151, {"C": "В пути", "D": "2000", "E": "20",})