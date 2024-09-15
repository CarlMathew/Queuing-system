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
    result_visitor = execute_query(query)
    total_count = execute_query(count)[0]["COUNT(*)"]
    print(total_count)
    print(result_visitor)

    return render(request, "base/home.html",
                  {"visitors": result_visitor,
                   "count": total_count})


def cashier_web(request):
    query = "SELECT *, row_number() OVER() AS Count FROM Visitors_Info"
    count = "SELECT COUNT(*) FROM Visitors_Info"
    query2 = "SELECT * FROM trn_cashier"
    result_visitor = execute_query(query)
    total_count = execute_query(count)[0]["COUNT(*)"]
    result_cashier = execute_query(query2)
    print(total_count)
    print(result_visitor)
    return render(request, 'base/cashier.html',
                  {"visitors": result_visitor,
                   "cashier": result_cashier,
                   "count": total_count})


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


def addCashier(request):
    transactIn = str(datetime.now())[:-3]
    purpose = "Cashier"
    Status = "Ongoing"
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            first_name = data.get("first")
            last_name = data.get("last")
            idType: str = data.get("id")
            selectQuery = f'SELECT * FROM trn_cashier WHERE FirstName = "{first_name}" AND lastName = "{last_name}" AND Type = "{idType}"'
            updateQuery = f'UPDATE visitors_info SET STATUS = "Ongoing" WHERE FirstName = "{first_name}" AND lastName = "{last_name}" AND Type = "{idType}"'
            results = execute_query(selectQuery)
            if results:
                data = {"status": True}
            elif not results:
                insertQuery = f"""
                INSERT INTO trn_cashier(FirstName, LastName, Type, Purpose, Status, TimeOfTransaction)
                VALUES ("{first_name}", "{last_name}", "{idType}", "{purpose}", "{Status}", "{transactIn}")
                """
                changeQuery(insertQuery)
                changeQuery(updateQuery)
                print("Successfully Inserted")
                visitor_info = execute_query(selectQuery)
                data = {"status": False,
                        "data": visitor_info[0]}  
                
        except:
            data = {"status":"Failed Fetching the data"}
    return JsonResponse(data)


def removeToCashier(request):
    if request.method == "POST":
        data = json.loads(request.body)
        firstName = data.get("first")
        lastName = data.get("last")
        id_num = data.get("id_num")

        deleteQuery = f"DELETE FROM trn_cashier WHERE FirstName = '{firstName}' AND LastName = '{lastName}' AND ID = '{id_num}'"
        updateQuery = f"UPDATE visitors_info SET Status = 'Pending' WHERE FirstName = '{firstName}' AND LastName = '{lastName}'"
        changeQuery(deleteQuery)
        changeQuery(updateQuery)
        


    return JsonResponse({"success": "fetch"})

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

    