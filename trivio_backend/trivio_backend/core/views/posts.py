import logging

from rest_framework import status, permissions, serializers, generics, response
from rest_framework.decorators import api_view, permission_classes

from trivio_backend.core import models
from trivio_backend.core.utils import ReadOnly


logger = logging.getLogger(__name__)


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = ["id", "user", "num_likes", "timestamp", "content", "title"]

    user = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects,
        style={'base_template': 'input.html'},
        required=False
    )
    num_likes = serializers.SerializerMethodField()

    @staticmethod
    def get_num_likes(obj):
        return obj.likes.count()


class PostItems(generics.ListCreateAPIView):
    permission_classes = (ReadOnly|permissions.IsAuthenticated, )
    queryset = models.Post.objects
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostItemDetail(generics.RetrieveAPIView):
    queryset = models.Post.objects
    serializer_class = PostSerializer


@api_view(["POST"])
@permission_classes((permissions.IsAuthenticated, ))
def like_post(request, pk):
    post = models.Post.objects.get(pk=pk)
    if post.user == request.user:
        return response.Response({
            "error": "self-liking is not allowed",
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    post.likes.add(request.user)
    return response.Response({
        "num_likes": post.likes.count(),
    })


@api_view(["POST"])
@permission_classes((permissions.IsAuthenticated, ))
def unlike_post(request, pk):
    post = models.Post.objects.get(pk=pk)
    post.likes.remove(request.user)

    return response.Response({
        "num_likes": post.likes.count(),
    })
