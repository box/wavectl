#!/usr/bin/env python

import argparse
import wavefront_api_client
import json


def main():

    alert, dashboard = ["alert", "dashboard"]

    parser = argparse.ArgumentParser(
        description="""A tool to create test fixtures using the latest version of
        the wavefront server. In wavectl tests, we have local representations
        of the json data that is returned by the wavefront api server. Depending
        on the server version and the api version, this data may change over time.
        With this script one could update the locally saves json test fixtures.""")
    parser.add_argument("wavefrontHost",
                        help="""Speficy the url of the wavefront host.""")
    parser.add_argument("apiToken", help="""Speficy the api token to use while
        communicating with the wavefront host.""")
    parser.add_argument(
        "rsrcType",
        choices=[
            alert,
            dashboard],
        help="Specify the resource kind represented in the file")
    parser.add_argument("inFile", help="Input File")
    parser.add_argument("outFile", help="Out File")

    args = parser.parse_args()

    config = wavefront_api_client.Configuration()
    config.host = args.wavefrontHost
    wavefrontClient = wavefront_api_client.ApiClient(
        configuration=config,
        header_name="Authorization",
        header_value="Bearer " + args.apiToken)

    alertApi = wavefront_api_client.AlertApi(wavefrontClient)
    dashboardApi = wavefront_api_client.DashboardApi(wavefrontClient)
    searchApi = wavefront_api_client.SearchApi(wavefrontClient)

    with open(args.inFile) as f:
        inRsrcs = json.load(f)

    uKey = "id"
    if args.rsrcType == alert:
        api = alertApi
        createFunc = api.create_alert
        searchFunc = searchApi.search_alert_entities
        delFunc = api.delete_alert
    elif args.rsrcType == dashboard:
        api = dashboardApi
        createFunc = api.create_dashboard
        searchFunc = searchApi.search_dashboard_entities
        delFunc = api.delete_dashboard
    else:
        assert not "Unexpected value in rsrcType parameter"

    outRsrcs = []
    for r in inRsrcs:
        createFuncParams = {"body": r}
        rawRes = createFunc(_preload_content=False, **createFuncParams)
        strRes = rawRes.read().decode('utf-8')
        res = json.loads(strRes)["response"]
        outRsrcs.append(res)

    with open(args.outFile, "w") as f:
        json.dump(
            outRsrcs,
            f,
            indent=4,
            sort_keys=True,
            separators=(
                ',',
                ': '))

    # Permanently delete every rsrc
    for r in outRsrcs:
        uId = r[uKey]
        delFunc(uId, _preload_content=False)
        delFunc(uId, _preload_content=False)


if __name__ == "__main__":
    main()
