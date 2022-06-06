from django.urls import path

from ecom_api.views import order_views as views


urlpatterns = [

    path("esewa_payment/", views.esewaPayment, name="esewa_payment"),

    path('add/', views.addOrderItems, name='orders-add'),
    path('myorders/', views.getMyOrders, name='myorders'),

    path('<str:pk>/', views.getOrderById, name='user-order'),
    
]
