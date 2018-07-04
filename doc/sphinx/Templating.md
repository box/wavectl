
\# Simple templating of alerts, dashboards

Wavefront alerts and dashboards are very powerful tools at developers' hands.
With Wavefront's monitoring capabilities, programmers can gain great insights
about of all sorts of applications. With that great versatility, we have seen
the alert and dashboard arsenals of our application owners grow organically in
an ad-hoc way.

Different teams have re-discovered almost identical best practices. Various
different ways to formuate the same query have independently spread in
the organization. For example, we have seen different teams use slightly
different metrics and conditions for their high CPU consumption alerts.
Sometimes we discover a more robust, improved way of building a query. That
knowledge does not spread across teams fast enough to quickly benefit the
entire organization. With these concerns, we thought to add more structure to
our Wavefront state and experimented with templating using \`wavectl.\` In this
document we give a brief introduction how \`wavectl\` can be used for simple,
templating.

Templated alerts, dashboards can be very a comprehensive feature and its
implementation could become very complex. At the start with \`wavectl\`, we
kept the templating capabilities limited and simple. Lets go over an example
and later on we discuss the limitations and future work. The following sections
focus on only templated alerts for brevity reasons. The commands and capabilities
easily expand to dashboards too.

\#\# Generate the template files first time.

Wavefront GUI has really powerful user experience.

\- \[Charts\]\(https://docs.wavefront.com/charts.html\) react instantly to
changing queries.

\- Alerts have a
\[backtesting\]\(https://docs.wavefront.com/alerts.html#backtesting\) mode
helping to avoid false positives and negatives.

\- Autocomplete
\[dropdown\]\(https://docs.wavefront.com/metrics_managing.html\) menus for
metric name completion.

Because of these and many other features, we strongly believe the Wavefront GUI
is the right medium for developing new alerts and dashboards. If there is a need to
templetize an alert, that alert would have been implemented via the Wavefront GUI
already.

With that observation, the first step to generate the alert templates is to
download the json representation of the alerts from Wavefront. The
\[\`pull\`\]\(CommandReference.md#pull-options\) command accomplishes that.


<!-- First delete the temporary directory  -->

```eval_rst
 .. program-output:: rm -rf /tmp/Templating
    :returncode: 0
```

```eval_rst
 .. program-output:: wavectl pull /tmp/Templating/alerts alert
    :returncode: 0
    :prompt:
```

```eval_rst
 .. program-output:: ls /tmp/Templating/alerts
    :returncode: 0
    :prompt:
```

```eval_rst
 .. program-output:: cat /tmp/Templating/alerts/*
    :returncode: 0
    :shell:
    :prompt:
    :ellipsis: 15
```

<!-- TODO: Add more templatable alerts to the TestAlert.json. So that this example -->
<!-- actually makes sense to the user. Use collections service alets. -->

Once we have the json files downloaded, we need to decide on a templating tool.
Since we are working on json files, in this example, we have choosen
\[jsonnet\]\(https://jsonnet.org/\). jsonnet is a very powerful json templating
tool and it is used in various other places in kubernetes community. You could
use your own favorite templating tool chain, the commands will be different but
the main idea stays the same. \[Mustache\]\(https://mustache.github.io/\) or
\[go\]\(https://golang.org/pkg/text/template/\) templates or even
\[sed\]\(https://www.gnu.org/software/sed/\) commands are suitable for this
task.



////////////////////////////

NOTES:

\1. Wavefront alerts, dashboards may deviate from templates if users modify them in GUI.
   \1. There is no automated process that will continuously equate the templates
   with the state in Wavefront.
\2. Template generation can be manual. The programmers are free to use any templating
language or tooling to convert the json files into templates. We have tried jsonnet,
python mustashe template solutions. Some other teammembers have also wrote simple
sed commands to convert into templates.
\3. Wavectl is quite opinioted about the file extensions and file names. One may
prefer to use the alert name itself as the name of the template. Doing that
requires manual work.
\4. In order to change a threshold, the team needs to re-generate the whole
templated alerts and write them back to dashboard.
\5. Once a team creates their alerts from a template they need to execute create.


ar

Not everything is automated, some manual command execution is necessary. The users
of the templates need to spend time to build the template, decide on the variables
and best tool to use


may need to and the implementation may
need to consider various use cases like:





