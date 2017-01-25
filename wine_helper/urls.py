from django.conf.urls import include, url
from .views import FacebookCallbackView
from . import views

urlpatterns = [
    url(
        regex=r'^9850eea4020c130fb92af877a626248479ef038f67a8638090/?$',
        view=FacebookCallbackView.as_view(),
        name='facebook_callback'
        ),
    url(r'^install', views.pre_install),
    url(r'^thanks', views.thanks),
    url(r'^listening', views.hears),
    url(r'^button', views.button),
    url(r'^slack/oauth/$', views.slack_oauth),
]
