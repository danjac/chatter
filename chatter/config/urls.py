# Django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

# Chatter
from chatter.chat.views import do_redirect
from chatter.users import views as account_views

urlpatterns = [
    path("", do_redirect),
    path("account/login/", account_views.login, name="account_login"),
    path("account/signup/", account_views.signup, name="account_signup"),
    path("account/", include("allauth.urls")),
    path("chat/", include("chatter.chat.urls")),
    path(settings.ADMIN_URL, admin.site.urls),
]

if settings.DEBUG:

    if "silk" in settings.INSTALLED_APPS:
        urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]

    # static views
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # allow preview/debugging of error views in development
    urlpatterns += [
        path("errors/400/", TemplateView.as_view(template_name="400.html")),
        path("errors/403/", TemplateView.as_view(template_name="403.html")),
        path("errors/404/", TemplateView.as_view(template_name="404.html")),
        path("errors/405/", TemplateView.as_view(template_name="405.html")),
        path("errors/500/", TemplateView.as_view(template_name="500.html")),
        path("errors/csrf/", TemplateView.as_view(template_name="403_csrf.html")),
    ]
