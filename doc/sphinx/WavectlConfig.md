
\# Easy configuration of \`wavectl\`

During execution, \`wavectl\` needs to talk to a Wavefront server. The address of
the Wavefront Server and the necessary tokens for authorization are required
for \`wavectl\` to work.

All applicable wavectl
\[subcommands\]\(CommandReference.md#subcommand-options\) accept a
\`--wavefrontHost\` and a \`--apiToken\` parameter to discover and authenticate
to the Wavefront Server. With these command line parameters, the user needs to
speficy the server path and the api token for every command. That may result in
too much typing at the command line and the user experience may degrade.

For example:

```eval_rst
 .. program-output:: wavectl show --wavefrontHost https://acme.wavefront.com --apiToken 98jsb6ef-3939-kk88-8jv2-f84knf71vq68 alert
    :prompt:
    :ellipsis: 5
    :returncode: 0
```

To make \`wavectl\` more usaable we have added a \`config\`
\[subcommand\]\(CommandReference.md#config-options\). You only need to execute
\`wavect config\` once and speficy your Wavefront host and api token once. \`config\`
command creates an \*unencrypted\* file at \`${HOME}/.wavectl/config\` and saves the
specified values there. Any other wavectl
\[subcommand\]\(CommandReference.md#subcommand-options\) after a  \`wavectl config\`
execution will use the credentials saved in \`${HOME}/.wavectl/config\` file.

For example:

```eval_rst
 .. program-output:: printf 'https://acme.wavefront.com \n 98jsb6ef-3939-kk88-8jv2-f84knf71vq68 \n' | wavectl config
    :prompt:
    :shell:
    :returncode: 0
```

```eval_rst
 .. program-output:: wavectl show alert
    :prompt:
    :ellipsis: 5
    :returncode: 0
```

The \`config\` subcommand supports only one set of Wavefront host and api token
specification. If your organization has two different Wavefront environments,
then you may need to fall back to the \`--wavefrontHost\` and \`--apiToken\`
command line parameters for the second environment. The command line options
take precedence over the values in the \`${HOME}/.wavectl/config\` file.


