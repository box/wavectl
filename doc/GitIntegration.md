
<!-- This file is auto generated. Do not edit it. Any modifications will be -->
<!-- overwritten next time documentation is generated. The source for this file -->
<!-- resides in <repo_root>/doc/sphinx directory. Modify there and execute -->
<!-- `make all` in that directory. -->

# Using wavectl with git

One of the advanced features of `wavectl` is its git integration. It can be enabled using the `--inGit,-g` parameter to [pull](CommandReference.md#pull-options), [push](CommandReference.md#push-options) and [create](CommandReference.md#create-options) commands. `wavectl` gets several benefits via git integration that are not immediately obvious. Some effective use cases are as follows:

## Build a git history of alerts, dashboards with [`pull`](CommandReference.md#pull-options)

Wavefront already keeps the change history of [alerts](https://docs.wavefront.com/alerts.html#viewing-alerts-and-alert-history) and [dashboards](https://docs.wavefront.com/dashboards_managing.html#managing-dashboard-versions). Those can be accessed via the browser gui. The powerful Wavefront v2 api also has endpoints to access the histories of [alerts](https://github.com/wavefrontHQ/python-client/blob/355698be1b53a32e81348f92549707dbcb4f6413/wavefront_api_client/api/alert_api.py#L428) and [dashboards](https://github.com/wavefrontHQ/python-client/blob/355698be1b53a32e81348f92549707dbcb4f6413/wavefront_api_client/api/dashboard_api.py#L523). With git integration in `wavectl` we do not add a brand new feature on top of those. Instead, we attempt to make the retrieval of the histories easier via the command line mostly using existing mechanisms in git.

Passing `--inGit` to `pull` command initalizes a git repository in the pulled directory, if the directory gets created with the `pull` command.

``` 
  $ wavectl pull --inGit /tmp/GitIntegrationPull/alerts alert
```

A git repo is created in the newly created /tmp/GitIntegrationPull/alerts directory.

``` 
  $ git -C /tmp/GitIntegrationPull/alerts status
  On branch master
  nothing to commit, working tree clean
```

Each `pull` command creates a new commit with the changes pulled from the Wavefront server at that time.

``` 
  $ git -C /tmp/GitIntegrationPull/alerts log --oneline
  10f895a Added files due to pull <resource> cmd:/Users/hbaba/box/src/skynet/wavectl/doc/bin/wavectl pull --inGit /tmp/GitIntegrationPull/alerts alert
  a8b1ac5 Initial commit with the README.md file
```

If you execute a long running daemon executing periodic pulls from Wavefront, an extensive git history can be built. The git history will correspond to users' edits to alerts and dashboards.

``` 
 while true; do
    wavectl pull <someDir> alert
    wavectl pull <someDir> dashboard
    sleep 300
 done
```

Then, later on, if someone is interested understanding the changes to some alerts or dashboards, the investigation can be done with git show and log commands, which are widely known by programmers already.

For example:

### When was an a particular alert created ?

``` 
  $ git -C /tmp/GitIntegrationPull/alerts log $(ls /tmp/GitIntegrationPull/alerts | sort | head -n 1)
  commit 10f895a6db9812a1f607a09cbcd445ae778524ab
  Author: Hakan Baba <you@example.com>
  Date:   Wed Aug 22 12:55:19 2018 -0700

      Added files due to pull <resource> cmd:/Users/hbaba/box/src/skynet/wavectl/doc/bin/wavectl pull --inGit /tmp/GitIntegrationPull/alerts alert
```

### When were each alert snoozed ?

``` 
  $ git -C /tmp/GitIntegrationPull/alerts log -S snoozed
  commit 10f895a6db9812a1f607a09cbcd445ae778524ab
  Author: Hakan Baba <you@example.com>
  Date:   Wed Aug 22 12:55:19 2018 -0700

      Added files due to pull <resource> cmd:/Users/hbaba/box/src/skynet/wavectl/doc/bin/wavectl pull --inGit /tmp/GitIntegrationPull/alerts alert
```

> NOTE: The updater id and the actual update time for each alert and dashboard can be retrieved using the history endpoing in [Wavefront API](https://docs.wavefront.com/wavefront_api.html). However, in the current `wavectl` implementation, the git commit messages do not contain either of them. In future `wavectl` releases we plan to improve the git integration of pull command to include the updater id and the update time.

## Using [git-diff](https://git-scm.com/docs/git-diff) to make safe local modifications to your alerts, dashboards with [`push`](CommandReference.md#push-options)

In the [repetitive editing doc](RepetitiveEditing.md) we have demonstrated an example using the [`sed`](https://www.gnu.org/software/sed/manual/sed.html) command to search and replace strings on local files. After the modifications, the alert, dashboard json files were written to Wavefront.

It is always good practice to inspect the changes to alerts and dashboards before writing them back to Wavefront with the [`push`](CommandReference.md#push-options) command. The git integration for the push command can provide a diff of local modifications for the user to verify. Since the git integration will work on a local git repo, [git-diff](https://git-scm.com/docs/git-diff) can be used for the diff generation.

Using the same example from the [repetitive editing doc](RepetitiveEditing.md), we first pull the alerts matching a regular expression. But this time we use the git integration command line parameter `--inGit,-g`

``` 
  $ wavectl pull --inGit /tmp/GitIntegrationPush/alerts alert --match "proc\."
```

Then the local modifications are executed:

``` 
  $ find /tmp/GitIntegrationPush -type f | xargs sed -i -e 's/proc\./host.proc./g'
```

See the modifications to alerts that are going to be pushed to Wavefront:

``` 
  $ git -C /tmp/GitIntegrationPush/alerts diff HEAD
  diff --git a/1530723441304.alert b/1530723441304.alert
  index a1bb891..ec02df7 100644
  --- a/1530723441304.alert
  +++ b/1530723441304.alert
  @@ -1,7 +1,7 @@
   {
       "additionalInformation": "This alert tracks the used network bandwidth percentage for all the compute-* (compute-master and compute-node) machines. If the cpu utilization exceeds 80%, this alert fires.",
  -    "condition": "ts(proc.net.percent,server_type=\"compute-*\" and env=\"live\") > 80",
  -    "displayExpression": "ts(proc.net.percent,server_type=\"compute-*\" and env=\"live\")",
  +    "condition": "ts(host.proc.net.percent,server_type=\"compute-*\" and env=\"live\") > 80",
  +    "displayExpression": "ts(host.proc.net.percent,server_type=\"compute-*\" and env=\"live\")",
       "id": "1530723441304",
       "minutes": 2,
       "name": "Kubernetes - Node Network Utilization - HIGH (Prod)",
  diff --git a/1530723441442.alert b/1530723441442.alert
  index ad9e8ef..bb0bf57 100644
  --- a/1530723441442.alert
  +++ b/1530723441442.alert
  @@ -1,7 +1,7 @@
   {
       "additionalInformation": "This alert tracks the used cpu percentage for all the compute-* (compute-master and compute-node) machines. If the cpu utilization exceeds 80%, this alert fires.",
  -    "condition": "ts(proc.stat.cpu.percentage_used,server_type=\"compute-*\" and env=\"live\") > 80",
  -    "displayExpression": "ts(proc.stat.cpu.percentage_used,server_type=\"compute-*\" and env=\"dev\")",
  +    "condition": "ts(host.proc.stat.cpu.percentage_used,server_type=\"compute-*\" and env=\"live\") > 80",
  +    "displayExpression": "ts(host.proc.stat.cpu.percentage_used,server_type=\"compute-*\" and env=\"dev\")",
       "id": "1530723441442",
       "minutes": 2,
       "name": "Kubernetes - Node Cpu Utilization - HIGH (Prod)",
  diff --git a/1530723441589.alert b/1530723441589.alert
  index e7a0d7f..830d19f 100644
  --- a/1530723441589.alert
  +++ b/1530723441589.alert
  ...
```

Submit your changes to the local repo:

``` 
  $ git -C /tmp/GitIntegrationPush/alerts commit -a -m "proc. is replaced with host.proc."
  [master 7cf998e] proc. is replaced with host.proc.
   4 files changed, 21 insertions(+), 21 deletions(-)
   rewrite 1530723443146.alert (67%)
```

> NOTE: If you are using git integration, `wavectl` will not let you push unless you have committed your changes to the repo. This behavior is like a safeguard to ensure that the user is fully aware of what he is writing to Wavefont via `wavectl push`. Asking the user to commit his local changes, serves to ensure that she has inspected the diff and is OK with the modifications.

Lastly, push your local modifications to Wavefront.

``` 
  $ wavectl push --inGit /tmp/GitIntegrationPush/alerts alert
  Replaced alert(s):
  ID               NAME                                                       STATUS    SEVERITY    
  1530723441304    Kubernetes - Node Network Utilization - HIGH (Prod)            WARN    
  1530723441442    Kubernetes - Node Cpu Utilization - HIGH (Prod)                WARN    
  1530723441589    Kubernetes - Node Memory Swap Utilization - HIGH (Prod)        WARN    
  1530723443146    Collections Dev High CPU                                       WARN
```

> NOTE: Even with all the safeguards, if you have made a mistake and pushed to Wavefront, you can roll back the git repo to the previous commit. A command like `git checkout HEAD^` will remove your most recent changes from local files. After that, you can re-execute the push command. That will update all alerts one more time and will set them to the previous state.
