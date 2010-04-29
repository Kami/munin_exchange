## Plugin relatives (/api/1.0/plugin/&lt;title-slug&gt;/relatives) ##

Returns all the relatives for the given plugin.  
Relatives are plugins which have the same name and output but are available for different platform.

**URL**: [http://exchange.munin-monitoring.org/api/1.0/plugin/&lt;title-slug&gt;/relatives](http://exchange.munin-monitoring.org/api/1.0/plugin/<title-slug>/relatives)  
**Parameters**:

  - format (optional) 	- json / xml
  - title_slug (required) - plugin title slug

**Example call**:

> GET: http://exchange.munin-monitoring.org/api/1.0/plugin/apache_watch_/relatives

Returns all the relatives of a plugin with a title slug "**apache_watch_**" (in this case, there are two).

**Example response**:

    {
        "meta": {
            "status": "success", 
            "count": 2
        }, 
        "data": [
            {
                "category": "Databases", 
                "description": "<p>test description</p>", 
                "title_slug": "apache_watch_-2", 
                "title": "apache_watch_", 
                "downloads": 0, 
                "tags": [
                    "scala", 
                    "ubuntu", 
                    "monitoring"
                ], 
                "latest_version_number": 1, 
                "download_url": "/plugins/apache_watch_-2/version/1/download", 
                "language": "Scala", 
                "rating_score": 0, 
                "platforms": [
                    "irix"
                ]
            }, 
            {
                "category": "Databases", 
                "description": "<p>Plugin for NetBSD.</p>", 
                "title_slug": "apache_watch_-3", 
                "title": "apache_watch_", 
                "downloads": 0, 
                "tags": [
                    "apache", 
                    "httpd", 
                    "web server", 
                    "requests", 
                    "watch"
                ], 
                "latest_version_number": 1, 
                "download_url": "/plugins/apache_watch_-3/version/1/download", 
                "language": "Ruby", 
                "rating_score": 0, 
                "platforms": [
                    "NetBSD"
                ]
            }
        ]
    }
    
**Example call**:

> GET: http://exchange.munin-monitoring.org/api/1.0/plugin/uustat/relatives

Returns all the relatives of a plugin with a title slug "**uustat**" (this plugin has no relatives, so empty list is returned).

**Example response**:

    {
        "meta": {
            "status": "success", 
            "count": 0
        }, 
        "data": []
    }