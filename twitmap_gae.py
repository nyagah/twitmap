import os
import urllib
import json
from random import randint

from google.appengine.api import memcache
from google.appengine.ext import ndb


import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Tweet(ndb.Model):
    keywords = ndb.StringProperty()
    lat = ndb.StringProperty()
    long = ndb.StringProperty()


class MainPage(webapp2.RequestHandler):

    def get(self):
        
        tweets = []
        toptweets = []
        keyword = self.request.get("keyword", "")
        
        if keyword == "":
            tweets = Tweet.query().fetch()
            start_offset = randint(0, len(tweets) - 7)
            toptweets = tweets[start_offset:start_offset + 6]
        else:
            tweets = memcache.get('%s' % keyword)

            if tweets is not None:
                toptweets = Tweet.query().fetch()
                start_offset = randint(0, len(toptweets) - 7)
                toptweets = toptweets[start_offset:start_offset + 6]
            else:
                tweets = Tweet.query(Tweet.keywords == keyword).fetch()
                memcache.add('%s' % tweets[0].keywords, tweets, 3600)

                toptweets = Tweet.query().fetch()
                start_offset = randint(0, len(toptweets) - 7)
                toptweets = toptweets[start_offset:start_offset + 6]
            

        template_values = {
            'tweets': tweets,
            'toptweets': toptweets,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class Tweetbook(webapp2.RequestHandler):

    def post(self):
        tweetin = json.loads((self.request.body))

        for hashtag in tweetin['entities']['hashtags']:
            tweet = Tweet()
            tweet.keywords = hashtag['text']
            tweet.lat = str(tweetin['coordinates']['coordinates'][1])
            tweet.long = str(tweetin['coordinates']['coordinates'][0])
            tweet.put()

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/post', Tweetbook),
], debug=True)
