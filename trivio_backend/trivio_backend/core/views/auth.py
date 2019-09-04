from rest_framework import status, response
from rest_framework.decorators import api_view

from rest_framework_simplejwt.tokens import RefreshToken

from trivio_backend.core import models
from django.db.models import Q
from trivio_backend.core.external import verify_email


@api_view(["POST"])
def auth_signup(request):
    """add documentation string here **hello**
    # its title
    """
    email = request.POST.get("email")
    # TODO: enrich user
    username = request.POST.get("username")
    password = request.POST.get("password")
    if not (email and username and password):
        return response.Response({
            "error": "one of the required field is not specified"
        })
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")

    if models.User.objects.filter(Q(username=username) | Q(email=email)).exists():
        return response.Response({
            "error": "user with this email or nickname already exists"
        }, status=status.HTTP_409_CONFLICT)
    if not verify_email(email):
        return response.Response({
            "error": "email is not valid"
        }, status.HTTP_400_BAD_REQUEST)

    user = models.User.objects.create(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
    )
    refresh = RefreshToken.for_user(user)
    return response.Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }, status=status.HTTP_201_CREATED)
