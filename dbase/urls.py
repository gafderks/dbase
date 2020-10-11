"""dbase URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

from booking.views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("booking/", include("booking.urls")),
    path("catalog/", include("catalog.urls")),
    path("users/", include("users.urls")),
    path("camera/", include("camera.urls")),
    path("admin/", admin.site.urls),
    path(
        "jsi18n/",
        JavaScriptCatalog.as_view(domain="djangojs", packages=["booking"]),
        name="javascript-catalog",
    ),
]
# The following patterns only work if DEBUG = TRUE. Django should not be used for
#  serving static files or uploaded files in production environments.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG and settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
