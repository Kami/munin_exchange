## Plugin versions (/api/1.0/plugin/&lt;title-slug&gt;/versions) ##

Returns the list of all the versions for the specified plugin.

**URL**: [http://exchange.munin-monitoring.org/api/1.0/plugin/&lt;title-slug&gt;/versions](http://exchange.munin-monitoring.org/api/1.0/plugin/<title-slug>/versions)  
**Parameters**:

  - format (optional) 	- json / xml
  - title_slug (required) - plugin title slug

**Example call**:

> GET: http://exchange.munin-monitoring.org/api/1.0/plugin/apache_watch_/versions

Returns all the versions for the plugin with a title slug "**apache_watch_**".

**Example response**:

    {
        "meta": {
            "status": "success", 
            "count": 2
        }, 
        "data": [
            {
                "submitted_by": "Kami", 
                "version_number": 2, 
                "author": "Janez Novak", 
                "notes": "version notes", 
                "date_submitted": "2010-05-30 15:39:00", 
                "download_url": "/plugins/apache_watch_/version/2/download"
            }, 
            {
                "submitted_by": "Kami", 
                "version_number": 1, 
                "author": "Bjørn Ruberg", 
                "notes": "initial release.", 
                "date_submitted": "2010-05-25 09:48:05", 
                "download_url": "/plugins/apache_watch_/version/1/download"
            }
        ]
    }