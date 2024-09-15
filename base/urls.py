from django.urls import path
from . import views


urlpatterns = [
    path("login", view=views.login, name="login"),
    path("home", view = views.home, name="home"),
    path("cashier", view = views.cashier_web, name = "cashier"),
    path("insert", view = views.new_visitors),
    path("sent", view = views.EmailSending),
    path('dataCashier', view=views.addCashier),
    path("removeCashier", view=views.removeToCashier)
    
]

