# -*- coding: utf-8 -*-
import munin_exchange.lib.bitly as bitly
import twitter
from itertools import chain

from django.conf import settings
from django.template.loader import render_to_string

# Celery
from celery.task import Task
from celery.registry import tasks

from oauthtwitter import OAuthApi

MAX_LENGTH = 135

class SendUpdateToTwitterTask(Task):
	ignore_result = True
	max_retries = 10
	default_retry_delay = 3 * 60 # Retry in 1 minute

	def run(self, plugin_title, version_number = None, platforms = None, category = None, tags = None, url = None, **kwargs):
		""" Sends an update about new plugin submission to the Twitter """
		bit_ly = bitly.Api(login = settings.BITLY_USERNAME, apikey = settings.BITLY_APIKEY)
		twitter_api = OAuthApi(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_SECRET)

		short_url = bit_ly.shorten(url)

		if version_number is None:
			# No version number, assuming this is a new plugin submission
			message = render_to_string('other/twitter_new_plugin.txt',
								{'plugin_title': plugin_title, 'url': short_url})
		else:
			message = render_to_string('other/twitter_new_plugin_version.txt',
								{
									'plugin_title': plugin_title,
									'plugin_version': version_number,
									'url': short_url
								})

		message_len = len(message)
		characters_left = MAX_LENGTH - message_len

		hashtags = []
		categories = [category]
		for tag in chain(platforms, categories, tags):
			tag = tag.replace(' ', '')
			tag = '#%s' % (tag)

			string = ' ' . join(hashtags + [tag])
			hashtags_len = len(string)

			# If there are still some characters left,
			# append the tag
			if hashtags_len < characters_left:
				hashtags.append(tag)

		hashtags_string = ' ' . join(hashtags)
		message = '%s %s' % (message, hashtags_string)

		twitter_api.UpdateStatus(status = message.encode('utf-8'))
