from django.utils import timezone
from .models import McpToken


class McpAuthenticator:
    """
    Authenticator class for token-based authentication
    """

    @staticmethod
    def authenticate_token(request):
        """
        Validate token from Authorization header
        Returns tuple: (is_valid, token_or_error_message)
        """
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return False, "Missing Authorization header"

        if not auth_header.startswith("Bearer "):
            return (
                False,
                "Invalid Authorization header format. Expected: Bearer <token>",
            )

        token = auth_header.split(" ")[1]

        try:
            mcp_token = McpToken.objects.get(token=token, is_active=True)

            # Update last_used timestamp
            mcp_token.last_used = timezone.now()
            mcp_token.save(update_fields=["last_used"])

            return True, mcp_token

        except McpToken.DoesNotExist:
            return False, "Invalid or inactive token"
