from google.appengine.ext import webapp
import logging, datetime

def remove_www(handler):
    if handler.request.url.startswith('http://www.'):
        handler.redirect(handler.request.url.replace('http://www.', 'http://'))

def makeStatic(template_name, context={}):
    class Static(webapp.RequestHandler):
        def get(self):
            remove_www(self)
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(
                render(template_name, context)
            )
    return Static

import re
# Allow 'abc' and 'abc.def' but not '.abc' or 'abc.'
valid_callback = re.compile('^\w+(\.\w+)*$')

import pytz

class JsonTime(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/javascript'
        callback = self.request.get('callback', default_value='')
        tz = self.request.get('tz', default_value = 'UTC')
        try:
            timezone = pytz.timezone(tz)
            json = (
                "{'datetime': '%s', 'tz': '%s', 'error': false}" % (
                    datetime.datetime.utcnow().replace(
                        tzinfo = pytz.utc
                    ).astimezone(timezone).strftime(
                        '%a, %d %b %Y %H:%M:%S %z'
                    ),
                    timezone.zone
                )
            )
        except pytz.UnknownTimeZoneError:
            json = "{'error': 'Unknown Timezone'}"
        
        if callback and valid_callback.match(callback):
            json = '%s(%s)' % (callback, json)
        self.response.out.write(json)

class Http404Page(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.error(404)
        self.response.out.write(render('404.html', {
            'path': self.request.path,
        }))

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    from wsgiref.handlers import CGIHandler
    application = webapp.WSGIApplication([
        ('/', makeStatic('index.html')),
        ('/time.json', JsonTime),
        ('/.*$', Http404Page),
    ], debug=True)
    CGIHandler().run(application)

import os
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
from google.appengine.ext.webapp import template
def render(template_name, context={}):
    path = os.path.join(template_dir, template_name)
    return template.render(path, context)

if __name__ == "__main__":
    main()
