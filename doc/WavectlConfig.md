
<!-- This file is auto generated. Do not edit it. Any modifications will be -->
<!-- overwritten next time documentation is generated. The source for this file -->
<!-- resides in <repo_root>/doc/sphinx directory. Modify there and execute -->
<!-- `make all` in that directory. -->

# Easy configuration of `wavectl`

During execution, `wavectl` needs to talk to a Wavefront server. The address of the Wavefront Server and the necessary tokens for authorization are required for `wavectl` to work.

All applicable wavectl [subcommands](CommandReference.md#subcommand-options) accept a `--wavefrontHost` and a `--apiToken` parameter to discover and authenticate to the Wavefront Server. With these command line parameters, the user needs to speficy the server path and the api token for every command. That may result in too much typing at the command line and the user experience may degrade.

For example:

``` 
  $ wavectl show --wavefrontHost https://acme.wavefront.com --apiToken 98jsb6ef-3939-kk88-8jv2-f84knf71vq68 alert
  ID               NAME                                                                                     STATUS                              SEVERITY    
  1523082347619    Kubernetes - Node Network Utilization - HIGH (Prod)                                      CHECKING                            WARN      
  1523082347824    Kubernetes - Node Cpu Utilization - HIGH (Prod)                                          CHECKING                            WARN      
  1523082348005    Kubernetes - Node Memory Swap Utilization - HIGH (Prod)                                  SNOOZED                             WARN      
  1523082348172    Wavefront Freshness                                                                      CHECKING                            WARN      
  ...
```

To make `wavectl` more usaable we have added a `config` [subcommand](CommandReference.md#config-options). You only need to execute `wavect config` once and speficy your Wavefront host and api token once. `config` command creates an *unencrypted* file at `${HOME}/.wavectl/config` and saves the specified values there. Any other wavectl [subcommand](CommandReference.md#subcommand-options) after a `wavectl config` execution will use the credentials saved in `${HOME}/.wavectl/config` file.

For example:

``` 
  $ printf 'https://acme.wavefront.com \n 98jsb6ef-3939-kk88-8jv2-f84knf71vq68 \n' | wavectl config
  Wavefront host url: Api token: Writing the following config to the config file at /tmp/Users/someuser/.wavectl/config: 
  {
      "apiToken": " 98jsb6ef-3939-kk88-8jv2-f84knf71vq68 ",
      "wavefrontHost": "https://acme.wavefront.com "
  }

  $ wavectl show alert
  ID               NAME                                                                                     STATUS                              SEVERITY    
  1523082347619    Kubernetes - Node Network Utilization - HIGH (Prod)                                      CHECKING                            WARN      
  1523082347824    Kubernetes - Node Cpu Utilization - HIGH (Prod)                                          CHECKING                            WARN      
  1523082348005    Kubernetes - Node Memory Swap Utilization - HIGH (Prod)                                  SNOOZED                             WARN      
  1523082348172    Wavefront Freshness                                                                      CHECKING                            WARN      
  ...
```

The `config` subcommand supports only one set of Wavefront host and api token specification. If your organization has two different Wavefront environments, then you may need to fall back to the `--wavefrontHost` and `--apiToken` command line parameters for the second environment. The command line options take precedence over the values in the `${HOME}/.wavectl/config` file.
