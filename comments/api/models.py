from django.db import models

class Comment(models.Model):
    """ A comment """
    NAME_MAX_LENGTH = 32

    sku = models.CharField(max_length=8, help_text='The comment\'s associated product SKU')
    content = models.TextField(help_text='The comment\'s textual content')
    created = models.DateTimeField(auto_now_add=True, help_text='The comment\'s creation date and time')
    modified = models.DateTimeField(auto_now=True, help_text='The comment\'s most recent modification date and time')

    @property
    def tone(self):
        """ Get this comment's tone by returning the comment tone value with the maximum score """
        tone = max(self.tones.all(), key=lambda tone: tone.score, default=None)
        if tone is not None:
            return tone.tone_name
        return None

    def __str__(self):
        """ Get comment name in the form of the comment content truncated to NAME_MAX_LENGTH """
        return (self.content[:self.NAME_MAX_LENGTH] + '..') if len(self.content) > self.NAME_MAX_LENGTH else self.content

class CommentTone(models.Model):
    """ The score for a particular tone type (joy, anger, etc) on a comment """
    class Meta:
        unique_together = (('comment_id', 'tone_type'),)

    TONE_CHOICES = (
        (0, 'anger'),
        (1, 'disgust'),
        (2, 'fear'),
        (3, 'joy'),
        (4, 'sadness'),
    )

    comment_id = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='tones', help_text='The comment tone\'s associated comment')
    tone_type = models.IntegerField(choices=TONE_CHOICES, help_text='The comment tone\'s type (joy, anger, etc)')
    score = models.FloatField(help_text='The comment tone\'s score value')
    created = models.DateTimeField(auto_now_add=True, help_text='The comment tone\'s creation date and time')
    modified = models.DateTimeField(auto_now=True, help_text='The comment tone\'s most recent modification date and time')

    @property
    def tone_name(self):
        """ Get this tone type's name """
        return next((tone_name for tone_id, tone_name in self.TONE_CHOICES if tone_id == self.tone_type), 'Unknown')

    def __str__(self):
        """ Get comment tone name in the form "tone_name: score" """
        return '{}: {}'.format(self.tone_name.capitalize(), self.score)
