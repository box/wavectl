
\# Repetitive editing of alerts, dashboards

At times one needs to change multiple alerts or various queries in several
dashboards at once. A change in a metric name can cause something like this.
For example the metric generator in kubernetes,
\[kube-state-metrics\]\(https://github.com/kubernetes/kube-state-metrics\),
occasionally changes a metric's
[name](https://github.com/kubernetes/kube-state-metrics/commit/aa8aa440de232fabb86af11c79b410d79dc48367#diff-28d2be13094298bdd1fac746cc0d3361R7).

After such a change, the platform owner needs to update all alerts and
dashboards with that metric. Searching for that in the Wavefront GUI and
updating the queries manually can be very labor intensive, error prone and time
consuming. \`wavectl\` can help with automating such a global change.

For the sake of an example, let's say because of an upsteam change, all metrics
that started with \`proc.\` have been renamed to start with \`host.proc.\`.
Once this upstream change gets deployed, numerous alerts and dashboards will be
broken. They will try to display the old metric name and will not show data.
In order to quickly fix this problem via \`wavectl\` we first
\[\`pull\`\]\(CommandReference.md#pull-options\) all alerts and resources that
match the \`proc\\.\` regular expression. The
\[\`--match\`\](CommandReference#resource-options) option can be used to narrow
down the returned set via a regular expression search.


<!-- First delete the temporary directory  -->

```eval_rst
 .. program-output:: rm -rf /tmp/RepetitiveEditing
    :returncode: 0
```

```eval_rst
 .. program-output:: wavectl pull /tmp/RepetitiveEditing/alerts alert --match "proc\."
    :returncode: 0
    :prompt:
```

```eval_rst
 .. program-output:: wavectl pull /tmp/RepetitiveEditing/dashboards dashboard --match "proc\."
    :returncode: 0
    :prompt:
```

See the pulled alerts, dashboards.

```eval_rst
 .. program-output:: find /tmp/RepetitiveEditing -type f
    :returncode: 0
    :prompt:
    :shell:
```

See the usage of the metrics starting with \`proc.\` in pulled alerts, dashboards.

```eval_rst
 .. program-output:: find /tmp/RepetitiveEditing -type f | xargs grep "proc."
    :returncode: 0
    :prompt:
    :shell:
    :ellipsis: 15
```

Then using \[\`sed\`\]\(https://www.gnu.org/software/sed/manual/sed.html\)
replace all occurances of \`proc.\` with \`host.proc.\`


```eval_rst
 .. program-output:: find /tmp/RepetitiveEditing -type f | xargs sed -i -e 's/proc\./host.proc./g'
    :returncode: 0
    :prompt:
    :shell:
```

<!-- TODO: This would be a nice place to introduce git integration -->

Check the changes you have make

```eval_rst
 .. program-output:: find /tmp/RepetitiveEditing -type f | xargs grep "host.proc."
    :returncode: 0
    :prompt:
    :shell:
    :ellipsis: 15
```

Replace the Wavefront alerts and dashboards using
\[\`wavectl push\`\]\(CommandReference.md#push-options\)

```eval_rst
 .. program-output:: wavectl push /tmp/RepetitiveEditing/alerts alert
    :returncode: 0
    :prompt:
```

```eval_rst
 .. program-output:: wavectl push /tmp/RepetitiveEditing/dashboards dashboard
    :returncode: 0
    :prompt:
```

After these steps all your alerts and dashboards in Wavefront will use the
new metric names.

\> NOTE: Doing local modifications via \`sed\` like commands and writing the
resulting files to Wavefront may be risky and dangerous. Some unintended
changes may be written to Wavefront by mistake.  If you want to execute safer
local modifications, where you have a better handle on the resulting diff, take
a look at the \[git integration to push command\]\(GitIntegration.md\) section.

