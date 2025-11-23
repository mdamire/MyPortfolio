from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from mcp_serializer.initializer import MCPInitializer
from mcp_serializer.serializers import MCPSerializer

from .authenticators import McpAuthenticator
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


class McpView(View):
    """
    MCP View with token-based authentication
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to add token authentication
        """
        # is_valid, result = McpAuthenticator.authenticate_token(request)

        # if not is_valid:
        #     return JsonResponse({"error": f"Unauthorized - {result}"}, status=401)

        # # Store authenticated token in request
        # request.mcp_token = result

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
        request_data = request.body.decode("utf-8")
        response_data = mcp_serializer.process_request(request_data)
        breakpoint()
        return JsonResponse(response_data, status=200, safe=False)


@csrf_exempt
def MCPView2(request):
    """
    MCP View with token-based authentication
    """
    if request.method == "POST":
        request_data = request.body.decode("utf-8")
        response_data = mcp_serializer.process_request(request_data)
        response = JsonResponse(response_data, status=200, safe=False)
        return response
    elif request.method == "GET":
        return JsonResponse({"message": "Hello, world!"}, status=200)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
