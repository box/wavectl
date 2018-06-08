
\# wavectl

\[!\[CircleCI\]\(https://circleci.com/gh/box/wavectl.svg?style=svg\)\]\(https://circleci.com/gh/box/wavectl\)
\[!\[Project Status\]\(http://opensource.box.com/badges/active.svg\)\]\(http://opensource.box.com/badges\)

A command line client for \[Wavefront\]\(https://www.wavefront.com\) inspired by
\[kubectl\]\(https://kubernetes.io/docs/reference/kubectl/overview/\) and
\[git\]\(https://git-scm.com/docs\) command line tools.


\#\# Example Commands

A short list of common usages. For more details \[Use Cases\]\(#example-use-cases\) section.


\#\#\# Show one line summaries for Wavefront alerts


```eval_rst
 .. program-output:: wavectl show alert
    :prompt:
    :returncode: 0
    :ellipsis: 4
```

\#\#\# Show json state of alerts


```eval_rst
 .. program-output:: wavectl show -o json alert
    :prompt:
    :returncode: 0
    :ellipsis: 19
```



\#\#\# Modify a dashboard's json and write it back to Wavefront



```
   $> vim ./metadata-dashboard.json    # Modify the json state of a dashboard
   $> wavectl push ./metadata-dashboard.json  dashboard  # Write the new version to Wavefront
```

```eval_rst
 .. program-output:: mutateDashboards.py
    :returncode: 0
```


\#\# Example Use Cases

\- \[Command line operations on your alerts, dashboards\]\(doc/CommandLine.md\)

\- \[Advanced grep in your alerts and dashboards\]\(doc/AdvancedGrep.md\)

\- \[Launch Wavefront GUI via \`wavectl\`\]\(doc/BrowserIntegration.md\)

\- \[Repetitive editing of alerts, dashboards\]\(doc/RepetitiveEditing.md\)

\- \[Git integration\]\(doc/GitIntegration.md\)

\- \[Easy configuration of \`wavectl\`\]\(doc/WavectlConfig.md\)


\#\# \[Command Reference\]\(doc/CommandReference.md\)


\#\# Installation

```
    pip install wavectl
```

\#\# A note about Performance

\`wavectl\`'s execution time depends on the number of alerts or dashboards you
have in Wavefront. All
\[resource filtering\]\(doc/CommandReference.md#resource-options\) except the
\`--customerTag, -t\` option is done on the client side. This enables the
powerful regular expression matching on your results. But if your organization
has thousands of alerts and dashboards, the data size may overwhelm the
\`wavectl\` execution time.

If your organization has a lot of alerts and dashboards in Wavefront we
strongly recommend to use \`--customerTag\` option in your commands. The
filtering based on customerTag is done on the Wavefront server side. With
\`--customerTags\` option, wavectl client will only receive data about
alerts/dashboards if they are tagged with all of the specified tags. This
reduces the data size processed by wavectl and results in faster execution.

\#\# Notes

If you could not find what you were looking for please consider
\[contributing\]\(CONTRIBUTING.md\). You could also take a look at
\[another\]\(https://github.com/wavefrontHQ/ruby-client/blob/master/README-cli.md\)
CLI implementation for Wavefront. That one is written by Wavefront and mirrors their
web api more closely. This \`wavectl\` CLI has evolved from our use cases.

\`wavectl\` is designed to add automation, command line access to Wavefront
data that is \*\*human generated\*\*. Initial examples are alerts and
dashboards. We see those as more permanent, slow changing state in Wavefront.
\`wavectl\` is not optimized to read, write time series data to Wavefront or
any other data that is ingested by Wavefront at real time production workload
scale.

\#\# Support

Need to contact us directly? Email oss@box.com and be sure to include the name
of this project in the subject.

\#\# Copyright and License


Copyright 2018 Box, Inc. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

```
   http://www.apache.org/licenses/LICENSE-2.0
```

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
