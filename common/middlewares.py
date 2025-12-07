import logging
import json
import time
from django.conf import settings

logger = logging.getLogger("portfolio.url")


class RequestResponseLoggingMiddleware:
    """
    Middleware to log HTTP requests and responses for specified urls.

    Configure url to log in settings.py:
    LOGGED_URLS = [
        '/api/',
        '/mcp/',
        '/admin/',
    ]

    Or set LOGGED_URLS = '__all__' to log all urls.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logged_urls = getattr(settings, "LOGGED_URLS", [])

    def __call__(self, request):
        should_log = self._should_log_endpoint(request.path)
        if should_log:
            start_time = time.time()

        # Process the request
        response = self.get_response(request)

        if should_log:
            duration = time.time() - start_time
            self._log_url(request, response, duration)

        return response

    def _is_console_logger(self):
        """Check if any handler is a StreamHandler (console)"""
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                return True

        # Also check root logger handlers
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.StreamHandler):
                return True
        return False

    def _log_url(self, request, response, duration):
        """Log the URL, method, and status code."""
        summary = self._log_summary(request, response, duration)
        request_log_data = self._log_request(request)
        response_log_data = self._log_response(response)

        if self._is_console_logger():
            request_log_text = self._indent(
                "Request: " + json.dumps(request_log_data, indent=2)
            )
            response_log_text = self._indent(
                "Request: " + json.dumps(response_log_data, indent=2)
            )
            summary += f"\n{request_log_text}\n{response_log_text}"

        logger.info(
            summary,
            extra={
                "request": request_log_data,
                "response": response_log_data,
            },
        )

    def _should_log_endpoint(self, path):
        """Check if the endpoint should be logged based on configuration."""
        if not self.logged_urls:
            return False

        if self.logged_urls == "__all__":
            return True

        return any(path.startswith(endpoint) for endpoint in self.logged_urls)

    def _indent(self, text, spaces=2):
        """Add indentation to each line of data."""
        indent = ("=" * spaces) + " "
        return "\n".join(f"{indent}{line}" for line in text.split("\n"))

    def _log_summary(self, request, response, duration):
        """Log a summary of the request and response."""
        summary_info = f"{request.method} {request.path} - {response.status_code} in {round(duration * 1000, 2)}ms"
        return summary_info

    def _log_request(self, request):
        """return incoming request data."""
        log_data = {
            "method": request.method,
            "path": request.path,
            "query_params": dict(request.GET),
            "user": str(request.user) if hasattr(request, "user") else "Anonymous",
            "ip": self._get_client_ip(request),
            "headers": {k: v for k, v in request.META.items() if k.startswith("HTTP_")},
            "content_type": request.content_type,
        }

        # Log body for POST/PUT/PATCH requests (be careful with sensitive data)
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                if request.content_type == "application/json":
                    log_data["body"] = json.loads(request.body.decode("utf-8"))
                else:
                    log_data["body"] = dict(request.POST)
            except Exception:
                log_data["body"] = "Unable to parse body"

        return log_data

    def _log_response(self, response):
        """return the outgoing response data."""
        log_data = {
            "status_code": response.status_code,
            "headers": dict(response.items()),
        }

        # Log response body for non-binary responses (optional, can be verbose)
        if hasattr(response, "content") and response.get("Content-Type", "").startswith(
            "application/json"
        ):
            try:
                content = response.content.decode("utf-8")
                if len(content) < 1000:  # Only log if response is small
                    log_data["body"] = json.loads(content)
                else:
                    log_data["body"] = f"Response too large ({len(content)} bytes)"
            except Exception:
                log_data["body"] = "Unable to parse response"

        return log_data

    def _get_client_ip(self, request):
        """Get the client's IP address from the request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
