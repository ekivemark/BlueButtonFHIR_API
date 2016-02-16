def application(environ, start_response):

    import os

    print("BBAPI Hello World!")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bbapi.settings")

    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()

    # status = '200 OK'
    # output = b'Hello World! This proves that the WSGI interface in a Docker container works.'

    # response_headers = [('Content-type', 'text/plain'),
    #                     ('Content-Length', str(len(output)))]
    # start_response(status, response_headers)

    # return [output]