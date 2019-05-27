FROM linuxserver/plex:arm32v7-latest

RUN \
 echo "**** install ntfs-3g packages ****" && \
 apt-get update && \
 apt-get install -y \
    ntfs-3g && \
 echo "**** cleanup ****" && \
 apt-get clean && \
 rm -rf \
    /etc/default/plexmediaserver \
    /tmp/* \
    /var/lib/apt/lists/* \
    /var/tmp/*


RUN echo "LABEL=SG1 /data/media ntfs-3g rw,user,auto,async 0 2" >> /etc/fstab
RUN echo "LABEL=SG2 /data/backups ntfs-3g rw,user,auto,aysnc 0 2" >> /etc/fstab

COPY ./start.sh ./start.sh

CMD ["bash", "start.sh"]
