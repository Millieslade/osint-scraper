"""Data gathering module."""
from __future__ import print_function

import json

import os

from urllib.request import urlopen

from bs4 import BeautifulSoup

from github import GitHub

import pypwned

import requests

import tweepy


def twitter_recon(username):
    """Use tweepy to access user data if name found."""
    twitter_con_key = os.environ.get('TWITTER_CON_KEY')
    twitter_con_secret = os.environ.get('TWITTER_CON_SECRET')
    twitter_token = os.environ.get('TWITTER_TOKEN')
    twitter_token_secret = os.environ.get('TWITTER_TOKEN_SECRET')
    auth = tweepy.OAuthHandler(twitter_con_key, twitter_con_secret)
    auth.set_access_token(twitter_token, twitter_token_secret)

    api = tweepy.API(auth)
    try:
        user = api.get_user(username)
    except:
        return None
    return user._json


def pwned_recon(email):
    """Check HIBP if email has been compromised."""
    results = pypwned.getAllBreachesForAccount(email=email)
    return results


def github_recon(user_name):
    """Github scraper."""
    gh = GitHub()
    try:
        ghuser = gh.users(user_name).get()
    except:
        return None
    return ghuser


def facebook_recon(email):
    """Find facebook account if linked via email."""
    try:
        r = requests.get('https://www.facebook.com/search/people?q={}'
                         .format(email))
        return r.url
    except:
        r = None


def photobucket_recon(user_name):
    """Check for pb account with user_name."""
    r = requests.get('http://s594.photobucket.com/user/{}/profile/'
                     .format(user_name))
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "lxml")
        return soup.find('input', 'linkcopy').attrs['value']
    else:
        return None

    # friends_count
    # followers_count
    # location
    # screen_name
    # id
    # description
    # geo_enabled
    # statuses_count
    # profile_image_url
    # profile_image_url_https
    # lang
    # created_at
    # url


def youtube_recon(user_name):
    """Use tweepy to access user data if name found."""
    youtube_key = os.environ.get('YOUTUBE_KEY')
    baseurl = 'https://www.googleapis.com/youtube/v3/'
    url = '{0}search?part=snippet&q={1}&key={2}'.format(baseurl,
                                                        user_name,
                                                        youtube_key)

    try:
        rawres = urlopen(url)
        res = rawres.read()
        response = json.loads(res)
        return response
    except:
        return None


def flickr_recon(user_name):
    """Check for flickr account with user_name."""
    url = 'https://www.flickr.com/people/{}/'.format(user_name)
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "lxml")
        title = soup.find('h1').contents[0].strip()
        av_div = soup.find('div', class_='avatar').attrs['style']
        avatar = 'https:' + av_div.split(' ')[1][4:-2]
        location = soup.find('p', class_='cp-location').contents[0]
        return {'avatar': avatar,
                'title': title,
                'user_name': user_name,
                'url': url,
                'location': location
                }
    else:
        return None


def hacker_recon(user_name):
    """Check for hackernews account with user_name."""
    url = 'https://news.ycombinator.com/user?id={}'.format(user_name)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")
    if b'No such user.' in r.content:
        return {'site': 'Hackernews',
                'empty': 'No hackernews account with that user name.'
                }
    try:
        tds = soup.find_all('td')
        about = tds[4].find_all('td')[7].contents[0].strip()
        return {'site': 'Hackernews',
                'about': about
                }
    except:
        return {'site': 'Hackernews',
                'empty': 'No hackernews account with that user name.'
                }


def imgur_recon(user_name):
    """Check for imgur account with user_name."""
    url = 'https://imgur.com/user/{}'.format(user_name)
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        bio = soup.find('div', id='account-bio').contents[0]
        a_date = soup.find('div', class_='textbox bold')
        acct_date = a_date.contents[2].split('\n')[1].strip()
        return {'acct_date': acct_date,
                'bio': bio,
                'link': 'https://imgur.com/user/{}'.format(user_name),
                'site': 'Imgur'
                }
    else:
        return None


def hacked_email_recon(email):
    """Check if email matches possible hacked emails from various breaches."""
    url = 'https://hacked-emails.com/api?q={}'.format(email)
    r = requests.get(url)
    if r.status_code == 200:
        to_dict = dict(r.json())
        return {
            'hack_dict': to_dict,
            'site': 'Hacked Emails'
        }
    else:
        return None


def wikipedia_recon(user_name):
    """Check for pb account with user_name."""
    url = 'https://en.wikipedia.org/wiki/User:{}'.format(user_name)
    r = requests.get(url)
    if r.status_code == 404:
        return {'site': 'Wikipedia',
                'empty': 'No Wikipedia account with that user name.'
                }
    else:
        return {'site': 'Wikipedia',
                'url': url
                }


def steam_recon(user_name):
    """Check for steam account with user_name."""
    url = 'https://steamcommunity.com/id/{}'.format(user_name)
    r = requests.get(url)
    if 'Sorry!' in r.text:
        return {'site': 'Steam',
                'empty': 'No Steam account with that user name.'
                }
    if 'This profile is private.' in r.text:
        soup = BeautifulSoup(r.content, 'lxml')
        ava = soup.find('div', class_="playerAvatarAutoSizeInner")
        avatar = ava.find('img').attrs['src']
        real_name = soup.find('span', class_='actual_persona_name').contents[0]
        return {'site': 'Steam',
                'avatar': avatar,
                'real_name': real_name,
                'bio': 'Private account'
                }
    else:
        soup = BeautifulSoup(r.content, 'lxml')
        ava = soup.find('div', class_="playerAvatarAutoSizeInner")
        avatar = ava.find('img').attrs['src']
        real_name = soup.find('span', class_='actual_persona_name').contents[0]
        loc = soup.find('div', class_='header_real_name ellipsis')
        location = loc.contents[-1].strip()
        bio = soup.find('div', class_='profile_summary').contents[0].strip()
        return {'site': 'Steam',
                'avatar': avatar,
                'real_name': real_name,
                'location': location,
                'bio': bio
                }


def liveleak_recon(user_name):
    """Check for liveleak account with user_name."""
    url = 'https://www.liveleak.com/c/{}'.format(user_name)
    r = requests.get(url)
    if 'Channel cannot be found!' in r.text:
        return {'site': 'LiveLeak',
                'empty': 'No LiveLeak account with that user name.'
                }
    else:
        soup = BeautifulSoup(r.content, 'lxml')
        loc = soup.find('h1').next_sibling.next_sibling.next_sibling
        location = loc.next_sibling.find('span').contents[0]
        memb = soup.find('h1').next_sibling.next_sibling.next_sibling.\
            next_sibling.next_sibling.next_sibling.find('span').contents[0]
        return {'site': 'LiveLeak',
                'location': location,
                'memb_since': memb,
                'url': url
                }