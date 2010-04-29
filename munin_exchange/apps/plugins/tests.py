import unittest

from django.test import TestCase
from django.test.client import Client

class PluginViewsTestCase(TestCase):
	fixtures = ['munin_exchange_import.json']
	
	def setUp(self):
		self.client = Client()
		
	def test_plugins_index(self):
		response = self.client.get('/plugins/')
		
		self.failUnlessEqual(response.status_code, 200)
		
	def test_plugins_valid_pages(self):
		response1 = self.client.get('/plugins/?filter=category:Databases')
		response2 = self.client.get('/plugins/?filter=category:Databases&filter=tag:apache')
		response3 = self.client.get('/plugins/?filter=category:unknown&filter=tag:apache')
		response4 = self.client.get('/plugins/?filter=tag:apache')
		response5 = self.client.get('/plugins/?sort=language:&sort=date_submitted:asc&filter=tag:memcache')
		response7 = self.client.get('/plugins/apache_watch_/details')
		response6 = self.client.get('/plugins/?sort=language:')
		response8 = self.client.get('/plugins/?sort=language:asc')
		response9 = self.client.get('/plugins/?sort=language:&sort=date_submitted:asc&filter=tag:memcache&filter=category:Other')
		response10 = self.client.get('/plugins/apache_watch_/version/1')
		response11 = self.client.get('/plugins/apache_watch_/versions')
		response12 = self.client.get('/plugins/apache_watch_/relatives')
		response13 = self.client.get('/plugins/apache_watch_/version/1/raw')
		response14 = self.client.get('/plugins/apache_watch_/version/1/download')
		
		self.failUnlessEqual(response1.status_code, 200)
		self.failUnlessEqual(response2.status_code, 200)
		self.failUnlessEqual(response3.status_code, 200)
		self.failUnlessEqual(response4.status_code, 200)
		self.failUnlessEqual(response5.status_code, 200)
		self.failUnlessEqual(response6.status_code, 200)
		self.failUnlessEqual(response7.status_code, 200)
		self.failUnlessEqual(response7.status_code, 200)
		self.failUnlessEqual(response8.status_code, 200)
		self.failUnlessEqual(response9.status_code, 200)
		self.failUnlessEqual(response10.status_code, 200)
		self.failUnlessEqual(response11.status_code, 200)
		self.failUnlessEqual(response12.status_code, 200)
		self.failUnlessEqual(response13.status_code, 200)
		self.failUnlessEqual(response14.status_code, 200)
		
	def test_plugins_without_screenshot(self):
		response1 = self.client.get('/plugins/snmp_zyxel_zywall__cpu/details')
		response2 = self.client.get('/plugins/xen_memory/details')
		response3 = self.client.get('/plugins/xen_cpu_v2/details')
		response4 = self.client.get('/plugins/dovecot126/details')
		
		self.failUnlessEqual(response1.status_code, 200)
		self.failUnlessEqual(response2.status_code, 200)
		self.failUnlessEqual(response3.status_code, 200)
		self.failUnlessEqual(response4.status_code, 200)
		
	def test_404_pages(self):
		response1 = self.client.get('/plugins/non-existent')
		response2 = self.client.get('/plugins/non-existent/details/')
		response3 = self.client.get('/plugins/apache_watch_/version/9/')
		response4 = self.client.get('/plugins/apache_watch_/version/9/download/')
		
		self.failUnlessEqual(response1.status_code, 301)
		self.failUnlessEqual(response2.status_code, 404)
		self.failUnlessEqual(response3.status_code, 404)
		self.failUnlessEqual(response4.status_code, 404)