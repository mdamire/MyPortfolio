"""MyPortfolio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from oauth2_provider import urls as oauth2_urls

from pages.views import HomePageView, StaticPageView
from posts.views import PostDetailView, PostListView
from mcp.views import (
    McpView,
    OAuthProtectedResourceMetadataView,
    OAuthAuthorizationServerMetadataView,
    DynamicClientRegistrationView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("", HomePageView.as_view(), name="home"),
    path("post/<str:permalink>", PostDetailView.as_view(), name="post-detail"),
    path("posts/", PostListView.as_view(), name="post-list"),
    path("page/<str:permalink>", StaticPageView.as_view(), name="static-page"),
    path("oauth/", include(oauth2_urls)),
    path("mcp/", McpView.as_view(), name="mcp"),
    path(
        ".well-known/oauth-authorization-server",
        OAuthAuthorizationServerMetadataView.as_view(),
        name="oauth_authorization_server_metadata",
    ),
    path(
        ".well-known/oauth-protected-resource",
        OAuthProtectedResourceMetadataView.as_view(),
        name="oauth_protected_resource_metadata",
    ),
    path(
        "register/",
        DynamicClientRegistrationView.as_view(),
        name="register_client",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
