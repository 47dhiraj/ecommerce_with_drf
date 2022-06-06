from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

import debug_toolbar


urlpatterns = [

    path('admin/', admin.site.urls),

    path('api/products/', include('ecom_api.urls.product_urls')),

    path('api/users/', include('ecom_api.urls.user_urls')),

    path('api/orders/', include('ecom_api.urls.order_urls')),

    path("__debug__/", include(debug_toolbar.urls)),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


