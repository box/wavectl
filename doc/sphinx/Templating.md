
\# Simple templating of alerts, dashboards

Wavefront alerts and dashboards are very powerful tools at developers' hands.
With the ease of monitoring capabilities, programmers can gain great insights
about of all sorts of applications. With that great versatility, we have seen
the alert, dashboard arsenals of our application owners grow organically.

Some teams have re-discovered almost identical best practices. Various
different ways to accomplish the same observation have independently spread in
the organization. For example, we have seen different teams use slightly
different metrics and conditions for their high CPU consumption alerts.
Sometimes we discover a more robust, improved way of building a query. That
knowledge does not spread across teams fast enough to quickly benefit the
entire organization. With these concerns, we thought to add more structure to
our Wavefront state and experimented with templating using \`wavectl.\` In this
document we give a brief introduction how \`wavectl\` can be used for simple,
templating.



