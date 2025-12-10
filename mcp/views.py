from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from mcp_serializer.initializer import MCPInitializer
from mcp_serializer.serializers import MCPSerializer
from oauth2_provider.views.generic import ProtectedResourceView
from oauth2_provider.models import Application
import json
import secrets

from .registry import registry

mcp_initializer = MCPInitializer()
mcp_initializer.add_server_info(
    name="MyPortfolio",
    version="1.0.0",
    title="A MCP to create and manage blog posts for my portfolio website.",
)
mcp_initializer.add_prompt()
mcp_initializer.add_resources()
mcp_initializer.add_tools()

mcp_serializer = MCPSerializer(
    initializer=mcp_initializer, registry=registry, page_size=20
)


class McpView(ProtectedResourceView):
    """
    MCP View with OAuth 2.0 authentication.
    Returns 401 with WWW-Authenticate header when authentication fails.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Let preflight OPTIONS requests pass
        if request.method.upper() == "OPTIONS":
            return super().dispatch(request, *args, **kwargs)

        # Check if the request is valid and the protected resource may be accessed
        valid, r = self.verify_request(request)
        if valid:
            request.resource_owner = r.user
            return super().dispatch(request, *args, **kwargs)
        else:
            # Return 401 Unauthorized (not 403) for MCP OAuth flow
            # The WWW-Authenticate header is added by WWWAuthenticateMiddleware
            return JsonResponse(
                {
                    "error": "unauthorized",
                    "error_description": "Authentication required",
                },
                status=401,
            )

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests
        """
        return JsonResponse({"message": "Hello, world!"}, status=200)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests
        """
        request_data = request.body.decode("utf-8")
        response_data = mcp_serializer.process_request(request_data)
        return JsonResponse(response_data, status=200, safe=False)


class OAuthProtectedResourceMetadataView(View):
    """
    OAuth 2.0 Protected Resource Metadata endpoint
    RFC 9728 compliant
    """

    def get(self, request, *args, **kwargs):
        # Authorization server issuer - base URL where client fetches /.well-known/oauth-authorization-server
        authorization_server_issuer = request.build_absolute_uri("/").rstrip("/")
        metadata = {
            # The protected resource identifier (this MCP server)
            "resource": request.build_absolute_uri(reverse("mcp")),
            # Authorization servers this resource trusts
            "authorization_servers": [authorization_server_issuer],
            # Supported bearer token methods
            "bearer_methods_supported": ["header"],
            # Scopes supported by this resource
            "scopes_supported": ["read", "write"],
        }
        return JsonResponse(metadata, status=200)


class OAuthAuthorizationServerMetadataView(View):
    """
    OAuth 2.0 Authorization Server Metadata endpoint
    RFC 8414 compliant
    """

    def get(self, request, *args, **kwargs):
        issuer = request.build_absolute_uri("/").rstrip("/")
        metadata = {
            "issuer": issuer,
            "authorization_endpoint": request.build_absolute_uri(
                reverse("oauth2_provider:authorize")
            ),
            "token_endpoint": request.build_absolute_uri(
                reverse("oauth2_provider:token")
            ),
            "registration_endpoint": request.build_absolute_uri(
                reverse("register_client")
            ),
            "revocation_endpoint": request.build_absolute_uri(
                reverse("oauth2_provider:revoke-token")
            ),
            "introspection_endpoint": request.build_absolute_uri(
                reverse("oauth2_provider:introspect")
            ),
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "token_endpoint_auth_methods_supported": [
                "client_secret_basic",
                "client_secret_post",
            ],
            "scopes_supported": ["read", "write"],
            "code_challenge_methods_supported": ["S256"],
        }
        return JsonResponse(metadata, status=200)


class DynamicClientRegistrationView(View):
    """
    Dynamic Client Registration endpoint
    RFC 7591 compliant
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Register a new OAuth client dynamically (RFC 7591)
        """
        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "error": "invalid_client_metadata",
                    "error_description": "Invalid JSON",
                },
                status=400,
            )

        # Extract registration parameters
        client_name = data.get("client_name", "MCP Client")
        redirect_uris = data.get("redirect_uris", [])
        grant_types = data.get("grant_types", ["authorization_code"])
        response_types = data.get("response_types", ["code"])
        scope = data.get("scope", "read write")
        token_endpoint_auth_method = data.get(
            "token_endpoint_auth_method", "client_secret_basic"
        )

        # MCP only supports authorization_code grant type
        if "authorization_code" not in grant_types:
            return JsonResponse(
                {
                    "error": "invalid_client_metadata",
                    "error_description": "MCP only supports authorization_code grant type",
                },
                status=400,
            )

        # Validate redirect_uris is a list
        if not isinstance(redirect_uris, list):
            return JsonResponse(
                {
                    "error": "invalid_redirect_uri",
                    "error_description": "redirect_uris must be an array",
                },
                status=400,
            )

        # redirect_uris is required for authorization_code grant
        if not redirect_uris:
            return JsonResponse(
                {
                    "error": "invalid_redirect_uri",
                    "error_description": "redirect_uris is required",
                },
                status=400,
            )

        # MCP uses confidential clients with authorization_code grant
        client_type = Application.CLIENT_CONFIDENTIAL
        authorization_grant_type = Application.GRANT_AUTHORIZATION_CODE

        # Create the OAuth application
        try:
            application = Application.objects.create(
                name=client_name,
                client_type=client_type,
                authorization_grant_type=authorization_grant_type,
                redirect_uris=" ".join(redirect_uris) if redirect_uris else "",
            )

            # Build RFC 7591 compliant response
            response_data = {
                "client_id": application.client_id,
                "client_secret": application.client_secret,
                "client_id_issued_at": int(application.created.timestamp()),
                "client_secret_expires_at": 0,  # 0 means it doesn't expire
                "client_name": application.name,
                "grant_types": grant_types,
                "response_types": response_types,
                "scope": scope,
                "token_endpoint_auth_method": token_endpoint_auth_method,
            }

            if redirect_uris:
                response_data["redirect_uris"] = redirect_uris

            return JsonResponse(response_data, status=201)

        except Exception as e:
            return JsonResponse(
                {
                    "error": "invalid_client_metadata",
                    "error_description": f"Failed to create client: {str(e)}",
                },
                status=500,
            )
