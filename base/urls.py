from django.urls import path
from . import views


urlpatterns = [
    path("login", view=views.login, name="login"),
    path("home", view = views.home, name="home"),
    path("cashier", view = views.cashier_web, name = "cashier"),
    path("insert", view = views.new_visitors),
    path("sent", view = views.EmailSending),
    path('dataCashier', view=views.addCashier),
    path("removeCashier", view=views.removeToCashier),
    path("new_trn_cashier", view=views.new_trn_cashier),
    path("egress", view = views.egress_count),
    path('search_visitor', view=views.search_visitor),
    path('id_type_search', view=views.id_type_search) 
]

