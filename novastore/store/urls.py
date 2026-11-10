from django.urls import path
from django.contrib.auth.views import LoginView

from . import views

app_name = "store"

urlpatterns = [
    path("hesap/", views.account, name="account"),
    path("giris/", LoginView.as_view(template_name="store/login.html"), name="login"),
    path("kayit/", views.register, name="register"),
    path("cikis/", views.sign_out, name="logout"),
    path("siparis/", views.checkout, name="checkout"),
    path("siparis/<int:order_id>/", views.order_detail, name="order_detail"),
    path("sepet/kaldir/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("sepet/guncelle/<int:product_id>/", views.update_cart, name="update_cart"),
    path("sepet/", views.cart_detail, name="cart_detail"),
    path("", views.index, name="index"),
    path("urun/<int:product_id>/", views.product_detail, name="product_detail"),
    path("sepet/ekle/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("urunler/", views.product_list, name="product_list"),
    path("yeni-gelenler/", views.new_arrivals, name="new_arrivals"),
]
