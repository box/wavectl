
<!-- This file is auto generated. Do not edit it. Any modifications will be -->
<!-- overwritten next time documentation is generated. The source for this file -->
<!-- resides in <repo_root>/doc/sphinx directory. Modify there and execute -->
<!-- `make all` in that directory. -->

# Repetitive editing of alerts, dashboards

At times one needs to change multiple alerts or various queries in several dashboards at once. A change in a metric name can cause something like this. For example the metric generator in kubernetes, [kube-state-metrics](https://github.com/kubernetes/kube-state-metrics), occasionally changes a metric's name.

After such a change, the platform owner needs to update all alerts and dashboards with that metric. Searching for that in the Wavefront GUI and updating the queries manually can be very labor intensive, error prone and time consuming. `wavectl` can help with automating such a global change.

For the sake of an example, let's say because of an upsteam change, all metrics that started with `proc.` have been renamed to start with `host.proc.`. Once this upstream change gets deployed, numerous alerts and dashboards will be broken. They will try to display the old metric name and will not show data. In order to quickly fix this problem via `wavectl` we first [`pull`](CommandReference.md#pull-options) all alerts and resources that match the `proc\.` regular expression. The [`--match`](CommandReference#resource-options) option can be used to narrow down the returned set via a regular expression search.

``` 
  $ wavectl pull /tmp/RepetitiveEditing/alerts alert --match "proc\."

  $ wavectl pull /tmp/RepetitiveEditing/dashboards dashboard --match "proc\."
```

See the pulled alerts, dashboards.

``` 
  $ find /tmp/RepetitiveEditing -type f
  /tmp/RepetitiveEditing/alerts/1523082347619.alert
  /tmp/RepetitiveEditing/alerts/1523082347824.alert
  /tmp/RepetitiveEditing/alerts/1523082348005.alert
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard
  /tmp/RepetitiveEditing/dashboards/octoproxy.dashboard
```

See the usage of the metrics starting with `proc.` in pulled alerts, dashboards.

``` 
  $ find /tmp/RepetitiveEditing -type f | xargs grep "proc."
  /tmp/RepetitiveEditing/alerts/1523082347619.alert:    "condition": "ts(proc.net.percent,server_type=\"compute-*\" and env=\"live\") > 80",
  /tmp/RepetitiveEditing/alerts/1523082347619.alert:    "displayExpression": "ts(proc.net.percent,server_type=\"compute-*\" and env=\"live\")",
  /tmp/RepetitiveEditing/alerts/1523082347824.alert:    "condition": "ts(proc.stat.cpu.percentage_used,server_type=\"compute-*\" and env=\"live\") > 80",
  /tmp/RepetitiveEditing/alerts/1523082347824.alert:    "displayExpression": "ts(proc.stat.cpu.percentage_used,server_type=\"compute-*\" and env=\"dev\")",
  /tmp/RepetitiveEditing/alerts/1523082348005.alert:    "condition": "ts(proc.meminfo.percentage_swapused,server_type=\"compute-*\" and env=\"live\") > 10",
  /tmp/RepetitiveEditing/alerts/1523082348005.alert:    "displayExpression": "ts(proc.meminfo.percentage_swapused,server_type=\"compute-*\" and env=\"live\")",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(\"proc.kernel.entropy_avail\", host=${metadata_server})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(proc.stat.cpu.percentage_used, ${PerfPod} and host=${metadata_server})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(proc.stat.cpu.percentage_used, ${PerfPod} and host=${metadata_db02})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(proc.stat.cpu.percentage_used, ${PerfPod} and host=${metadata_database})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(proc.stat.cpu.percentage_used, ${PerfPod} and host=${eng01})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(proc.stat.cpu.percentage_used, ${PerfPod} and host=${content01})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(proc.stat.cpu.percentage_iowait, ${PerfPod} and host=${metadata_server})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(proc.stat.cpu.percentage_iowait, ${PerfPod} and host=${metadata_database})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(proc.stat.cpu.percentage_iowait, ${PerfPod} and host=${metadata_db02})",
  ...
```

Then using [`sed`](https://www.gnu.org/software/sed/manual/sed.html) replace all occurances of `proc.` with `host.proc.`

``` 
  $ find /tmp/RepetitiveEditing -type f | xargs sed -i -e 's/proc\./host.proc./g'
```

Check the changes you have make

``` 
  $ find /tmp/RepetitiveEditing -type f | xargs grep "host.proc."
  /tmp/RepetitiveEditing/alerts/1523082347619.alert:    "condition": "ts(host.proc.net.percent,server_type=\"compute-*\" and env=\"live\") > 80",
  /tmp/RepetitiveEditing/alerts/1523082347619.alert:    "displayExpression": "ts(host.proc.net.percent,server_type=\"compute-*\" and env=\"live\")",
  /tmp/RepetitiveEditing/alerts/1523082347824.alert:    "condition": "ts(host.proc.stat.cpu.percentage_used,server_type=\"compute-*\" and env=\"live\") > 80",
  /tmp/RepetitiveEditing/alerts/1523082347824.alert:    "displayExpression": "ts(host.proc.stat.cpu.percentage_used,server_type=\"compute-*\" and env=\"dev\")",
  /tmp/RepetitiveEditing/alerts/1523082348005.alert:    "condition": "ts(host.proc.meminfo.percentage_swapused,server_type=\"compute-*\" and env=\"live\") > 10",
  /tmp/RepetitiveEditing/alerts/1523082348005.alert:    "displayExpression": "ts(host.proc.meminfo.percentage_swapused,server_type=\"compute-*\" and env=\"live\")",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(\"host.proc.kernel.entropy_avail\", host=${metadata_server})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(host.proc.stat.cpu.percentage_used, ${PerfPod} and host=${metadata_server})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(host.proc.stat.cpu.percentage_used, ${PerfPod} and host=${metadata_db02})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(host.proc.stat.cpu.percentage_used, ${PerfPod} and host=${metadata_database})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(host.proc.stat.cpu.percentage_used, ${PerfPod} and host=${eng01})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(host.proc.stat.cpu.percentage_used, ${PerfPod} and host=${content01})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(host.proc.stat.cpu.percentage_iowait, ${PerfPod} and host=${metadata_server})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(host.proc.stat.cpu.percentage_iowait, ${PerfPod} and host=${metadata_database})",
  /tmp/RepetitiveEditing/dashboards/metadata-perfpod.dashboard:                                    "query": "ts(host.proc.stat.cpu.percentage_iowait, ${PerfPod} and host=${metadata_db02})",
  ...
```

Replace the Wavefront alerts and dashboards using [`wavectl push`](CommandReference.md#push-options)

``` 
  $ wavectl push /tmp/RepetitiveEditing/alerts alert
  Replaced alert(s):
  ID               NAME                                                       STATUS    SEVERITY    
  1523082347619    Kubernetes - Node Network Utilization - HIGH (Prod)            WARN    
  1523082347824    Kubernetes - Node Cpu Utilization - HIGH (Prod)                WARN    
  1523082348005    Kubernetes - Node Memory Swap Utilization - HIGH (Prod)        WARN

  $ wavectl push /tmp/RepetitiveEditing/dashboards dashboard
  Replaced dashboard(s):
  ID                  NAME                DESCRIPTION                                      
  metadata-perfpod    Metadata PerfPod    Monitors for testing Metadata in the PerfPods    
  octoproxy           Skynet Octoproxy    One look summary about the load balancer
```

After these steps all your alerts and dashboards in Wavefront will use the new metric names.

> NOTE: Doing local modifications via `sed` like commands and writing the resulting files to Wavefront may be risky and dangerous. Some unintended changes may be written to Wavefront by mistake. If you want to execute safer local modifications, where you have a better handle on the resulting diff, take a look at the [git integration to push command](GitIntegration.md) section.
