import tweepy
import json
from common.custom_logging import custom_log

def get_api(json_file, symbol):
    with open(json_file, "r") as file_ptr:
        json_data = json.load(file_ptr)
    json_data = json_data[symbol]
    client = tweepy.Client(json_data["bearer_token"],
                           json_data["api_key"],
                           json_data["api_key_secret"],
                           json_data["access_token"],
                           json_data["access_token_secret"])
    auth = tweepy.OAuth1UserHandler(json_data["api_key"],
                                    json_data["api_key_secret"],
                                    json_data["access_token"],
                                    json_data["access_token_secret"])
    api = tweepy.API(auth)
    return api, client

def tweet(client, message, tags=None, dont_send=False):
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
