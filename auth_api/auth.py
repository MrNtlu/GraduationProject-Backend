from rest_framework.authentication import TokenAuthentication

class TokenAuthGet(TokenAuthentication):
    def authenticate(self, request):
        token = request.query_params.get("key", False)

        if token and "HTTP_AUTHORIZATION" not in request.META:
            return self.authenticate_credentials(token)
        else:
            return super().authenticate(request)