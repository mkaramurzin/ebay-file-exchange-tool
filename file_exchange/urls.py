from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("static", views.static, name="static"),
    path("unique", views.unique, name="unique"),
    path("download/<int:id>", views.download, name="download"),
    path("templates", views.templates, name="templates"),
    path("template/<int:id>", views.template, name="template")
]