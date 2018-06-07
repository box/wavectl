
<!-- This file is auto generated. Do not edit it. Any modifications will be -->
<!-- overwritten next time documentation is generated. The source for this file -->
<!-- resides in <repo_root>/doc/sphinx directory. Modify there and execute -->
<!-- `make all` in that directory. -->

# Launch Wavefront GUI via `wavectl`

Wavefront has an amazing GUI that we all love and use regularly. With its great performance and design, it significantly enables us to analyze our metrics. As a command line client to Wavefront, `wavectl` cannot replace the powerful GUI and all the crucial use cases addressed by the GUI. It was imperative for `wavectl` users to be able to switch to Wavefront GUI effortlessly. Because of that, we have build an `--in-browser` option into the [`show`](CommandReference.md#show-options) command. With `--in-browser`, the `show` command launches new browser tabs and loads your selected alerts and dashboards.

For example say you want to investigate your alerts that have the name "Kubernetes" in them. You could narrow down your shown alerts with the `--name REGEX` command line option. After you list them in the terminal and are convinved of the selected alerts, you would probably interact with them via the Wavefront GUI. `wavectl` `show` can load all selected alerts in a browser tab with the `--in-browser` option. This saves a lot of clicking in the browser and unncessary copy paste from the command line to the browser.

For example, the following command list all alerts with "Kubernetes" in their name and will create new browser tabs for each selected one and load the Wavefront page to that alert.

``` 
  $ wavectl show --in-browser alert  --name Kubernetes
  ID               NAME                                                                                     STATUS                              SEVERITY    
  1523082347619    Kubernetes - Node Network Utilization - HIGH (Prod)                                      CHECKING                            WARN      
  1523082347824    Kubernetes - Node Cpu Utilization - HIGH (Prod)                                          CHECKING                            WARN      
  1523082348005    Kubernetes - Node Memory Swap Utilization - HIGH (Prod)                                  SNOOZED                             WARN
```

Similarly, the following views all Metadata dashboards in Wavefront GUI.

``` 
  $ wavectl show --in-browser dashboard  --name Metadata
  ID                      NAME                                                        DESCRIPTION                                                                                         
  metadata-operations     Metadata Operations                                         Metrics about each operation that can be performed against the data store                           
  metadata-perfpod        Metadata PerfPod                                            Monitors for testing Metadata in the PerfPods                                                       
  metadata-php            Metadata PHP                                                Monitors for Metadata in the PHP webapp
```
