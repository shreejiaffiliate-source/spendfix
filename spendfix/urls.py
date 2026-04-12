"""
URL configuration for spendfix project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path , include
from django.conf import settings # 🎯 Ye line add karein
from django.conf.urls.static import static
from django.views.generic.base import RedirectView # Ye line add karo
from tracker.views import custom_dashboard # 🎯 Ye line add karein

urlpatterns = [
    path('', RedirectView.as_view(url='portal/', permanent=True)),
    path('admin/', admin.site.urls),
    path('api/', include('account.urls')),
    path('api/tracker/', include('tracker.urls')), # Tracker ke raste (Naya)
    path('portal/', custom_dashboard, name='main_dashboard'),
]


# 🎯 Sabse aakhiri mein ye MAGIC LINE add karein (Ye photos ko 404 aane se rokegi)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)