from django.http import HttpResponseNotAllowed

class AllowedMethodsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define allowed methods for each endpoint
        self.allowed_methods = {
            '/login': ['POST'],
            '/register': ['POST'],
            '/categories': ['GET', 'POST'],
            '/inventory': ['GET', 'POST', 'PUT', 'DELETE'],
            '/inventory/add-remove-stock': ['PUT'],
            '/inventory/summary': ['GET'],
        }

    def __call__(self, request):
        path = request.path
        if path in self.allowed_methods:
            if request.method not in self.allowed_methods[path]:
                return HttpResponseNotAllowed(
                    self.allowed_methods[path],
                    content=f"Method {request.method} not allowed for {path}"
                )
        return self.get_response(request)