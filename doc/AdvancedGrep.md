
<!-- This file is auto generated. Do not edit it. Any modifications will be -->
<!-- overwritten next time documentation is generated. The source for this file -->
<!-- resides in <repo_root>/doc/sphinx directory. Modify there and execute -->
<!-- `make all` in that directory. -->

# Advanced grep in your alerts and dashboards.

`wavectl` allows users to execute regular expression searches on alerts and dashboards. Using the [resource options](CommandReference.md#resource-options), the user can specify fields and a regular expression to match for each field. `wavectl` will process only resources that satisfy all specified regular expressions. For `show` command, only the matched alerts/dashboards will be displayed, for `push` only the matching ones will be written to Wavefront, and so on.

For example: show alerts that have "Kubernetes" and "Utilization" in their names:

``` 
  $ wavectl show alert --name "Kubernetes.*Utilization"
  ID               NAME                                                                                     STATUS                              SEVERITY    
  1530723441304    Kubernetes - Node Network Utilization - HIGH (Prod)                                      CHECKING                            WARN      
  1530723441442    Kubernetes - Node Cpu Utilization - HIGH (Prod)                                          CHECKING                            WARN      
  1530723441589    Kubernetes - Node Memory Swap Utilization - HIGH (Prod)                                  SNOOZED                             WARN
```

The `--match` parameter can be used to search anywhere in the json representation of an alert or a dashboard rather than in known key value pairs.

For example: Show the dashboards that use metrics from the live environment

``` 
  $ wavectl show dashboard --match "env=live"
  ID                      NAME                                                        DESCRIPTION                                                                                         
  metadata-php            Metadata PHP                                                Monitors for Metadata in the PHP webapp                                                             
  octoproxy               Skynet Octoproxy                                            One look summary about the load balancer                                                            
  skynet-kube-box-pki     SKYNET KUBE BOX PKISomeNameToBeMachedInKubeBoxPki           Info about PKI system.
```

Write alerts back to Wavefront that have a specific person in the `updaterId`

``` 
  $ wavectl push /tmp/AdvancedGrep/dashboards dashboard --updaterId hbaba
  Replaced dashboard(s):
  ID                      NAME                                                        DESCRIPTION                                                                                         
  SKYNET-OCTOPROXY-DEV    Skynet Octoproxy Dev                                        One look summary about the load balancer                                                            
  data-retention          Data Retention                                              Info about Data                                                                                     
  jgranger001             Skynet Monitoring (Cloned)SomeMatchStringSomeMatchString                                                                                                        
  metadata-operations     Metadata Operations                                         Metrics about each operation that can be performed against the data store                           
  metadata-perfpod        Metadata PerfPod                                            Monitors for testing Metadata in the PerfPods                                                       
  metadata-php            Metadata PHP                                                Monitors for Metadata in the PHP webapp                                                             
  ...
```

`wavectl` uses python standard library's regular expression [module](https://docs.python.org/3.4/library/re.html). Any valid python regular expression can be specified for the [resource options](CommandReference.md#resource-options).
