from django.conf.urls import include, url
from .views import FacebookCallbackView

urlpatterns = [
    url(
        regex=r'^9850eea4020c130fb92af877a626248479ef038f67a8638090/?$',
        view=FacebookCallbackView.as_view(),
        name='facebook_callback'
        ),
]
