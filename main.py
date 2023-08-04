import argparse
import requests
import re
from common.custom_logging import custom_log, basicConfig
from functools import partial
from bs4 import BeautifulSoup

MODE_CHOICES = ["GME", "AMC"]
MODE = "AMC"

SS_SCORE = "Short Squeeze Score"
DESIRED_FRANKENZ = ["Short Interest", "Days To Cover", SS_SCORE]
DESIRED_PRICE = ["Date", "Open", "Close", "High", "Low", "% Price Change"]
DESIRED_FTD = ["Date", "Failure to Deliver", "Price", "Amount (FTD x $)"]

# todo comment/pylint
# todo README

def find_element_with_partial_text(soup, text):
    for element in soup.find_all(string=True):
        if text in element:
            return element

def find_element_by_id_with_pattern(soup, pattern):
    pattern_re = re.compile(pattern)
    return soup.find(id=pattern_re)

def get_soup(url):
    try:
        response = requests.get(url)
        # check for any HTTP errors
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        custom_log(f"Error fetching the webpage - {e}")

def pull_chart_exchange():
    url = f"https://chartexchange.com/symbol/nyse-{MODE.lower()}/borrow-fee/"
    soup = get_soup(url)
    if soup is not None:
        # find the element with the text
        target_element = find_element_with_partial_text(soup, "shares available with a fee of")

        if target_element:
            # get the next element (which contains the desired value)
            value_element = target_element.find_next_sibling('span')

            if value_element:
                return value_element.text
            else:
                custom_log("CTB not found.")
        else:
            custom_log("partial text not found.")

def pull_frankenz():
    def extract_short_squeeze_score(soup, symbol):
        # find the element with the regex pattern
        id_pattern = f'h-{symbol.lower()}-short-squeeze-score-\\d{{1,3}}'
        element = find_element_by_id_with_pattern(soup, id_pattern)

        if element:
            # extract the short squeeze score and return
            score = int(element.get_text().split(':')[-1].strip())
            return score
        else:
            custom_log("could not extract SS_SCORE.")

    # save name so I dont need to update printing if I refactor
    url = "https://franknez.com/list-of-momentum-stocks-short-interest-and-utilization/"
    if MODE == "AMC":
        bulk_id_value = "h-4-amc-short-interest-today"
    elif MODE == "GME":
        bulk_id_value = "h-5-gme-short-interest"
    else:
        custom_log(f"Franknez not set up for this stock {MODE}")
        return
    pulled_dict = {}
    soup = get_soup(url)
    if soup is not None:
        # get the short score
        short_squeeze_score = extract_short_squeeze_score(soup, MODE.lower())
        if short_squeeze_score is not None:
            pulled_dict[SS_SCORE] = short_squeeze_score

        # find the element with the id to get rest
        target_element = soup.find(id=bulk_id_value)
        if target_element:
            # find the following paragraph element
            next_para = target_element.find_next("p")
            if next_para:
                para_text = next_para.get_text()
                kv_pairs = [pair.strip() for pair in para_text.split("|")]
                for pair in kv_pairs:
                    key, value = pair.split(":", 1)
                    pulled_dict[key.strip()] = value.strip()
            else:
                custom_log("did not find next para")
        else:
            custom_log("did not find element with id")
        return pulled_dict

def get_day_dict(soup, days_from_today):
        data_dict = {}
        # find all <tr> in the table
        tr_elements = soup.select("tbody tr")

        # find the <tr> we are looking for
        target_tr = None
        for ind, tr in enumerate(tr_elements):
            if ind == days_from_today:
                target_tr = tr
                break

        if target_tr:
            # get data from <th> and <td> for a dictionary of this day
            th_elements = soup.select("thead th")
            td_elements = target_tr.select("td")
            for th, td in zip(th_elements, td_elements):
                key = th.text.strip()
                value = td.text.strip()
                data_dict[key] = value

        return data_dict


def pse_helper(link):
    soup = get_soup(link)
    if soup is not None:
        return get_day_dict(soup, 0)

def pull_stocks_era():
    failure_to_deliver  = pse_helper(f"https://stocksera.pythonanywhere.com/ticker/failure_to_deliver/?quote={MODE}")
    price = pse_helper(f"https://stocksera.pythonanywhere.com/historical_data/?quote={MODE}")
    return price, failure_to_deliver

def format_dict(dictionary, filter_keys=None):
    return_str = ""
    if filter_keys:
        dictionary = {key: dictionary[key] for key in dictionary if key in filter_keys}
    for key in dictionary:
        return_str = f"{return_str}{key}: {dictionary[key]}\n"
    print(return_str)


def main():
    basicConfig("log.txt")
    global MODE
    parser = argparse.ArgumentParser(description="Set the mode.")
    parser.add_argument(
        "--mode",
        choices=MODE_CHOICES,
        default=MODE,
        help=f"Choose the mode. Available choices: {', '.join(MODE_CHOICES)}. Default: {MODE}",
    )
    args = parser.parse_args()
    MODE = args.mode

    cost_to_borrow = pull_chart_exchange()
    if cost_to_borrow is None:
        custom_log("pull_chart_exchange failed")
    else:
        print(f"{cost_to_borrow = }")

    frankenz_dict = pull_frankenz()
    if frankenz_dict is None:
        custom_log("frankenz_dict failed")
    else:
        format_dict(frankenz_dict, DESIRED_FRANKENZ)
    price, failure_to_deliver = pull_stocks_era()
    if price is None:
        print("failed to get price data from stocks era")
    else:
        format_dict(price, DESIRED_PRICE)
    if failure_to_deliver is None:
        print("failed to get FTD data from stocks era")
    else:
        format_dict(failure_to_deliver, DESIRED_FTD)

if __name__ == "__main__":
    main()
