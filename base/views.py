from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .utils import execute_query, SendEmail, changeQuery
import json
from datetime import datetime
# Create your views here.

def login(request):
    return render(request, "base/login.html")

def home(request):
    query = "SELECT *, row_number() OVER() AS Count FROM Visitors_Info"
    count = "SELECT COUNT(*) FROM Visitors_Info"
    count_cashier = execute_query('SELECT COUNT(*) AS Count FROM Visitors_Info WHERE Purpose = "Cashier"')[0]["Count"]
    count_registrar = execute_query("SELECT COUNT(*) AS Count FROM visitors_info WHERE Purpose = 'Registrar'")[0]["Count"]
    count_accounting = execute_query("SELECT COUNT(*) AS Count FROM visitors_info WHERE Purpose = 'Accounting'")[0]["Count"]
    result_visitor = execute_query(query)
    total_count = execute_query(count)[0]["COUNT(*)"]
    print(total_count)
    print(result_visitor)

    return render(request, "base/home1.html",
                  {"visitors": result_visitor,
                   "count": total_count,
                   "count_cashier": count_cashier,
                   "count_registrar": count_registrar,
                   "count_accounting": count_accounting
                  })


def cashier_web(request):
    query = "SELECT *, row_number() OVER() AS Count FROM Visitors_Info"
    count = "SELECT COUNT(*) FROM Visitors_Info"
    query2 = "SELECT * FROM trn_cashier"
    query3 = "SELECT COUNT(*) FROM trn_registrar"
    query4 = "SELECT COUNT(*) FROM trn_accounting"
    result_visitor = execute_query(query)
    total_count = execute_query(count)[0]["COUNT(*)"]
    total_registrar = execute_query(query3)[0]["COUNT(*)"]
    result_cashier = execute_query(query2)
    total_accounting = execute_query(query4)[0]["COUNT(*)"]
    print(total_count)
    print(result_visitor)
    return render(request, 'base/cashier.html',
                  {"visitors": result_visitor,
                   "cashier": result_cashier,
                   "count": total_count,
                   "registrar_count": total_registrar,
                   "accounting_count": total_accounting
                   })


def new_visitors(request):
    if request.method == "POST":
        query = "SELECT * FROM Visitors_Info ORDER BY ID DESC LIMIT 1"
        query2 = "SELECT COUNT(*) AS Count FROM Visitors_Info"
        visitor = execute_query(query)[0]
        total_count = execute_query(query2)
        return JsonResponse({
            "visitor": visitor,
            "count": total_count[0]["Count"]
        }, status = 200, safe=False)


def new_trn_cashier(request):
    if request.method == "GET":
        try:
            # cashier_history_count = execute_query("SELECT COUNT(*) AS Count FROM trn_cashier_history")[0]["Count"]
            cashier_count = execute_query("SELECT COUNT(*) AS Count FROM trn_cashier")[0]["Count"]
            visitors_update = execute_query("SELECT * FROM Visitors_Info")
            data = {
                "visitors":visitors_update,
                "cashier_count": cashier_count
            }
        except:
             data = {"status":"Failed Fetching the data"}

    return JsonResponse(data)
        
def egress_count(request):
    if request.method == 'GET':
        try:
            visitor_count = execute_query("SELECT COUNT(*) AS Count FROM Visitors_Info")[0]['Count']
            visitor_update = execute_query("SELECT * FROM Visitors_Info")
            data = {
                "count": visitor_count,
                "update": visitor_update
            }

        except:
            data = {'Status':"Failed Fetching the data"}
        return JsonResponse(data)

def addCashier(request):
    # data = {'status': True}
    print('running')
    transactIn = str(datetime.now())[:-3]
    purpose = "Cashier"
    Status = "Ongoing"
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            first_name = data.get("first")
            last_name = data.get("last")
            idType: str = data.get("id")
            rfidnum: str = data.get("rfidNum")
            selectQuery = f'SELECT * FROM trn_cashier WHERE RFID_NUM = "{rfidnum}"'
            updateQuery = f'UPDATE visitors_info SET STATUS = "Ongoing", Purpose = "Cashier" WHERE RFID_NUM = "{rfidnum}"'
            results = execute_query(selectQuery)
            if results:
                data = {"status": True}
            elif not results:
                insertQuery = f"""
                INSERT INTO trn_cashier(RFID_NUM, FirstName, LastName, Type, Purpose, Status, TimeOfTransaction)
                VALUES ("{rfidnum}","{first_name}", "{last_name}", "{idType}", "{purpose}", "{Status}", "{transactIn}")
                """
                changeQuery(insertQuery)
                changeQuery(updateQuery)
                print("Successfully Inserted")
                visitor_info = execute_query(selectQuery)
                data = {"status": False,
                        "data": visitor_info[0]}  
        except:
            data = {"status":"Failed Fetching the data"}
        finally:
            pass
    return JsonResponse(data)


def removeToCashier(request):
    if request.method == "POST":
        data = json.loads(request.body)
        firstName = data.get("first")
        lastName = data.get("last")
        id_num = data.get("id_num")
        rfid = data.get("rfid")
        type = data.get("type")
        deleteQuery = f"DELETE FROM trn_cashier WHERE RFID_NUM = '{rfid}' "
        updateQuery = f"UPDATE visitors_info SET Status = 'Pending', Purpose = 'School' WHERE RFID_NUM = '{rfid}' "
        insertQuery = f"""
                        INSERT INTO trn_cashier_history ( RFID_NUM, FirstName, LastName, Type, Purpose, Status, TimeOfTransaction)
                        SELECT RFID_NUM, FirstName, LastName, Type, Purpose, Status, TimeOfTransaction FROM trn_cashier WHERE RFID_NUM = '{rfid}'
                       """
        changeQuery(insertQuery)
        changeQuery(deleteQuery)
        changeQuery(updateQuery)    
    return JsonResponse({"success": "fetch"})



def search_visitor(request):
    if request.method == "POST":
        all_list = {"data": []} 
        try:
            data = json.loads(request.body)
            fullName = str(data.get("name", '')).title()
            query = f"""
                        SELECT RFID_NUM, FirstName, LastName, concat(FirstName, ' ', LastName) AS FullName, Type, Purpose, Status, LogIn 
                        FROM visitors_info;
                    """
            result = execute_query(query)
            if fullName == "":
                print(result)
                return JsonResponse({"data": result})
            elif fullName != "":
                for visitor in result:
                    if visitor['FullName'].__contains__(fullName):
                        all_list["data"].append(visitor)
            
                return JsonResponse(all_list)
        except:
            return JsonResponse({"error": "Error in the database"})

def id_type_search(request):
    if request.method == "POST":
        try: 
            data = json.loads(request.body)
            id_type = data.get("id", '')
            if id_type not in ["Philippine Identification Card", 'Unified Multi-Purpose Id', 'Drivers License']:
                query = f"""
                SELECT RFID_NUM, FirstName, LastName, concat(FirstName, ' ', LastName) AS FullName, Type, Purpose, Status, LogIn 
                FROM visitors_info;"""
                result = execute_query(query)
                return JsonResponse({"data":result})
            else:
                query = f"""
                            SELECT RFID_NUM, FirstName, LastName, concat(FirstName, ' ', LastName) AS FullName, Type, Purpose, Status, LogIn 
                            FROM visitors_info WHERE Type = '{id_type}' """
                result = execute_query(query)
            return JsonResponse({'data': result})
        except: 
            return JsonResponse({"data": "error"})


def registrar(request):
    query = "SELECT *, row_number() OVER() AS Count FROM Visitors_Info"
    count = "SELECT COUNT(*) FROM Visitors_Info"
    registrar_query = "SELECT * FROM trn_registrar"
    cashier_count = execute_query("SELECT COUNT(*) AS Count FROM trn_cashier")[0]["Count"]
    account_count = execute_query("SELECT COUNT(*) AS Count FROM trn_accounting")[0]["Count"]
    visitors_update = execute_query("SELECT * FROM Visitors_Info")
    result_visitor = execute_query(query)
    result_registrar = execute_query(registrar_query)
    total_count = execute_query(count)[0]["COUNT(*)"]
    
    print(result_registrar)
    
    return render(request, 'base/registrar.html',
                    {"visitors": result_visitor,
                    "registrar": result_registrar,
                    "count": total_count,
                    "cashier_count": cashier_count,
                    "accounting_count": account_count
                    }
                )

def addRegistrar(request):
    transactIn = str(datetime.now())[:-3]
    purpose = "Registrar"
    Status = "Ongoing"
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            first_name = data.get("first")
            last_name = data.get("last")
            idType: str = data.get("id")
            rfidnum: str = data.get("rfidNum")
            selectQuery = f'SELECT * FROM trn_registrar WHERE RFID_NUM = "{rfidnum}"'
            updateQuery = f'UPDATE visitors_info SET STATUS = "Ongoing", Purpose = "Registrar" WHERE RFID_NUM = "{rfidnum}"'
            results = execute_query(selectQuery)
            if results:
                data = {"status": True}
            elif not results:
                insertQuery = f"""
                INSERT INTO trn_registrar(RFID_NUM, FirstName, LastName, Type, Purpose, Status, TimeOfTransaction)
                VALUES ("{rfidnum}","{first_name}", "{last_name}", "{idType}", "{purpose}", "{Status}", "{transactIn}")
                """
                changeQuery(insertQuery)
                changeQuery(updateQuery)
                print("Successfully Inserted")
                visitor_info = execute_query(selectQuery)
                data = {"status": False,
                        "data": visitor_info[0]}
            return JsonResponse(data)
        
        except:
            return JsonResponse({"Status": "Error fetching Data"})

def removeRegistrar(request):
    if request.method == "POST":
        data = json.loads(request.body)
        rfid = data.get("rfid", '')
        deleteQuery = f"DELETE FROM trn_registrar WHERE RFID_NUM = '{rfid}'"
        updateQuery = f"UPDATE visitors_info SET Status = 'Pending', Purpose = 'School' WHERE RFID_NUM = '{rfid}' "
        insertQuery = f"""
                        INSERT INTO trn_registrar_history ( RFID_NUM, FirstName, LastName, Type, Purpose, Status, TimeOfTransaction)
                        SELECT RFID_NUM, FirstName, LastName, Type, Purpose, Status, TimeOfTransaction FROM trn_registrar WHERE RFID_NUM = '{rfid}'
                       """
        changeQuery(insertQuery)
        changeQuery(deleteQuery)
        changeQuery(updateQuery)    
    return JsonResponse({"success": "fetch"})


        
def new_trn_registrar(request):
    if request.method == "GET":
        count_registrar = "SELECT COUNT(*) FROM trn_registrar"
        visitor_table = "SELECT * FROM visitors_info"
        count = execute_query(count_registrar)
        table_registrar = execute_query(visitor_table)

        return JsonResponse({
            "count_registrar": count,
            "registrar": table_registrar
        })


def accounting_web(request):
    query = "SELECT *, row_number() OVER() AS Count FROM Visitors_Info"
    count = "SELECT COUNT(*) FROM Visitors_Info"
    query2 = "SELECT * FROM trn_accounting"
    query3 = "SELECT COUNT(*) FROM trn_cashier"
    query4 = "SELECT COUNT(*) FROM trn_registrar"
    total_count = execute_query(count)[0]["COUNT(*)"]
    total_cashier = execute_query(query3)[0]["COUNT(*)"]
    total_registrar = execute_query(query4)[0]["COUNT(*)"]
    visitors = execute_query(query)
    total_accounting = execute_query(query2)
    return render(request, "base/accounting.html", {
        "count":total_count,
        "visitors": visitors,
        "accounting": total_accounting,
        "cashier": total_cashier,
        "registrar":total_registrar
    })
    
def addAccounting(request):
    # data = {'status': True}
    print('running')
    transactIn = str(datetime.now())[:-3]
    purpose = "Accounting"
    Status = "Ongoing"
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            first_name = data.get("first")
            last_name = data.get("last")
            idType: str = data.get("id")
            rfidnum: str = data.get("rfidNum")
            selectQuery = f'SELECT * FROM trn_accounting WHERE RFID_NUM = "{rfidnum}"'
            updateQuery = f'UPDATE visitors_info SET STATUS = "Ongoing", Purpose = "Accounting" WHERE RFID_NUM = "{rfidnum}"'
            results = execute_query(selectQuery)
            if results:
                data = {"status": True}
            elif not results:
                insertQuery = f"""
                INSERT INTO trn_accounting(RFID_NUM, FirstName, LastName, Type, Purpose, Status, TimeOfTransaction)
                VALUES ("{rfidnum}","{first_name}", "{last_name}", "{idType}", "{purpose}", "{Status}", "{transactIn}")
                """
                changeQuery(insertQuery)
                changeQuery(updateQuery)
                print("Successfully Inserted")
                visitor_info = execute_query(selectQuery)
                data = {"status": False,
                        "data": visitor_info[0]}  
        except:
            data = {"status":"Failed Fetching the data"}
        finally:
            pass
    return JsonResponse(data)



def removeAccounting(request):
    if request.method == "POST":
        data = json.loads(request.body)
        rfid = data.get("rfid", '')
        deleteQuery = f"DELETE FROM trn_accounting WHERE RFID_NUM = '{rfid}'"
        updateQuery = f"UPDATE visitors_info SET Status = 'Pending', Purpose = 'School' WHERE RFID_NUM = '{rfid}' "
        insertQuery = f"""
                        INSERT INTO trn_accounting_history ( RFID_NUM, FirstName, LastName, Type, Purpose, Status, TimeOfTransaction)
                        SELECT RFID_NUM, FirstName, LastName, Type, Purpose, Status, TimeOfTransaction FROM trn_registrar WHERE RFID_NUM = '{rfid}'
                       """
        changeQuery(insertQuery)
        changeQuery(deleteQuery)
        changeQuery(updateQuery)    
    return JsonResponse({"success": "fetch"})

def new_trn_accounting(request):
    if request.method == "GET":
        count_registrar = "SELECT COUNT(*) FROM trn_accounting"
        visitor_table = "SELECT * FROM visitors_info"
        count = execute_query(count_registrar)[0]["COUNT(*)"]
        table_registrar = execute_query(visitor_table)

        return JsonResponse({
            "count_accounting": count,
            "visitors": table_registrar
        })


def EmailSending(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name", '')
            purpose = data.get("purpose", '')
            timeIn = data.get("timeIn", '')
            print(timeIn)
            SendEmail(name, timeIn, purpose)
            response = {"status": "Sent Email Successfully"}
        except: 
            response = {"status": "Email Sent Failed"}
        return JsonResponse(response)

def addPhoneNumber(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            phone = data.get("phone", '')
            rfid_num = data.get('rfid_num')
            update_query = f"UPDATE visitors_info SET PhoneNumber = '{phone}' WHERE RFID_NUM = '{rfid_num}'"
            changeQuery(update_query)
            data = {
                "data": True
            }
            return JsonResponse(data)
        except:
            return JsonResponse({"Status": "Error in backend"})
             

    