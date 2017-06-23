from rest_framework import serializers

from .models import Comment, CommentTone

class CommentSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:comment-detail')

    class Meta:
        model = Comment
        fields = ('url', 'sku', 'content', 'tone', 'created', 'modified')

