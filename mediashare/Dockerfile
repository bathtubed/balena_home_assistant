FROM balenalib/raspberrypi3-debian

RUN \
 echo "**** install packages ****" && \
 apt-get update && \
 apt-get install -y \
    ntfs-3g minidlna samba && \
 echo "**** cleanup ****" && \
 apt-get clean && \
 rm -rf \
    /etc/default/plexmediaserver \
    /tmp/* \
    /var/lib/apt/lists/* \
    /var/tmp/*

RUN echo "LABEL=SG1 /data/media ntfs-3g rw,user,auto,async 0 2" >> /etc/fstab
RUN echo "LABEL=SG2 /data/backups ntfs-3g rw,user,auto,aysnc 0 2" >> /etc/fstab

COPY minidlna.conf /etc/minidlna.conf

COPY ./samba.conf ./samba.conf
RUN cat samba.conf >> /etc/samba/smb.conf

COPY ./start.sh ./start.sh

CMD ["bash", "start.sh"]
