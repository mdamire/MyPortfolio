from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .authenticators import McpAuthenticator


class McpView(View):
    """
    MCP View with token-based authentication
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to add token authentication
        """
        is_valid, result = McpAuthenticator.authenticate_token(request)

        if not is_valid:
            return JsonResponse({"error": f"Unauthorized - {result}"}, status=401)

        # Store authenticated token in request
        request.mcp_token = result

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests
        """
        pass

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests
        """
        pass
