# Credits @NaytSeyd
FROM *DarK* 

# Maintainer
Ahmet Tokka <ahtosial@gmail.com>

# Zaman dilimini ayarla
ENV TZ=Europe/Istanbul

# Çalışma dizini
ENV PATH="/root/darkuser/bin:$PATH"
WORKDIR /root/darkuser

# Repoyu klonla
RUN git clone -b dark https://github.com/qkoer/darkuserbot /root/darkuser

# Oturum ve yapılandırmayı kopyala (varsa)
COPY ./sample_config.env ./dark.session* ./config.env* /root/darkuser/

# Botu çalıştır
CMD ["python3","dark.py"]
