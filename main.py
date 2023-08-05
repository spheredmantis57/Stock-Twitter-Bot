import argparse
from datetime import date
from common import emojis
from common.custom_logging import basicConfig, custom_log
from os.path import abspath
from stock_data import pull_data
from twitter.tweet import get_api, tweet

# todo comment/pylint
# todo README

DESIRED_FRANKENZ = ["Short Interest", "Days To Cover", pull_data.SS_SCORE]
DESIRED_PRICE = ["Date", "Open", "Close", "High", "Low", "% Price Change"]
DESIRED_FTD = ["Date", "Failure to Deliver", "Price", "Amount (FTD x $)"]

GME_TAGS = ["$GME #GME #GameStop #GMESTOP"]
AMC_TAGS = ["$AMC #AMC #SECScandal", "#Ape #ThresholdList AMCSTOCK"]
SHARED_TAGS = ["#Moon #NeverLeaving #MOASS #ApesTogetherStrong", "#Squeeze #FTD #Bullish #NYSE"]

def stringize_dict(dictionary, filter_keys=None):
    return_lst = []
    if filter_keys:
        dictionary = {key: dictionary[key] for key in dictionary if key in filter_keys}
    for key in dictionary:
        return_lst.append(f"{key}: {dictionary[key]}")
    return return_lst

def get_tweet(mode):
    tweet = []

    for start, pull_func, filter in [(f"{mode} Price {emojis.STONK}{emojis.FIRE}", pull_data.pull_stocks_era_price, DESIRED_PRICE),
                              (f"\n{mode} Misc Stats{emojis.ROCKET}{emojis.APE}\nDate: {date.today()}", pull_data.pull_frankenz, DESIRED_FRANKENZ),
                              (None, pull_data.pull_chart_exchange, None),
                              (f"\n{mode} Most recent FTD info {emojis.MOON}{emojis.CASH}", pull_data.pull_stocks_era_ftd, DESIRED_FTD)]:
        info = pull_func()
        if start:
            tweet.extend([start,])
        if info is not None:
            tweet.extend(stringize_dict(info, filter))

    return "\n".join(tweet)

def set_up():
    basicConfig("log.txt")
    choices = {
        "AMC": pull_data.stock_config_amc,
        "GME": pull_data.stock_config_gme}
    parser = argparse.ArgumentParser(description="Set the mode.")
    parser.add_argument(
        "--mode",
        choices=choices.keys(),
        required=True,
        help=f"Choose the mode. Available choices: {', '.join(choices.keys())}. Default: {pull_data.MODE}",
    )
    parser.add_argument("--ndebug", action="store_false",
                        help="Will actually send the tweet")
    args = parser.parse_args()
    args.tags = None
    if args.mode == "AMC":
        pull_data.stock_config_amc()
        args.tags = AMC_TAGS.copy()
        args.tags.extend(SHARED_TAGS)
    elif args.mode == "GME":
        args.tags = GME_TAGS.copy()
        args.tags.extend(SHARED_TAGS)
        pull_data.stock_config_gme()
    return args

def main():
    args = set_up()
    tweet_message = get_tweet(args.mode)
    try:
        api, client = get_api(abspath("twitter/.data.json"), args.mode)
    except KeyError:
        custom_log(f"JSON: {args.mode} is not yet set up")
        return
    for message in tweet_message.split("\n\n"):
        tweet(client, message, args.tags, args.ndebug)

if __name__ == "__main__":
    main()
