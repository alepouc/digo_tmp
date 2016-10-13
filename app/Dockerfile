FROM python

WORKDIR /srv/webapp
ADD requirements.txt /srv/webapp/
RUN pip install -r /srv/webapp/requirements.txt

#ADD webapp/ /srv/webapp/
EXPOSE 5000
CMD ["/srv/webapp/digo.py"]
