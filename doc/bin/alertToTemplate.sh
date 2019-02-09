#!/bin/bash

# In this script we modify a json representation of an alert into a jsonnet
# template file.

# Finally we also execute jsonnet to make sure the final file is syntactically
# correct.

set -x
set -e

in_dir=/tmp/Templating/alerts
out_dir=/tmp/Templating/alertTemplates
rm -fr ${out_dir}
mkdir -p ${out_dir}

for in_file in $(ls ${in_dir}/*.alert);
do
    base_name=$(basename -- ${in_file})
    file_name="${base_name%.*}"
    out_file=${out_dir}/${file_name}.jsonnet

    cp -f ${in_file} ${out_file}

    sed -i 's/collections-service-dev/"+std.extVar("namespace")+"/g' ${out_file}
    sed -i 's/Collections Dev/"+std.extVar("namespace")+"/g' ${out_file}
    sed -i 's/"collections-service"/std.extVar("teamTag")/g' ${out_file}
    sed -i 's/"core-frameworks"/std.extVar("parentTeamTag")/g' ${out_file}
    sed -i 's/"pd: .*"/std.extVar("pagerDutyKey")/g' ${out_file}

    jsonnet fmt -i ${out_file}
    jsonnet --ext-str namespace=new-team-namespace \
        --ext-str teamTag=new-team-tag \
        --ext-str parentTeamTag=same-parent-team-tag \
        --ext-str pagerDutyKey=newteampagerdutykey \
        ${out_file}
done

