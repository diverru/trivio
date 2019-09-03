import logging
import requests
import requests.exceptions
import time

from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework import serializers
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from trivio_backend.core import models
from django.db.models import Q

# TODO: configure logging

logger = logging.getLogger(__name__)


def call_external_api(url, max_attempts=3, timeout=5, retry_interval=0.5):
    for attempt in range(max_attempts):
        try:
            logger.info(f"calling API {url}, attempt {attempt + 1}")
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200:
                logger.info(f"API call successful")
                return r.json()
            logger.info(f"got HTTP {r.status_code}")
        except requests.exceptions.RequestException:
            logger.exception('')
        time.sleep(retry_interval)
        retry_interval *= 1.5
    logger.info("giving up to call API")
    return None


@api_view(["POST"])
def auth_signup(request):
    """add documentation string here **hello**
    # its title
    """
    email = request.POST["email"]
    # TODO: check email
    # TODO: enrich user
    username = request.POST["username"]
    password = request.POST["password"]
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")

    if models.User.objects.filter(Q(username=username) | Q(email=email)).exists():
        return Response({
            "error": "user with this email or nickname already exists"
        }, status=status.HTTP_409_CONFLICT)

    user = models.User.objects.create(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
    )
    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }, status=status.HTTP_201_CREATED)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = ["id", "user", "num_likes", "timestamp", "content", "title"]

    user = serializers.PrimaryKeyRelatedField(queryset=models.User.objects, style={'base_template': 'input.html'})
    num_likes = serializers.SerializerMethodField()

    @staticmethod
    def get_num_likes(obj):
        return obj.likes.count()


class PostItems(ListCreateAPIView):
    permission_classes = (ReadOnly|IsAuthenticated, )
    queryset = models.Post.objects
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostItemDetail(RetrieveAPIView):
    queryset = models.Post.objects
    serializer_class = PostSerializer


@api_view(["POST"])
@permission_classes((IsAuthenticated, ))
def like_post(request, pk):
    post = models.Post.objects.get(pk=pk)
    if post.user == request.user:
        return Response({
            "error": "self-liking is not allowed",
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    post.likes.add(request.user)
    return Response({
        "num_likes": post.likes.count(),
    })


@api_view(["POST"])
@permission_classes((IsAuthenticated, ))
def unlike_post(request, pk):
    post = models.Post.objects.get(pk=pk)
    post.likes.remove(request.user)

    return Response({
        "num_likes": post.likes.count(),
    })
