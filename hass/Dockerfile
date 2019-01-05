FROM homeassistant/raspberrypi3-homeassistant

# Installing this ourselves tbh
RUN pip install jsonrpclib-pelix

WORKDIR /root/
COPY . ./

CMD ["bash", "start.sh"]
