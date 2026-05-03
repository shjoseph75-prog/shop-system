from django.urls import path
from .views import home, delete_product, edit_product, sell_product, sales_history
from . import views

urlpatterns = [
    path('', views.home),
    path('delete/<int:id>/', delete_product, name='delete_product'),
    path('edit/<int:id>/', edit_product, name='edit_product'),
    path('sell', sell_product, name='sell_product'),
    path('sales/', sales_history, name='sales_history'),
]