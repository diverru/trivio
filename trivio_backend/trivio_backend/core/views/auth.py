from rest_framework import status, response
from rest_framework.decorators import api_view

from rest_framework_simplejwt.tokens import RefreshToken

from trivio_backend.core import models
from django.db.models import Q
from trivio_backend.core.external import verify_email, enrich_email


def update_field_if_empty(obj, field_name, new_value):
    if new_value and not getattr(obj, field_name):
        setattr(obj, field_name, new_value)


def get_dict_value(root, path):
    parts = path.split("/")
    for part in parts:
        root = root.get(part)
        if root is None:
            return None
    return root


def enrich_user(email, user):
    extra_data = enrich_email(email)
    update_field_if_empty(user, "first_name", get_dict_value(extra_data, "name/givenName"))
    update_field_if_empty(user, "last_name", get_dict_value(extra_data, "name/familyName"))
    update_field_if_empty(user, "location", get_dict_value(extra_data, "location"))
    user.save()


@api_view(["POST"])
def auth_signup(request):
    """add documentation string here **hello**
    # its title
    """
    email = request.POST.get("email")
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
    enrich_user(email, user)
    refresh = RefreshToken.for_user(user)
    return response.Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }, status=status.HTTP_201_CREATED)
