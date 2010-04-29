## Plugin details (/api/1.0/plugin/&lt;title-slug&gt;/details) ##

Returns the details for the specified plugin.

**URL**: [http://exchange.munin-monitoring.org/api/1.0/plugin/&lt;title-slug&gt;/details](http://exchange.munin-monitoring.org/api/1.0/plugin/<title-slug>/details)  
**Parameters**:

  - format (optional) 	- json / xml
  - title_slug (required) - plugin title slug

**Example call**:

> GET: http://exchange.munin-monitoring.org/api/1.0/plugin/apache_watch_/details

Returns the details for the plugin with a title slug "**apache_watch_**".

**Example response**:

    {
        "meta": {
            "status": "success", 
            "count": 1
        }, 
        "data": {
            "category": "Other", 
            "description": "<p>Plugin that graphs Apache activity on different virtual hosts</p>", 
            "title_slug": "apache_watch_", 
            "tags": [
                "apache", 
                "other", 
                "apt", 
                "powerdns"
            ], 
            "downloads": 2, 
            "title": "apache_watch_", 
            "latest_version_number": 2, 
            "download_url": "/plugins/apache_watch_/version/2/download", 
            "language": "Perl", 
            "rating_score": 4, 
            "platforms": [
                "platform independent"
            ]
        }
    }
    
**Notes**: Download URL is always pointing to the latest version.