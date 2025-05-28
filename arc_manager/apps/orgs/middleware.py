class OrganizationMiddleware:
    """
    Middleware simple para agregar el contexto de organización a las requests
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Agregar la organización del usuario a la request
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.user_organization = request.user.organization
        else:
            request.user_organization = None
            
        response = self.get_response(request)
        return response 