
\# Command line operations on your alerts, dashboards

In this document we describe general tasks using the command line that you can
accomplish with \`wavectl\` using your alerts and dashboards.

Many of these examples can be accomplished by using the Wavefront gui too.
\`wavectl\` enables accomplishing these tasks in a command line interface and in
conjunction with powerful tools like \`grep\`, \`awk\`, \`sed\`,
\[\`jq\`\]\(https://stedolan.github.io/jq/\), or similar


\#\# Print one line summaries of your alerts, dashboards.

\`wavectl\` can be used to list all alerts in a one line summary form.

For example:


```eval_rst
 .. program-output:: wavectl show alert
    :prompt:
    :ellipsis: 5
    :returncode: 0
```

The short summary form contains the \[alert
state\]\(https://docs.wavefront.com/alerts_states_lifecycle.html#alert-states\)
and the severity in addition to the name and unique id of the alert. Once you have a
structured columned print of your alerts, you can do all sorts of processing with them.

For example:

\#\#\# Find the alerts firing right now.

```eval_rst
 .. program-output:: wavectl show alert | grep FIRING
    :prompt:
    :shell:
    :returncode: 0
```

This could be used from a script too. For example, an operator may want to ensure
no alerts from "kubernetes" are firing before executing a script that is going to
downtime one of the kubernetes control plane hosts.

\#\#\# Count the total number of alerts in your organization.

```eval_rst
 .. program-output:: wavectl show --no-header alert | wc -l
    :prompt:
    :shell:
    :returncode: 0
```


\#\# Inspect all attributes of alerts, dashboards.

In addition to printing one line summaries the \`show\` command can also print
detailed state of your alerts in json form:

```eval_rst
 .. program-output:: wavectl show -o json alert
    :prompt:
    :returncode: 0
    :ellipsis: 19
```

One you have an easy way to retrieve the json representation of alerts, dashboards,
this can lead to various powerful use cases with using text processing tools like
\[\`jq\`\]\(https://stedolan.github.io/jq/\) or grep. For example:

\#\#\# Print the name and the
\[condition\]\(https://docs.wavefront.com/alerts_states_lifecycle.html#alert-conditions\) for
each alert.

```eval_rst
 .. program-output:: wavectl show -o json alert | jq '{name,condition}'
    :prompt:
    :shell:
    :returncode: 0
    :ellipsis: 11
```


\#\#\# See the existing usages of a particular metric.

You may want to see a metric's usages in all dashboard queries. You may be
unsure about the semantics of a metric and seeing its correct usages definitely
helps.

Dashboards' json state can be inspected similarly to alerts. Seeing all dashboard
queries regarding haproxy backends:

```eval_rst
 .. program-output:: wavectl show -o json dashboard | grep haproxy_backend
    :prompt:
    :shell:
    :returncode: 0
```

\#\#\# See existing usages of advanced Wavefront functions.

Some advanced functions in \[Wavefront query
language\]\(https://docs.wavefront.com/query_language_reference.html\) are not
the easiest to learn. It is always helpful to see existing
usages of a Wavefront function by your colleagues before writing your own. Take
the \[taggify\]\(https://docs.wavefront.com/ts_taggify.html\) as an example.

```eval_rst
 .. program-output:: wavectl show -o json dashboard | grep taggify
    :prompt:
    :shell:
    :returncode: 0
```

\> After textually inspecting the alert, dashboard state you may want to jump to
the Wavefront gui and see the time series there. For that you can use the wavectl
\[browser integration\]\(BrowserIntegration.md\).


\#\#\# See all sections in all your dashboards.


```eval_rst
 .. program-output:: wavectl show -o json dashboard | jq '{name: .name, sections: [.sections[].name]}'
    :prompt:
    :shell:
    :returncode: 0
    :ellipsis: 19
```


