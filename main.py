"""Main module for the stock twitter bot"""
import argparse
from os.path import abspath, exists, dirname
from common import emojis
from common.custom_logging import basic_config, custom_log
from stock_data import pull_data
from twitter.tweet import get_api, tweet

DESIRED_FRANKENZ = ["Short Interest", "Days To Cover", pull_data.SS_SCORE]
DESIRED_PRICE = ["Date", "Open", "Close", "High", "Low", "% Price Change"]
DESIRED_FTD = ["Date", "Failure to Deliver", "Price", "Amount (FTD x $)"]

GME_TAGS = ["$GME #GME #GameStop #GMESTOP"]
AMC_TAGS = ["$AMC #AMC #SECScandal", "#Ape #ThresholdList #AMCSTOCK"]
SHARED_TAGS = ["#Moon #NeverLeaving #MOASS #ApesTogetherStrong", "#Squeeze #FTD #Bullish #NYSE"]

def stringize_dict(dictionary, filter_keys=None):
    """Takes a dict and makes it into a list with items of str 'Key: Value'

    Arguments:
    dictionary (dict): the functionary to stringize
    filter_keys (str[], None): if desired, a list of keys that should be used.
                               Acts as a whitelist.
                               If None, all keys will be used

    Returns:
    str[] of the stringized dict
    """
    return_lst = []
    if filter_keys:
        dictionary = {key: dictionary[key] for key in dictionary if key in filter_keys}
    for key in dictionary:
        return_lst.append(f"{key}: {dictionary[key]}")
    return return_lst

def get_tweet(mode):
    """pulls the stock data and builds the tweet message

    Arguments:
    mode (str): the ticker of the stock

    returns:
    str the twitter message
    """
    tweet_message = []
    puller = pull_data.StockData(mode)

    # create the long tups for the for loop
    price_tup = (f"{mode} Price {emojis.STONK}{emojis.FIRE}",
                 puller.pull_stocks_era_price,
                 DESIRED_PRICE)

    frankenz_str = f"\n{mode} Misc Stats{emojis.ROCKET}{emojis.APE}"
    frankenz_tup = (frankenz_str,
                    puller.pull_frankenz,
                    DESIRED_FRANKENZ)

    fdt_tup = (f"\n{mode} Most recent FTD info {emojis.MOON}{emojis.CASH}",
               puller.pull_stocks_era_ftd,
               DESIRED_FTD)

    # start is the header for the dict
    # pull_func is called to the get the dict to format and add to the tweet
    # filter is a list of key names to grab from the resulting dict
    for start, pull_func, filter_list in [price_tup,
                                          frankenz_tup,
                                          (None, puller.pull_chart_exchange, None),
                                          fdt_tup]:
        # pull dict and add to the tweet
        info = pull_func()
        if start:
            tweet_message.extend([start,])
        if info is not None:
            tweet_message.extend(stringize_dict(info, filter_list))

    return "\n".join(tweet_message)

def set_up():
    """Parses the args, configures logging, and builds tags"""
    choices = ["AMC", "GME"]
    parser = argparse.ArgumentParser(description="Stock Twitter Bot")
    parser.add_argument(
        "--log",
        type=str,
        required=True,
        help="The path to the log file",
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="The path to the config json",
    )
    parser.add_argument(
        "--mode",
        choices=choices,
        required=True,
        help="Choose the ticker to get data for",
    )
    parser.add_argument("--ndebug", action="store_false",
                        help="Will actually send the tweet")
    args = parser.parse_args()

    if not exists(dirname(args.log)):
        raise FileNotFoundError(f"Path to log file does not exist: {args.log}")
    basic_config(args.log)
    args.config = abspath(args.config)
    args.tags = None
    if args.mode == "AMC":
        args.tags = AMC_TAGS.copy()
    elif args.mode == "GME":
        args.tags = GME_TAGS.copy()
        args.tags.extend(SHARED_TAGS)
    return args

def main():
    """The main func of the program"""
    try:
        args = set_up()
    except FileNotFoundError as ex:
        print(ex)
        return
    tweet_message = get_tweet(args.mode)
    try:
        _, client = get_api(abspath(args.config), args.mode)
    except KeyError:
        custom_log(f"JSON: {args.mode} is not yet set up")
        return
    except FileNotFoundError:
        custom_log(f"JSON: {args.config} does not exist")
        return
    for message in tweet_message.split("\n\n"):
        tweet(client, message, args.tags, args.ndebug)

if __name__ == "__main__":
    main()
