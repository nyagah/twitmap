import tweepy
import json
import requests
import pprint

api_key = ''
api_secret = ''
access_token = ''
access_token_secret = ''

class Listener(tweepy.StreamListener):

    def __init__(self, output):
        self.output = output
        self.counter = 0
        self.url = 'http://twitmap-heatmap.appspot.com/post'
        self.headers = {'Content-Type': 'application/json'}

    def on_data(self, data):
        if  'in_reply_to_status' in data:
            if self.on_status(data) is False:
                return False
        elif 'delete' in data:
            print 'delete'
            return
        elif 'limit' in data:
            print 'limit'
            return
        elif 'warning' in data:
            warning = json.loads(data)['warnings']
            print warning['message']
            return


    def on_status(self, status):
        data = json.loads(status)
        if data['coordinates'] and data['entities']['hashtags']:
            self.output.write(status)
            r = requests.post(self.url, data=status, headers=self.headers)
            print r.status_code
            
            self.counter += 1

            if self.counter > 9:
                return False
            
            #if self.counter > 5:
            #    self.output.write('"tweet' + str(self.counter) + '":' + status.strip())
            #    return False
            #else:
            #    self.output.write('"tweet' + str(self.counter) + '":' + status.strip() + ',')            
            #
            #self.counter += 1

    def on_error(self, status):
        print 'Encountered error: ', status

    def on_timeout(self):
        print 'Timeout...'


def main():

    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)

    output = open('tweets.json', 'w')

    listener = Listener(output)

    stream = tweepy.Stream(auth, listener, timeout=10)
    stream.sample()

    output.close()

    #pprint.pprint(json.load(output))

    #output = open('tweet.json', 'w')
    #output.write('{')
    #
    #listener = Listener(output)
    #
    #stream = tweepy.Stream(auth, listener, timeout=10)
    #stream.sample()
    #
    #output.write('}')
    #output.close();


if __name__ == '__main__':
    main()

