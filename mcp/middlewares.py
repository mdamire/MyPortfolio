"""
Middleware for MCP OAuth authentication
"""

from django.urls import reverse


class WWWAuthenticateMiddleware:
    """
    Middleware to add WWW-Authenticate header to 401 responses
    for OAuth-protected resources
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add WWW-Authenticate header for 401 responses on MCP endpoints
        if response.status_code == 401 and request.path_info.startswith("/mcp/"):
            resource_metadata_url = request.build_absolute_uri(
                reverse("oauth_protected_resource_metadata")
            )
            response["WWW-Authenticate"] = (
                f'Bearer resource_metadata="{resource_metadata_url}"'
            )

        return response
