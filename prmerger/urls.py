from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'', include('interface.urls', namespace='interface')),
    url(r'', include('social_django.urls', namespace='social')),
    url(r'^worker/', include('django_rq.urls')),
    url(r'^admin/', admin.site.urls)
]
