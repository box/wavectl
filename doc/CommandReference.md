
<!-- This file is auto generated. Do not edit it. Any modifications will be -->
<!-- overwritten next time documentation is generated. The source for this file -->
<!-- resides in <repo_root>/doc/sphinx directory. Modify there and execute -->
<!-- `make all` in that directory. -->

# wavectl command reference

## Global Options

``` 
  usage: wavectl [-h] [--log {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                 {config,show,pull,push,create} ...

  A command line tool to programmatically interact with wavefront

  optional arguments:
    -h, --help            show this help message and exit
    --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                          Set the logging level for the command

  subcommands:
    Choose a subcommand to execute

    {config,show,pull,push,create}
      config              Set wavefront host, api token.
      show                show prints Wavefront rsrcs in various formats
      pull                pull resrouces from wavefront api server and save them
                          in a local directory in json format
      push                push resource files from the given target to Wavefront
      create              create new resources in Wavefront using target
```

## Subcommand Options

### Config Options

``` 
  usage: wavectl config [-h]

  optional arguments:
    -h, --help  show this help message and exit
```

### Show Options

``` 
  usage: wavectl show [-h] [--output {summary,json}] [--color {auto,never}]
                      [--in-browser] [--no-header]
                      [--wavefrontHost WAVEFRONTHOST] [--apiToken APITOKEN]
                      {alert,dashboard} ...

  optional arguments:
    -h, --help            show this help message and exit
    --output {summary,json}, -o {summary,json}
                          Output fromat. summary output is default where one
                          line is printed for each resource. Json prints out the
                          full state of each resource in json form.
    --color {auto,never}, -l {auto,never}
                          Enable/Disable colored output in the summary table. If
                          set to auto the output will be colored if the terminal
                          supports it. If set to never, ouput will not be
                          colored
    --in-browser, -b      Open the selected resources in the default browser in
                          new tabs. At most 10 new tabs are supported. If the
                          selected number of resources are more than 10, an
                          exception is thrown. The supported max can be changed
                          by setting the MAX_BROWSER_TABS env var
    --no-header           If set, the show command does not print the table
                          header in summary mode
    --wavefrontHost WAVEFRONTHOST
                          Speficy the url of the wavefront host. If specified,
                          this takes precedence over the config file entry.
    --apiToken APITOKEN   Speficy the api token to use while communicating with
                          the wavefront host. If specified, this takes
                          precedence over the config file entry.

  resourceType:
    Select the resource type to operate on

    {alert,dashboard}
      alert               Specify to use alert resources
      dashboard           Specify to use dashboard resources
```

### Pull Options

``` 
  usage: wavectl pull [-h] [--merge-into-branch {master,None}] [--inGit]
                      [--wavefrontHost WAVEFRONTHOST] [--apiToken APITOKEN]
                      dir {alert,dashboard} ...

  positional arguments:
    dir                   Wavefront resource data will be saved in this
                          directory

  optional arguments:
    -h, --help            show this help message and exit
    --merge-into-branch {master,None}, -b {master,None}
                          The name of the branch to merge into. By default it is
                          the master branch. If an None is passed, no merge is
                          processed. The pulled changes remain in the pull
                          branch only. Right now only master and None are
                          supported as parameters
    --inGit, -g           The given directory is source controlled with git. In
                          this case the pull and push commands make use of git
                          branches, do extra checks for modified files and
                          detect conflicting remote-local changes.
    --wavefrontHost WAVEFRONTHOST
                          Speficy the url of the wavefront host. If specified,
                          this takes precedence over the config file entry.
    --apiToken APITOKEN   Speficy the api token to use while communicating with
                          the wavefront host. If specified, this takes
                          precedence over the config file entry.

  resourceType:
    Select the resource type to operate on

    {alert,dashboard}
      alert               Specify to use alert resources
      dashboard           Specify to use dashboard resources
```

### Push Options

``` 
  usage: wavectl push [-h] [--inGit] [--quiet] [--wavefrontHost WAVEFRONTHOST]
                      [--apiToken APITOKEN]
                      target {alert,dashboard} ...

  positional arguments:
    target                Wavefront resource data from this target will be
                          written to the wavefront server. target can be a path
                          to a directory or a file. For directories all resource
                          files in that directory will be considered. For files,
                          on the that file is considered for a push

  optional arguments:
    -h, --help            show this help message and exit
    --inGit, -g           The given directory is source controlled with git. In
                          this case the pull and push commands make use of git
                          branches, do extra checks for modified files and
                          detect conflicting remote-local changes.
    --quiet, -q           Supress printed output about mutated resrouces.
    --wavefrontHost WAVEFRONTHOST
                          Speficy the url of the wavefront host. If specified,
                          this takes precedence over the config file entry.
    --apiToken APITOKEN   Speficy the api token to use while communicating with
                          the wavefront host. If specified, this takes
                          precedence over the config file entry.

  resourceType:
    Select the resource type to operate on

    {alert,dashboard}
      alert               Specify to use alert resources
      dashboard           Specify to use dashboard resources
```

### Create Options

``` 
  usage: wavectl create [-h] [--inGit] [--quiet] [--wavefrontHost WAVEFRONTHOST]
                        [--apiToken APITOKEN]
                        target {alert,dashboard} ...

  positional arguments:
    target                Wavefront resource data from this target will be
                          written to the wavefront server. target can be a path
                          to a directory or a file. For directories all resource
                          files in that directory will be considered. For files,
                          on the that file is considered for a push

  optional arguments:
    -h, --help            show this help message and exit
    --inGit, -g           The given directory is source controlled with git. In
                          this case the pull and push commands make use of git
                          branches, do extra checks for modified files and
                          detect conflicting remote-local changes.
    --quiet, -q           Supress printed output about mutated resrouces.
    --wavefrontHost WAVEFRONTHOST
                          Speficy the url of the wavefront host. If specified,
                          this takes precedence over the config file entry.
    --apiToken APITOKEN   Speficy the api token to use while communicating with
                          the wavefront host. If specified, this takes
                          precedence over the config file entry.

  resourceType:
    Select the resource type to operate on

    {alert,dashboard}
      alert               Specify to use alert resources
      dashboard           Specify to use dashboard resources
```

## Resource Options

### For Alerts

``` 
  usage: wavectl push target alert [-h] [--customerTag CUSTOMERTAG]
                                   [--match REGEX] [--status REGEX]
                                   [--name REGEX]
                                   [--additionalInformation REGEX]
                                   [--displayExpression REGEX] [--id REGEX]
                                   [--condition REGEX] [--severity REGEX]

  optional arguments:
    -h, --help            show this help message and exit
    --customerTag CUSTOMERTAG, -t CUSTOMERTAG
                          Narrow down the matching resources by their tags.
                          Multiple customer tags can be passed. Resources that
                          contain all tags will be returned.
    --match REGEX, -m REGEX
                          specify a regular expression to further narrow down on
                          matches in any field in the resource. If this regex
                          mathes in the resource's representation, then the
                          resource will be included in the processing
    --status REGEX, -a REGEX
                          specify a regular expression to further narrow down on
                          matches in the status field in a alert
    --name REGEX, -n REGEX
                          specify a regular expression to further narrow down on
                          matches in the name field in a alert
    --additionalInformation REGEX, -f REGEX
                          specify a regular expression to further narrow down on
                          matches in the additionalInformation field in a alert
    --displayExpression REGEX, -x REGEX
                          specify a regular expression to further narrow down on
                          matches in the displayExpression field in a alert
    --id REGEX, -i REGEX  specify a regular expression to further narrow down on
                          matches in the id field in a alert
    --condition REGEX, -d REGEX
                          specify a regular expression to further narrow down on
                          matches in the condition field in a alert
    --severity REGEX, -e REGEX
                          specify a regular expression to further narrow down on
                          matches in the severity field in a alert
```

### For Dashboards

``` 
  usage: wavectl push target dashboard [-h] [--customerTag CUSTOMERTAG]
                                       [--match REGEX] [--updaterId REGEX]
                                       [--description REGEX] [--id REGEX]
                                       [--name REGEX]

  optional arguments:
    -h, --help            show this help message and exit
    --customerTag CUSTOMERTAG, -t CUSTOMERTAG
                          Narrow down the matching resources by their tags.
                          Multiple customer tags can be passed. Resources that
                          contain all tags will be returned.
    --match REGEX, -m REGEX
                          specify a regular expression to further narrow down on
                          matches in any field in the resource. If this regex
                          mathes in the resource's representation, then the
                          resource will be included in the processing
    --updaterId REGEX, -s REGEX
                          specify a regular expression to further narrow down on
                          matches in the updaterId field in a dashboard
    --description REGEX, -d REGEX
                          specify a regular expression to further narrow down on
                          matches in the description field in a dashboard
    --id REGEX, -i REGEX  specify a regular expression to further narrow down on
                          matches in the id field in a dashboard
    --name REGEX, -n REGEX
                          specify a regular expression to further narrow down on
                          matches in the name field in a dashboard
```
