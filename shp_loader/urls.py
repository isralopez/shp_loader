from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'shp_loader.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
                       url(r'^/?$', TemplateView.as_view(template_name='home.html'), name='home'),
                       url(r'^admin/', include(admin.site.urls)),

                       #(r'^avatar/', include('avatar.urls')),
)
