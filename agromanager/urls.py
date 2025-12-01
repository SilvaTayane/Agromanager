from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("home", views.visualizar_home, name="home"),
    path("login/", views.visualizar_login, name="login"),
    path("dashboard", views.visualizar_dashboard, name="dashboard"),
    path("localizacao/", views.mostrar_localizacao, name="localizacao"), 
    path("relatorio/", views.visualizar_relatorio, name="relatorio"),
    path("atividades/", include('apps.atividades.urls')),
    path('animais/', include('apps.animal.urls')),
    path('monitoramento/', include('apps.monitoramento.urls')),
    path('estoque/', include('apps.estoque.urls')),

]








