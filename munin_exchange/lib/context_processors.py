import redis
import pickle
import random

from plugins.views import get_latest_plugins, \
    get_most_downloaded_plugins, get_top_rated_plugins
from core.views import get_latest_comments
from plugins.models import Plugin
from tag_cloud import calculate_cloud

def plugins_tag_cloud(request, count = 15):

    redis_instance = redis.Redis()
    tag_cloud = redis_instance.get('plugins.tag_cloud')

    if not tag_cloud:
        tag_cloud = calculate_cloud()
        tag_cloud = pickle.dumps(tag_cloud)
        redis_instance.set('plugins.tag_cloud', tag_cloud)
    else:
        tag_cloud = pickle.loads(tag_cloud)

    if not isinstance(tag_cloud, list):
        tag_cloud = []
    else:
        random.shuffle(tag_cloud)
        tag_cloud = tag_cloud[:count]

    return {
        'tag_cloud': tag_cloud
    }

def plugins_stats_footer(request, count = 4):
    latest_plugins = get_latest_plugins(count)
    latest_comments = get_latest_comments(2)
    most_downloaded_plugins = get_most_downloaded_plugins(count)
    top_rated_plugins = get_top_rated_plugins(count)

    return {
        'latest_plugins': latest_plugins,
        'latest_comments': latest_comments,
        'most_downloaded_plugins': most_downloaded_plugins,
        'top_rated_plugins': top_rated_plugins
     }
