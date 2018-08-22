
\# Simple templating of alerts, dashboards

Wavefront alerts and dashboards are very powerful tools at developers' hands.
With Wavefront's monitoring capabilities, programmers can gain great insights
about of all sorts of applications. With that great versatility, we have seen
the alert and dashboard arsenals of our application owners grow organically in
an ad-hoc way.

Different teams have re-discovered almost identical best practices. Various
different ways of formulating the same query have independently spread in
the organization. For example, we have seen different teams use slightly
different metrics and conditions for their high CPU consumption alerts.
Sometimes we discover a more robust, improved way of building a query. That
knowledge does not spread across teams fast enough to quickly benefit the
entire organization. With these concerns, we thought to add more structure to
our Wavefront state and experimented with templating using \`wavectl.\` In this
document we give a brief introduction how \`wavectl\` can be used for simple
templating.

Templated alerts, dashboards can be very a comprehensive feature and its
implementation could become very complex. At the start with \`wavectl\`, we
kept the templating capabilities limited and simple. Lets go over an example
and later on we discuss the limitations and future work. The following sections
focus on only templated alerts for brevity reasons. The commands and capabilities
easily expand to dashboards too.

\#\# Generate the template files first time.

\#\#\# Choose which alerts to templetize.

Some problematic observations are common in various applications. For example
high cpu, memory... consumption. With containers and
\[Kubernetes\]\(https://kubernetes.io/\) orchestration framework, we get some
more additional common observations like:

\- Too many container restarts.

\- Too many Pod restarts.

\- Too many Pods stuck at an unhealthy state.

\- Pods getting to close to their ResourceQuota usage.

\- ...

In your organization, first, you need to identify some common observations that
would add value to numerous teams. The purpose of an alert templating exercise
should be to simplify and improve many teams' monitoring capabilities. Once you
select a common observation, you may discover distinct Wavefront alerts that
detect the same problem.  They may be implemented differently or may not
maintained similarly. Those would be good candidates for templetizing.


\#\#\# Download json files of alerts from Wavefront.

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
is the right medium for developing new alerts and dashboards. If there is a
need to templetize an alert, an initial version of that alert would have been
implemented via the Wavefront GUI already.

With that observation, the first step to generate the alert templates is to
download the json representation of the alerts from Wavefront.  In this
example, a service called collections-service has some good alerts. We want to
build templates from them so that they can be easily used by other teams too.
The \[\`pull\`\]\(CommandReference.md#pull-options\) command is used to
download the alerts.


<!-- First delete the temporary directory  -->

```eval_rst
 .. program-output:: rm -rf /tmp/Templating
    :returncode: 0
```

```eval_rst
 .. program-output:: wavectl pull /tmp/Templating/alerts alert -t collections-service
    :returncode: 0
    :prompt:
```

After pulling the alerts you can see them in the target directory.

```eval_rst
 .. program-output:: ls /tmp/Templating/alerts
    :returncode: 0
    :prompt:
```

They are in json format:

```eval_rst
 .. program-output:: cat /tmp/Templating/alerts/*
    :returncode: 0
    :shell:
    :prompt:
    :ellipsis: 15
```

\> NOTE: In this example there are a small number of alerts. All the concepts
and commands discussed here easily expand to many more alerts and dashboards.
We kept the data small to have a easy to follow example.

\#\#\# Convert the json files of alerts into a templating languge.

Once we have the json files downloaded, we need to decide on a templating tool.
Since we are working on json files, in this example, we have choosen
\[jsonnet\]\(https://jsonnet.org/\). jsonnet is a very powerful json templating
tool and it is used in various other places in kubernetes community. You could
use your own favorite templating tool chain, the commands will be different but
the main idea stays the same. \[Mustache\]\(https://mustache.github.io/\) or
\[go\]\(https://golang.org/pkg/text/template/\) templates or even
\[sed\]\(https://www.gnu.org/software/sed/\) commands are suitable for this
task.

Converting json files into jsonnet templating language is a one time setup step
for templates. It requires jsonnet lanuage know-how. In this example, the
before and after json -> jsonnet files would looke like this:

```eval_rst
 .. program-output:: alertToTemplate.sh >/dev/null 2>&1
    :returncode: 0
    :shell:
```

\#\#\#\# Alert's json file:

```eval_rst
 .. program-output:: ls /tmp/Templating/alerts/*.alert| head -n 1 | xargs cat
    :returncode: 0
    :shell:
```

\#\#\#\# The corresponding jsonnet template:

We have replaced the hardcoded values for a specific service, with variables
that can be overwritten at template complie time. For example, namespace, tag
and pagerDuty key.

```eval_rst
 .. program-output:: ls /tmp/Templating/alertTemplates/*.jsonnet | head -n 1 | xargs cat
    :returncode: 0
    :shell:
```

Once this transformation is done, you get the template files. They can be reused
to generate Wavefront alerts later on.


\#\# Generate a new set of alerts from templates.


\#\# Future Work.


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




Not everything is automated, some manual command execution is necessary. The users
of the templates need to spend time to build the template, decide on the variables
and best tool to use






