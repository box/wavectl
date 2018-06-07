
\# Launch Wavefront GUI via \`wavectl\`

Wavefront has an amazing GUI that we all love and use regularly. With its great
performance and design, it significantly enables us to analyze our metrics. As
a command line client to Wavefront, \`wavectl\` cannot replace the powerful GUI
and all the crucial use cases addressed by the GUI. It was imperative for
\`wavectl\` users to be able to switch to Wavefront GUI effortlessly. Because
of that, we have build an \`--in-browser\` option into the
\[\`show\`\]\(CommandReference.md\#show-options\) command. With
\`--in-browser\`, the \`show\` command launches new browser tabs and loads your
selected alerts and dashboards.

For example say you want to investigate your alerts that have the name
"Kubernetes" in them. You could narrow down your shown alerts with the \`--name REGEX\`
command line option. After you list them in the terminal and are convinved of the
selected alerts, you would probably interact with them via the Wavefront GUI.
\`wavectl\` \`show\` can load all selected alerts in a browser tab with the
\`--in-browser\` option. This saves a lot of clicking in the browser and unncessary
copy paste from the command line to the browser.

For example, the following command list all alerts with "Kubernetes" in their name
and will create new browser tabs for each selected one and load the Wavefront page
to that alert.

```eval_rst
 .. program-output:: wavectl show --in-browser alert  --name Kubernetes
    :prompt:
    :returncode: 0
```

Similarly, the following views all Metadata dashboards in Wavefront GUI.

```eval_rst
 .. program-output:: wavectl show --in-browser dashboard  --name Metadata
    :prompt:
    :returncode: 0
```

