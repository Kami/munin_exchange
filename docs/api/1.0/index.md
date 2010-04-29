## Munin Exchange REST API (1.0) ##

Here you can find documentation for the Munin Exchange REST API version 1.0.

### General info ###

**API url:** [http://exchange.munin-monitoring.org/api/1.0/&lt;method name&gt;](http://exchange.munin-monitoring.org/api/1.0/<method name>)  
**Response formats:** JSON, XML

### Available methods ###

1. [/api/1.0/plugins/](/docs/api/1-0/plugins/) - returns list of the plugins
1. [/api/1.0/plugin/&lt;title-slug&gt;/details](/docs/api/1-0/plugin_details/) - plugin details
1. [/api/1.0/plugin/&lt;title-slug&gt;/version/&lt;version number&gt;](/docs/api/1-0/plugin_version/) - plugin version details
1. [/api/1.0/plugin/&lt;title-slug&gt;/versions](/docs/api/1-0/plugin_versions/) - plugin versions
1. [/api/1.0/plugin/&lt;title-slug&gt;/relatives](/docs/api/1-0/plugin_relatives/) - plugin relatives

For more information about the available parameters and the response values, click on the method name.

### Return values ###

The response always contains two keys:

- meta - this keys holds information about the response status (success / failure and the number of the results)
- data - the actual data you have requested

Example - success:

> GET: http://exchange.munin-monitoring.org/api/1.0/plugins

    {
        "meta": {
            "status": "success", 
            "count": 50
        }, 
        "data": [
        ....
        ]
    }
    
Example - failure:

> GET: http://exchange.munin-monitoring.org/api/1.0/plugin/nonexistent/details

    {
        "meta": {
            "status": "failure", 
            "error_message": "Plugin with this title_slug does not exist"
        }, 
        "data": null
    }

*Note: default response format for all the requests is JSON.*