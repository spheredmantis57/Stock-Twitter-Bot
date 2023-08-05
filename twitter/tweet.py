"""Module for functions to tweet"""
import json
import tweepy
from common.custom_logging import custom_log

def get_api(json_file, symbol):
    """connects to the twitter account

    json_file (str): path to the json file that holds the key of the Ticker and
                     subkeys of:
                        -"bearer_token"
                        - "api_key"
                        - "api_key_secret"
                        - "access_token"
                        - "access_token_secret"
    symbol: the Ticker to look up in the json

    Returns:
    api, client
    api (tweepy.API): Twitter API v1.1 Interface
    client (tweepy.Client): Twitter API v2 Client
    """
    # load keys and tokens
    with open(json_file, "r") as file_ptr:
        json_data = json.load(file_ptr)
    json_data = json_data[symbol]
    # get the client
    client = tweepy.Client(json_data["bearer_token"],
                           json_data["api_key"],
                           json_data["api_key_secret"],
                           json_data["access_token"],
                           json_data["access_token_secret"])
    # authenticate
    auth = tweepy.OAuth1UserHandler(json_data["api_key"],
                                    json_data["api_key_secret"],
                                    json_data["access_token"],
                                    json_data["access_token_secret"])
    api = tweepy.API(auth)
    return api, client

def tweet(client, message, tags=None, dont_send=False):
    """tweets a message

    Arguments:
    client (tweepy.Client): Twitter API v2 Client
    message (str): the contents of the tweet
    tags (str[]): the list of tags to put at the end of the tweet
    dont_send (bool): True to not actually send the tweet but print it and len
                      False to actually send the tweet
    """
    if tags is not None:
        message = [message, ]
        message.extend(tags)
        message = "\n".join(message)
    if dont_send:
        print(f"{len(message) = }")
        print(f"'{message}'\n")
    else:
        try:
            client.create_tweet(text=message)
        except tweepy.errors.BadRequest as ex:
            custom_log(f"{ex}\nfor {len(message) = }: '{message}'")
