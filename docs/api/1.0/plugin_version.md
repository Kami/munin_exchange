## Plugin version details (/api/1.0/plugin/&lt;title-slug&gt;/version/&lt;version number&gt;) ##

Returns the details for the specified plugin version.

**URL**: [http://exchange.munin-monitoring.org/api/1.0/plugin/&lt;title-slug&gt;/version/&lt;version number&gt;](http://exchange.munin-monitoring.org/api/1.0/plugin/<title-slug>/version/<version number>)  
**Parameters**:

  - format (optional) 	- json / xml
  - title_slug (required) - plugin title slug
  - version number (required) - plugin version number

**Example call**:

> GET: http://exchange.munin-monitoring.org/api/1.0/plugin/apache_watch_/version/1

Returns the details for the version "**1**" of the plugin with a title slug "**apache_watch_**".

**Example response**:

    {
        "meta": {
            "status": "success", 
            "count": 1
        }, 
        "data": {
            "submitted_by": "Kami", 
            "version_number": 1, 
            "author": "Bjørn Ruberg", 
            "notes": "initial release.", 
            "date_submitted": "2010-05-25 09:48:05", 
            "download_url": "/plugins/apache_watch_/version/1/download"
        }
    }