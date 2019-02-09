
<!-- This file is auto generated. Do not edit it. Any modifications will be -->
<!-- overwritten next time documentation is generated. The source for this file -->
<!-- resides in <repo_root>/doc/sphinx directory. Modify there and execute -->
<!-- `make all` in that directory. -->

# Command line operations on your alerts, dashboards

In this document we describe general tasks using the command line that you can accomplish with `wavectl` using your alerts and dashboards.

Many of these examples can be accomplished by using the Wavefront gui too. `wavectl` enables accomplishing these tasks in a command line interface and in conjunction with powerful tools like `grep`, `awk`, `sed`, [`jq`](https://stedolan.github.io/jq/), or similar

## Print one line summaries of your alerts, dashboards.

`wavectl` can be used to list all alerts in a one line summary form.

For example:

``` 
  $ wavectl show alert
  ID               NAME                                                                                     STATUS                              SEVERITY    
  1530723441304    Kubernetes - Node Network Utilization - HIGH (Prod)                                      CHECKING                            WARN      
  1530723441442    Kubernetes - Node Cpu Utilization - HIGH (Prod)                                          CHECKING                            WARN      
  1530723441589    Kubernetes - Node Memory Swap Utilization - HIGH (Prod)                                  SNOOZED                             WARN      
  1530723441737    Wavefront Freshness                                                                      CHECKING                            WARN      
  ...
```

The short summary form contains the [alert state](https://docs.wavefront.com/alerts_states_lifecycle.html#alert-states) and the severity in addition to the name and unique id of the alert. Once you have a structured columned print of your alerts, you can do all sorts of processing with them.

For example:

### Find the alerts firing right now.

``` 
  $ wavectl show alert | grep FIRING
  1530723442180    Orion Response time more than 2 seconds                                                  FIRING                              INFO
```

This could be used from a script too. For example, an operator may want to ensure no alerts from "kubernetes" are firing before executing a script that is going to downtime one of the kubernetes control plane hosts.

### Count the total number of alerts in your organization.

``` 
  $ wavectl show --no-header alert | wc -l
        14
```

## Inspect all attributes of alerts, dashboards.

In addition to printing one line summaries the `show` command can also print detailed state of your alerts in json form:

``` 
  $ wavectl show -o json alert
  {
      "additionalInformation": "This alert tracks the used network bandwidth percentage for all the compute-* (compute-master and compute-node) machines. If the cpu utilization exceeds 80%, this alert fires.",
      "condition": "ts(proc.net.percent,server_type=\"compute-*\" and env=\"live\") > 80",
      "displayExpression": "ts(proc.net.percent,server_type=\"compute-*\" and env=\"live\")",
      "id": "1530723441304",
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
      "target": "pd: 07fe9ebacf8c44e881ea2f6e44dbf2d2"
  }
  {
      "additionalInformation": "This alert tracks the used cpu percentage for all the compute-* (compute-master and compute-node) machines. If the cpu utilization exceeds 80%, this alert fires.",
  ...
```

One you have an easy way to retrieve the json representation of alerts, dashboards, this can lead to various powerful use cases with using text processing tools like [`jq`](https://stedolan.github.io/jq/) or grep. For example:

### Print the name and the [condition](https://docs.wavefront.com/alerts_states_lifecycle.html#alert-conditions) for each alert.

``` 
  $ wavectl show -o json alert | jq '{name,condition}'
  {
    "name": "Kubernetes - Node Network Utilization - HIGH (Prod)",
    "condition": "ts(proc.net.percent,server_type=\"compute-*\" and env=\"live\") > 80"
  }
  {
    "name": "Kubernetes - Node Cpu Utilization - HIGH (Prod)",
    "condition": "ts(proc.stat.cpu.percentage_used,server_type=\"compute-*\" and env=\"live\") > 80"
  }
  {
    "name": "Kubernetes - Node Memory Swap Utilization - HIGH (Prod)",
    "condition": "ts(proc.meminfo.percentage_swapused,server_type=\"compute-*\" and env=\"live\") > 10"
  ...
```

### See the existing usages of a particular metric.

You may want to see a metric's usages in all dashboard queries. You may be unsure about the semantics of a metric and seeing its correct usages definitely helps.

Dashboards' json state can be inspected similarly to alerts. Seeing all dashboard queries regarding haproxy backends:

``` 
  $ wavectl show -o json dashboard | grep haproxy_backend
                                      "query": "ts(octoproxy.haproxy_backend_connections_total, ${dev})",
                                      "query": "rate(ts(octoproxy.haproxy_backend_connections_total, ${dev}))",
                                      "query": "ts(octoproxy.haproxy_backend_response_errors_total, ${dev})",
                                      "query": "ts(octoproxy.haproxy_backend_retry_warnings_total, ${dev})",
                                      "query": "ts(octoproxy.haproxy_backend_up, ${dev})",
                                      "query": "ts(octoproxy.haproxy_backend_connections_total, env=live)",
                                      "query": "rate(ts(octoproxy.haproxy_backend_connections_total, env=live))",
                                      "query": "ts(octoproxy.haproxy_backend_retry_warnings_total, env=live)",
                                      "query": "ts(octoproxy.haproxy_backend_response_errors_total, env=live)",
                                      "query": "ts(octoproxy.haproxy_backend_up, env=live)",
```

### See existing usages of advanced Wavefront functions.

Some advanced functions in [Wavefront query language](https://docs.wavefront.com/query_language_reference.html) are not the easiest to learn. It is always helpful to see existing usages of a Wavefront function by your colleagues before writing your own. Take the [taggify](https://docs.wavefront.com/ts_taggify.html) as an example.

``` 
  $ wavectl show -o json dashboard | grep taggify
                                      "query": "rawsum(aliasMetric(taggify(${RdyCalicUncrdndNdsWithPod},metric,pod,0),tagk,node,\"(.*)\",\"$1\"),pod,dc,metrics)",
                                      "query": "rawsum(taggify(${NotReadyCalicoPodsWithNodeInMetrics},metric,node,0),node,dc)",
                                      "query": "taggify(${RdyCalicUncrdndNds},tagk,node,node,0)",
                                      "query": "rawsum(taggify(${BirdUp},source,node,0),node,dc)",
                                      "query": "taggify(${RdyCalicUncrdndNds},tagk,node,node,0)",
                                      "query": "rawsum(taggify(${BgpState},source,node,0),node,dc)",
                                      "query": "taggify(${RdyCalicUncrdndNds},tagk,node,node,0)",
```

> After textually inspecting the alert, dashboard state you may want to jump to the Wavefront gui and see the time series there. For that you can use the wavectl [browser integration](BrowserIntegration.md).

### See all sections in all your dashboards.

``` 
  $ wavectl show -o json dashboard | jq '{name: .name, sections: [.sections[].name]}'
  {
    "name": "Skynet Octoproxy Dev",
    "sections": [
      "Vitals",
      "getEndpoints",
      "lbRestart",
      "getServices",
      "HA Proxy Backend Metrics",
      "HAProxy Frontend Metrics"
    ]
  }
  {
    "name": "Data Retention",
    "sections": [
      "Retention",
      "Disposition",
      "Disposition Notifications Runmode - Sundays"
    ]
  }
  ...
```
