from django.conf.urls import url
from django.contrib import admin
#from meow import meow_app
import meow_app.views as views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),              # root
    url(r'^login$', views.login_view),    # login user
    url(r'^logout$', views.logout_view),  # logout user
    url(r'^signup$', views.signup),       # register new user
    url(r'^meows$', views.public),        # public meows
    url(r'^submit$', views.submit),       # submit new meow
]
