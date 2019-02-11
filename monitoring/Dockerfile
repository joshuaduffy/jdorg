FROM grafana/grafana:5.4.2

ADD ./provisioning /etc/grafana/provisioning
ADD ./dashboards /var/lib/grafana/dashboards
ADD ./grafana.ini /etc/grafana/grafana.ini
ADD ./credentials /usr/share/grafana/.aws/credentials