
\# Using wavectl with git

One of the advanced features of \`wavectl\` is its git integration. It can be
enabled using the \`--inGit,-g\` parameter to
\[pull\]\(CommandReference.md#pull-options\),
\[push\]\(CommandReference.md#push-options\) and
\[create\]\(CommandReference.md#create-options\) commands.  \`wavectl\` gets
several benefits via git integration that are not immediately obvious. Some
effective use cases are as follows:

\#\# Build a git history of alerts, dashboards with
\[\`pull\`\]\(CommandReference.md#pull-options\)

Wavefront already keeps the change history of
\[alerts\]\(https://docs.wavefront.com/alerts.html#viewing-alerts-and-alert-history\)
and
\[dashboards\]\(https://docs.wavefront.com/dashboards_managing.html#managing-dashboard-versions\).
Those can be accessed via the browser gui. The powerful Wavefront v2 api also
has endpoints to access the histories of
\[alerts\]\(https://github.com/wavefrontHQ/python-client/blob/355698be1b53a32e81348f92549707dbcb4f6413/wavefront_api_client/api/alert_api.py#L428\)
and
\[dashboards\](https://github.com/wavefrontHQ/python-client/blob/355698be1b53a32e81348f92549707dbcb4f6413/wavefront_api_client/api/dashboard_api.py#L523\).
With git integration in  \`wavectl\` we do not add a brand new feature on top
of those. Instead, we attempt to make the retrieval of the histories easier via
the command line mostly using existing mechanisms in git.

Passing \`--inGit\` to \`pull\` command initalizes a git repository in the
pulled directory, if the directory gets created with the \`pull\` command.


<!-- First delete the temporary directory  -->

```eval_rst
 .. program-output:: rm -rf /tmp/GitIntegrationPull
    :returncode: 0
```

```eval_rst
 .. program-output:: wavectl pull --inGit /tmp/GitIntegrationPull/alerts alert
    :returncode: 0
    :prompt:
```

A git repo is created in the newly created /tmp/GitIntegrationPull/alerts directory.


```eval_rst
 .. program-output:: git -C /tmp/GitIntegrationPull/alerts status
    :returncode: 0
    :prompt:
```

Each \`pull\` command creates a new commit with the changes pulled from the
Wavefront server at that time.


```eval_rst
 .. program-output:: git -C /tmp/GitIntegrationPull/alerts log --oneline
    :returncode: 0
    :prompt:
```

If you execute a long running daemon executing periodic pulls from Wavefront, an
extensive git history can be built. The git history will correspond to users'
edits to alerts and dashboards.


      while true; do
         wavectl pull <someDir> alert
         wavectl pull <someDir> dashboard
         sleep 300
      done


Then, later on, if someone is interested understanding the changes to some alerts
or dashboards, the investigation can be done with git show and log commands, which are widely
known by programmers already.

For example:

\#\#\# When was an a particular alert created ?

```eval_rst
 .. program-output:: git -C /tmp/GitIntegrationPull/alerts log $(ls /tmp/GitIntegrationPull/alerts | sort | head -n 1)
    :returncode: 0
    :shell:
    :prompt:
```

\#\#\# When were each alert snoozed ?

```eval_rst
 .. program-output:: git -C /tmp/GitIntegrationPull/alerts log -S snoozed
    :returncode: 0
    :shell:
    :prompt:
```


\> NOTE: The updater id and the actual update time for each alert and dashboard
can be retrieved using the history endpoing in \[Wavefront
API\]\(https://docs.wavefront.com/wavefront_api.html\). However, in
the current \`wavectl\` implementation, the git commit messages
do not contain either of them. In future \`wavectl\` releases we plan to improve
the git integration of pull command to include the updater id and the update time.



\#\# Using \[git-diff\]\(https://git-scm.com/docs/git-diff\) to make safe local
modifications to your alerts, dashboards with
\[\`push\`\]\(CommandReference.md#push-options\)

In the \[repetitive editing doc\]\(RepetitiveEditing.md\) we have
demonstrated an example using the
\[\`sed\`\]\(https://www.gnu.org/software/sed/manual/sed.html\) command to
search and replace strings on local files. After the modifications, the alert,
dashboard json files were written to Wavefront.

It is always good practice to inspect the changes to alerts and dashboards
before writing them back to Wavefront with the
\[\`push\`\]\(CommandReference.md#push-options\) command. The git integration
for the push command can provide a diff of local modifications for the user to
verify.  Since the git integration will work on a local git repo,
\[git-diff\]\(https://git-scm.com/docs/git-diff\) can be used for the diff
generation.

<!-- First delete the temporary directory  -->

```eval_rst
 .. program-output:: rm -rf /tmp/GitIntegrationPush
    :returncode: 0
```

Using the same example from the \[repetitive editing doc\]\(RepetitiveEditing.md\), we
first pull the alerts matching a regular expression. But this time we use the
git integration command line parameter \`--inGit,-g\`

```eval_rst
 .. program-output:: wavectl pull --inGit /tmp/GitIntegrationPush/alerts alert --match "proc\."
    :returncode: 0
    :prompt:
```

Then the local modifications are executed:

```eval_rst
 .. program-output:: find /tmp/GitIntegrationPush -type f | xargs sed -i -e 's/proc\./host.proc./g'
    :returncode: 0
    :prompt:
    :shell:
```

See the modifications to alerts that are going to be pushed to Wavefront:

```eval_rst
 .. program-output:: git -C /tmp/GitIntegrationPush/alerts diff HEAD
    :returncode: 0
    :prompt:
    :ellipsis: 32
```

Submit your changes to the local repo:

```eval_rst
 .. program-output:: git -C /tmp/GitIntegrationPush/alerts commit -a -m "proc. is replaced with host.proc."
    :returncode: 0
    :shell:
    :prompt:
```

\> NOTE: If you are using git integration, \`wavectl\` will not let you push
unless you have committed your changes to the repo. This behavior is like a
safeguard to ensure that the user is fully aware of what he is writing to
Wavefont via \`wavectl push\`. Asking the user to commit his local changes,
serves to ensure that she has inspected the diff and is OK with the
modifications.


Lastly, push your local modifications to Wavefront.

```eval_rst
 .. program-output:: wavectl push --inGit /tmp/GitIntegrationPush/alerts alert
    :returncode: 0
    :prompt:
```


\> NOTE: Even with all the safeguards, if you have made a mistake and pushed to
Wavefront, you can roll back the git repo to the previous commit.  A command
like \`git checkout HEAD^\` will remove your most recent changes from local
files. After that, you can re-execute the push command. That will update all
alerts one more time and will set them to the previous state.


