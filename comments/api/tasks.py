from celery import shared_task
from celery.utils.log import get_task_logger

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import Error
from django.core.cache import cache

from .models import Comment, CommentTone

# Celery logger
logger = get_task_logger(__name__)

@shared_task
def fetch_tone(comment_pk):
    """ Request tone scores from the Watson API and store them """

    # Fetch comment object
    try:
        comment = Comment.objects.get(pk=comment_pk)
    except ObjectDoesNotExist:
        logger.error('Unknown comment object in fetch tone task: {}'.format(comment_pk))
        return

    # Request tone scores from Watson API
    params = {
        'text': comment.content,
        'tones': 'emotion',
        'sentences': 'false',
        'version': settings.WATSON_API_VERSION,
    }
    headers = {'Accept': 'application/json'}
    try:
        response = requests.get(settings.WATSON_API_URL, params=params, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # TODO: Handle status 429 by delaying subsequent tasks
        logger.error('Error response received from Watson API: {}'.format(str(e)))
        return
    except requests.exceptions.RequestException as e:
        # TODO: Handle timeout errors differently (maybe by retrying the task?)
        logger.error('Error requesting from Watson API: {}'.format(str(e)))
        return

    # Parse response
    try:
        data = response.json()
    except ValueError as e:
        logger.error('Unable to parse response from Watson API ("{}"): {}'.format(str(e), response.text))
        return

    # Get tone values from response
    try:
        tone_categories = data['document_tone']['tone_categories']
        tones = next(category['tones'] for category in tone_categories if category['category_id'] == 'emotion_tone')
    except KeyError:
        logger.error('Invalid response format from Watson API: {}'.format(response.text))
        return
    except StopIteration:
        logger.error('No "emotion_tone" category in response from Watson API: {}'.format(response.text))
        return

    # Create comment tone objects
    comment_tones = []
    for tone in tones:

        # Create CommentTone object
        try:
            comment_tone = CommentTone(comment_id=comment, score=tone['score'])
        except KeyError:
            logger.error('No tone score in response from Watson API: {}'.format(response.text))
            continue

        # Set type
        try:
            comment_tone.tone_name = tone['tone_id']
        except KeyError:
            logger.error('No tone ID in response from Watson API: {}'.format(response.text))
            continue
        except ValueError as e:
            logger.error(str(e))
            continue

        # Add to list of this comment's tones
        comment_tones.append(comment_tone)

    # Delete any existing comment tones from the database
    try:
        comment.tones.all().delete()
    except Error as e:
        logger.error('Error deleting existing comment tones: {}'.format(e))
        return

    # Add new comment tones to database
    try:
        CommentTone.objects.bulk_create(comment_tones)
    except Error as e:
        logger.error('Error adding comment tones: {}'.format(e))
        return

    # Invalidate cache
    # TODO: Only invalidate the relevant cache keys instead of clearing the whole cache
    # as this is currently killing performance!
    cache.clear()
