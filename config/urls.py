"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from commerce.controllers import products_controller, address_controller, vendor_controller, order_controller, city_controller, checkout_controller
from config import settings

api = NinjaAPI()

api.add_router('products', products_controller)
api.add_router('addresses', address_controller)
api.add_router('vendors', vendor_controller)
api.add_router('orders', order_controller)
api.add_router('cities', city_controller)
api.add_router('checkout', checkout_controller)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
