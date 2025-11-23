from django.urls import path
from .views import McpView, MCPView2

urlpatterns = [
    # path("", McpView.as_view(), name="mcp"),
    path("", MCPView2, name="mcp"),
]
