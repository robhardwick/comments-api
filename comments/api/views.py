from rest_framework import viewsets

from .models import Comment
from .serializers import CommentSerializer
from .tasks import fetch_tone

class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint to viewing, creating, updating and deleting comments.

    list:
    Return a paginated list of all comments

    The comments are listed in the `results` attribute. To update or delete a specific comment use appropriate method on the `url` attribute. For information on the fields within each comment see the `GET /api/{id}/` docs.

    Clients can move through pages of results by following the URLs in the `next` and `previous` attributes. If there are no succeeding/preceding results then the `next`/`previous` attributes will be `null`.

    The total number of comments across all pages is specified in the `count` attribute.

    retrieve:
    Return the specified comment

    The fields returned are:
    * `sku` - The associated product's SKU
    * `content` - The textual content of the comment
    * `tone` - The tone of the comment as determined by the Watson API (one of anger, disgust, fear, joy or sadness)
    * `created` - The date and time of the comment's creation
    * `modified` - The date and time of the comment's most recent modification

    If the `tone` attribute is `null` then either the Watson API task has not yet been performed or an error was encountered by the task. There is currently no way to determine between these two states.

    Comment URLs should never be built manually, but instead should be determined from other API responses.

    create:
    Create a new comment

    New comments must have the following fields:
    * `sku` - A string with a maximum length of 8 characters representing the product the comment should be associated with
    * `content` - A string containing the textual content of the comment

    update:
    Update the specified comment

    When updating a comment all fields used when creating a comment must be included.

    partial_update:
    Perform a partial update of the specified comment

    A partial update of a comment may be performed with either (or both) of the fields used when creating a comment.

    destroy:
    Remove the specified comment

    When a comment is removed all of its associated tone data will also be deleted.
    """
    queryset = Comment.objects.all().order_by('-created')
    serializer_class = CommentSerializer
    filter_fields = ('sku',)
    ordering = ('created',)

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
