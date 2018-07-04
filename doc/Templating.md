
<!-- This file is auto generated. Do not edit it. Any modifications will be -->
<!-- overwritten next time documentation is generated. The source for this file -->
<!-- resides in <repo_root>/doc/sphinx directory. Modify there and execute -->
<!-- `make all` in that directory. -->

# Simple templating of alerts, dashboards

Wavefront alerts and dashboards are very powerful tools at developers' hands. With Wavefront's monitoring capabilities, programmers can gain great insights about of all sorts of applications. With that great versatility, we have seen the alert and dashboard arsenals of our application owners grow organically in an ad-hoc way.

Different teams have re-discovered almost identical best practices. Various different ways to formuate the same query have independently spread in the organization. For example, we have seen different teams use slightly different metrics and conditions for their high CPU consumption alerts. Sometimes we discover a more robust, improved way of building a query. That knowledge does not spread across teams fast enough to quickly benefit the entire organization. With these concerns, we thought to add more structure to our Wavefront state and experimented with templating using `wavectl.` In this document we give a brief introduction how `wavectl` can be used for simple, templating.

Templated alerts, dashboards can be very a comprehensive feature and its implementation could become very complex. At the start with `wavectl`, we kept the templating capabilities limited and simple. Lets go over an example and later on we discuss the limitations and future work. The following sections focus on only templated alerts for brevity reasons. The commands and capabilities easily expand to dashboards too.

## Generate the template files first time.

Wavefront GUI has really powerful user experience.

  - [Charts](https://docs.wavefront.com/charts.html) react instantly to changing queries.

  - Alerts have a [backtesting](https://docs.wavefront.com/alerts.html#backtesting) mode helping to avoid false positives and negatives.

  - Autocomplete [dropdown](https://docs.wavefront.com/metrics_managing.html) menus for metric name completion.

Because of these and many other features, we strongly believe the Wavefront GUI is the right medium for developing new alerts and dashboards. If there is a need to templetize an alert, that alert would have been implemented via the Wavefront GUI already.

With that observation, the first step to generate the alert templates is to download the json representation of the alerts from Wavefront. The [`pull`](CommandReference.md#pull-options) command accomplishes that.

``` 
  $ wavectl pull /tmp/Templating/alerts alert

  $ ls /tmp/Templating/alerts
  1523082347619.alert
  1523082347824.alert
  1523082348005.alert
  1523082348172.alert
  1523082348348.alert
  1523082348512.alert
  1523082348708.alert
  1523082348877.alert
  1523082349048.alert
  1523082349224.alert
  1523082349397.alert

  $ cat /tmp/Templating/alerts/*
  {
      "additionalInformation": "This alert tracks the used network bandwidth percentage for all the compute-* (compute-master and compute-node) machines. If the cpu utilization exceeds 80%, this alert fires.",
      "condition": "ts(proc.net.percent,server_type=\"compute-*\" and env=\"live\") > 80",
      "displayExpression": "ts(proc.net.percent,server_type=\"compute-*\" and env=\"live\")",
      "id": "1523082347619",
      "minutes": 2,
      "name": "Kubernetes - Node Network Utilization - HIGH (Prod)",
      "resolveAfterMinutes": 2,
      "severity": "WARN",
      "tags": {
          "customerTags": [
              "kubernetes",
              "skynet"
          ]
      },
  ...
```

NOTES:

\\1. Wavefront alerts, dashboards may deviate from templates if users modify them in GUI. \\1. There is no automated process that will continuously equate the templates with the state in Wavefront. \\2. Template generation can be manual. The programmers are free to use any templating language or tooling to convert the json files into templates. We have tried jsonnet, python mustashe template solutions. Some other teammembers have also wrote simple sed commands to convert into templates. \\3. Wavectl is quite opinioted about the file extensions and file names. One may prefer to use the alert name itself as the name of the template. Doing that requires manual work.

ar

Not everything is automated, some manual command execution is necessary. The users of the templates need to spend time to build the template, decide on the variables and best tool to use

may need to and the implementation may need to consider various use cases like:
