
<!-- This file is auto generated. Do not edit it. Any modifications will be -->
<!-- overwritten next time documentation is generated. The source for this file -->
<!-- resides in <repo_root>/doc/sphinx directory. Modify there and execute -->
<!-- `make all` in that directory. -->

# Simple templating of alerts, dashboards

Wavefront alerts and dashboards are very powerful tools at developers' hands. With Wavefront's monitoring capabilities, programmers can gain great insights about of all sorts of applications. With that great versatility, we have seen the alert and dashboard arsenals of our application owners grow organically in an ad-hoc way.

Different teams have re-discovered almost identical best practices. Various different ways of formulating the same query have independently spread in the organization. For example, we have seen different teams use slightly different metrics and conditions for their high CPU consumption alerts. Sometimes we discover a more robust, improved way of building a query. That knowledge does not spread across teams fast enough to quickly benefit the entire organization. With these concerns, we thought to add more structure to our Wavefront state and experimented with templating using `wavectl.` In this document we give a brief introduction how `wavectl` can be used for simple templating.

Templated alerts, dashboards can be very a comprehensive feature and its implementation could become very complex. At the start with `wavectl`, we kept the templating capabilities limited and simple. Lets go over an example and later on we discuss the limitations and future work. The following sections focus on only templated alerts for brevity reasons. The commands and capabilities easily expand to dashboards too.

## Generate the template files first time.

### Choose which alerts to templetize.

Some problematic observations are common in various applications. For example high cpu, memory... consumption. With containers and [Kubernetes](https://kubernetes.io/) orchestration framework, we get some more additional common observations like:

  - Too many container restarts.

  - Too many Pod restarts.

  - Too many Pods stuck at an unhealthy state.

  - Pods getting to close to their ResourceQuota usage.

  - ...

In your organization, first, you need to identify some common observations that would add value to numerous teams. The purpose of an alert templating exercise should be to simplify and improve many teams' monitoring capabilities. Once you select a common observation, you may discover distinct Wavefront alerts that detect the same problem. They may be implemented differently or may not maintained similarly. Those would be good candidates for templetizing.

### Download json files of alerts from Wavefront.

Wavefront GUI has really powerful user experience.

  - [Charts](https://docs.wavefront.com/charts.html) react instantly to changing queries.

  - Alerts have a [backtesting](https://docs.wavefront.com/alerts.html#backtesting) mode helping to avoid false positives and negatives.

  - Autocomplete [dropdown](https://docs.wavefront.com/metrics_managing.html) menus for metric name completion.

Because of these and many other features, we strongly believe the Wavefront GUI is the right medium for developing new alerts and dashboards. If there is a need to templetize an alert, an initial version of that alert would have been implemented via the Wavefront GUI already.

With that observation, the first step to generate the alert templates is to download the json representation of the alerts from Wavefront. In this example, a service called collections-service has some good alerts. We want to build templates from them so that they can be easily used by other teams too. The [`pull`](CommandReference.md#pull-options) command is used to download the alerts.

``` 
  $ wavectl pull /tmp/Templating/alerts alert -t collections-service
```

After pulling the alerts you can see them in the target directory.

``` 
  $ ls /tmp/Templating/alerts
  1530723442872.alert
  1530723443002.alert
  1530723443146.alert
```

They are in json format:

``` 
  $ cat /tmp/Templating/alerts/*
  {
      "condition": "sum(ts(kube.metrics.deployment_status_replicas_available, namespace=collections-service-dev)) < sum(ts(kube.metrics.deployment_status_replicas, namespace=collections-service-dev))",
      "displayExpression": "sum(ts(kube.metrics.deployment_status_replicas_available, namespace=collections-service-dev))",
      "id": "1530723442872",
      "minutes": 10,
      "name": "Collections Dev Pod Count Low",
      "severity": "SEVERE",
      "tags": {
          "customerTags": [
              "collections-service",
              "core-frameworks"
          ]
      },
      "target": "pd: c6cce4d0d93345a6ab0b76ce1a3b1498"
  }{
  ...
```

> NOTE: In this example there are a small number of alerts. All the concepts and commands discussed here easily expand to many more alerts and dashboards. We kept the data small to have a easy to follow example.

### Convert the json files of alerts into a templating languge.

Once we have the json files downloaded, we need to decide on a templating tool. Since we are working on json files, in this example, we have choosen [jsonnet](https://jsonnet.org/). jsonnet is a very powerful json templating tool and it is used in various other places in kubernetes community. You could use your own favorite templating tool chain, the commands will be different but the main idea stays the same. [Mustache](https://mustache.github.io/) or [go](https://golang.org/pkg/text/template/) templates or even [sed](https://www.gnu.org/software/sed/) commands are suitable for this task.

Converting json files into jsonnet templating language is a one time setup step for templates. It requires jsonnet lanuage know-how. In this example, the before and after json -\> jsonnet files would looke like this:

#### Alert's json file:

``` 
  {
      "condition": "sum(ts(kube.metrics.deployment_status_replicas_available, namespace=collections-service-dev)) < sum(ts(kube.metrics.deployment_status_replicas, namespace=collections-service-dev))",
      "displayExpression": "sum(ts(kube.metrics.deployment_status_replicas_available, namespace=collections-service-dev))",
      "id": "1530723442872",
      "minutes": 10,
      "name": "Collections Dev Pod Count Low",
      "severity": "SEVERE",
      "tags": {
          "customerTags": [
              "collections-service",
              "core-frameworks"
          ]
      },
      "target": "pd: c6cce4d0d93345a6ab0b76ce1a3b1498"
  }
```

#### The corresponding jsonnet template:

We have replaced the hardcoded values for a specific service, with variables that can be overwritten at template complie time. For example, namespace, tag and pagerDuty key.

``` 
  {
    condition: 'sum(ts(kube.metrics.deployment_status_replicas_available, namespace=' + std.extVar('namespace') + ')) < sum(ts(kube.metrics.deployment_status_replicas, namespace=' + std.extVar('namespace') + '))',
    displayExpression: 'sum(ts(kube.metrics.deployment_status_replicas_available, namespace=' + std.extVar('namespace') + '))',
    id: '1530723442872',
    minutes: 10,
    name: '' + std.extVar('namespace') + ' Pod Count Low',
    severity: 'SEVERE',
    tags: {
      customerTags: [
        std.extVar('teamTag'),
        std.extVar('parentTeamTag'),
      ],
    },
    target: std.extVar('pagerDutyKey'),
  }
```

Once this transformation is done, you get the template files. They can be reused to generate Wavefront alerts later on.

## Generate a new set of alerts from templates.

TODO: Add this section

## Future Work.

TODO: Add this section
