from rest_framework import viewsets

from .models import Comment
from .serializers import CommentSerializer
from .tasks import fetch_tone

class CommentViewSet(viewsets.ModelViewSet):
    """
    list:
    Return a paginated list of all comments.

    retrieve:
    Return the specified comment.

    create:
    Create a new comment.

    update:
    Update the specified comment.

    partial_update:
    Perform a partial update of the specified comment

    destroy:
    Remove the specified comment
    """
    queryset = Comment.objects.all().order_by('-created')
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        """ Queue fetch tone task after creating comment """
        super(CommentViewSet, self).perform_create(serializer)
        self._fetch_tone(serializer.instance)

    def perform_update(self, serializer):
        """ Queue fetch tone task after updating comment """
        super(CommentViewSet, self).perform_update(serializer)
        self._fetch_tone(serializer.instance)

    def _fetch_tone(self, instance):
        fetch_tone.delay(instance.pk)
