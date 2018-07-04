
\# Advanced grep in your alerts and dashboards.

\`wavectl\` allows users to execute regular expression searches on
alerts and dashboards. Using the
\[resource options\]\(CommandReference.md#resource-options\), the user can specify
fields and a regular expression to match for each field. \`wavectl\` will
process only resources that satisfy all specified regular expressions.
For \`show\` command, only the matched alerts/dashboards will be displayed, for
\`push\` only the matching ones will be written to Wavefront, and so on.


<!-- First setup the fake home dir and config file  -->

```eval_rst
 .. program-output:: printf 'https://acme.wavefront.com \n 98jsb6ef-3939-kk88-8jv2-f84knf71vq68 \n' | wavectl config > /dev/null
    :shell:
    :returncode: 0
```

For example: show alerts that have "Kubernetes" and "Utilization" in their names:

```eval_rst
 .. program-output:: wavectl show alert --name "Kubernetes.*Utilization"
    :prompt:
    :returncode: 0
```

The \`--match\` parameter can be used to search anywhere in the json representation
of an alert or a dashboard rather than in known key value pairs.

For example: Show the dashboards that use metrics from the live environment

```eval_rst
 .. program-output:: wavectl show dashboard --match "env=live"
    :prompt:
    :returncode: 0
```

Write alerts back to Wavefront that have a specific person in the \`updaterId\`


<!-- First delete the temporary directory  -->

```eval_rst
 .. program-output:: rm -rf /tmp/AdvancedGrep/dashboards
    :returncode: 0
```

<!-- Pull the alerts in the tmp directory  -->

```eval_rst
 .. program-output:: wavectl pull /tmp/AdvancedGrep/dashboards dashboard
    :returncode: 0
    :shell:
```

```eval_rst
 .. program-output:: wavectl push /tmp/AdvancedGrep/dashboards dashboard --updaterId hbaba
    :returncode: 0
    :prompt:
    :ellipsis: 8
```


\`wavectl\` uses python standard library's regular expression
\[module\]\(https://docs.python.org/3.4/library/re.html\). Any valid python
regular expression can be specified for the \[resource
options\]\(CommandReference.md#resource-options\).
