## Plugin list (/api/1.0/plugins/) ##

Returns list of the plugins matching the specified criteria.

**URL**: [http://exchange.munin-monitoring.org/api/1.0/plugins/](http://exchange.munin-monitoring.org/api/1.0/plugins/)  
**Parameters**:

  - format (optional) 	- json / xml
  - title (optional)		- part of the plugin title
  - category (optional) 	- category names seperated by a comma
  - platforms (optional)	- platforms seperated by a comma
  - language (optional)	- programming language name
  - tags (optional)		- the list of tags seperated by a comma
  - limit (optional)		- the maximum number of items to return (default = 50)

**Example call**:

> GET: http://exchange.munin-monitoring.org/api/1.0/plugins/?title=mongrel

Returns all the plugins which title starts with "**mongrel**".

**Example response**:

    {
        "meta": {
            "status": "success", 
            "count": 2
        }, 
        "data": [
            {
                "category": "Other", 
                "description": "<p>Graphs the memory consumption of all the mongrel processes on a machine</p>", 
                "title_slug": "mongrel_process_memory", 
                "tags": [
                    "other"
                ], 
                "downloads": 0, 
                "title": "mongrel_process_memory", 
                "latest_version_number": 1, 
                "language": "Ruby", 
                "rating_score": 0, 
                "platforms": [
                    "platform independent"
                ]
            }, 
            {
                "category": "Other", 
                "description": "<p>Shows RSS usage of mongrel processes on Solaris</p>", 
                "title_slug": "mongrel_memory", 
                "tags": [
                    "other"
                ], 
                "downloads": 6, 
                "title": "mongrel_memory", 
                "latest_version_number": 1, 
                "language": "Ruby", 
                "rating_score": 0, 
                "platforms": [
                    "platform independent"
                ]
            }
        ]
    }
    
**Example call**:

> GET: http://exchange.munin-monitoring.org/api/1.0/plugins/?tag=openvpn,memcache&language=perl

Returns all the plugins taggeded with "**openvpn**" OR "**memcached**" written in "**Perl**".

**Example response**:

    {
        "meta": {
            "status": "success", 
            "count": 7
        }, 
        "data": [
            {
                "category": "Other", 
                "description": "<p>Number of connected clients on an openvpn server</p>", 
                "title_slug": "openvpn_clients", 
                "title": "openvpn_clients", 
                "downloads": 0, 
                "tags": [
                    "openvpn"
                ], 
                "latest_version_number": 1, 
                "download_url": "/plugins/openvpn_clients/version/1/download", 
                "language": "Perl", 
                "rating_score": 0, 
                "platforms": [
                    "platform independent"
                ]
            }, 
            {
                "category": "Other", 
                "description": "<p>Monitors the numbers of bytes used in the cache</p>", 
                "title_slug": "memcached_bytes_", 
                "title": "memcached_bytes_", 
                "downloads": 0, 
                "tags": [
                    "memcache"
                ], 
                "latest_version_number": 1, 
                "download_url": "/plugins/memcached_bytes_/version/1/download", 
                "language": "Perl", 
                "rating_score": 0, 
                "platforms": [
                    "platform independent"
                ]
            }, 
            {
                "category": "Other", 
                "description": "<p>Monitors the number of connections to the memcached server</p>", 
                "title_slug": "memcached_connections_", 
                "title": "memcached_connections_", 
                "downloads": 0, 
                "tags": [
                    "memcache"
                ], 
                "latest_version_number": 1, 
                "download_url": "/plugins/memcached_connections_/version/1/download", 
                "language": "Perl", 
                "rating_score": 0, 
                "platforms": [
                    "platform independent"
                ]
            }, 
            ...
        ]
    }
