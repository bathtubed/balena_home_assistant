FROM homeassistant/raspberrypi3-homeassistant

# Installing this ourselves tbh
RUN pip install jsonrpclib-pelix

WORKDIR /root/
COPY . ./

RUN echo "*/5 *  * * *   root    /root/check_wifi.sh" >> /etc/crontab

CMD ["bash", "start.sh"]
