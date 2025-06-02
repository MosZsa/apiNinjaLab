class SessionAuth:
    def __call__(self, request):
        if request.user and request.user.is_authenticated:
            return request.user
        return None
