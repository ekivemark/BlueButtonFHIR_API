FROM grahamdumpleton/mod-wsgi-docker:python-3.4-onbuild

CMD [ "--working-directory", “.“, \
      "--url-alias", "/static", “/app/sitestatic”, \
      “--user”, “www-data” “-—group”, “www-data”, \
      ”—application-type”, “module”, “/app/bbapi/apache2/wsgi” ]

# CMD [ "hello.wsgi" ]