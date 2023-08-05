"""Module for pulling the stats of a stock from different sites"""
import re
import requests
from bs4 import BeautifulSoup
from common.custom_logging import custom_log

SS_SCORE = "Short Squeeze Score"
STOCKERA_FMT = "https://stocksera.pythonanywhere.com/{}/?quote={}"

class StockData:
    """Class for configuring the pulls to a specific ticker"""
    def __init__(self, ticker):
        """
        Arguments:
        ticker (str): the ticker of the stock to configure the pulls to
        """
        self.ticker = ticker

    def pull_chart_exchange(self):
        """
        Pulls the Cost to Borrow for the self.ticker stock

        Returns:
        dict - with on item of "Cost to Borrow":CTB_STR for compatibility with other
        pulls that return dicts
        None - if the pull failed (check logs)
        """
        url = f"https://chartexchange.com/symbol/nyse-{self.ticker.lower()}/borrow-fee/"
        soup = get_soup(url)
        if soup is not None:
            # find the element with the text
            target_element = find_element_with_partial_text(soup, "shares available with a fee of")

            if target_element:
                # get the next element (which contains the desired value)
                value_element = target_element.find_next_sibling('span')

                if value_element:
                    return {f"Cost to Borrow": value_element.text}
                custom_log("CTB not found.")
            else:
                custom_log("partial text not found.")
        return None

    def pull_frankenz(self):
        """
        Pulls the stock data from frankenz website

        Returns:
        dict of stock info with keys of
            - 'Short Squeeze Score'
            - 'Short Interest'
            - 'Utilization'
            - 'Cost To Borrow'
            - 'Shares On Loan'
            - 'Days To Cover'
        None - if the pull failed (check logs)
        """
        def extract_short_squeeze_score(soup, symbol):
            """
            Gets the squeeze score from frankenz website

            Arguments:
            soup (BeautifulSoup): the soup of the website
            symbol (str): the lowercase of the stock ticker

            Returns:
            int of the Short Squeeze Score of the ticker
            """
            # find the element with the regex pattern
            id_pattern = f'h-{symbol.lower()}-short-squeeze-score-\\d{{1,3}}'
            element = find_element_by_id_with_pattern(soup, id_pattern)

            if element:
                # extract the short squeeze score and return
                score = int(element.get_text().split(':')[-1].strip())
                return score
            custom_log("could not extract SS_SCORE.")
            return None

        url = "https://franknez.com/list-of-momentum-stocks-short-interest-and-utilization/"
        if self.ticker == "AMC":
            bulk_id_value = "h-4-amc-short-interest-today"
        elif self.ticker == "GME":
            bulk_id_value = "h-5-gme-short-interest"
        else:
            custom_log(f"Franknez not set up for this stock {self.ticker}")
        pulled_dict = {}
        soup = get_soup(url)
        if soup is not None:
            # get the short score
            short_squeeze_score = extract_short_squeeze_score(soup, self.ticker.lower())
            if short_squeeze_score is not None:
                pulled_dict[SS_SCORE] = short_squeeze_score

            # find the element with the id to get rest
            target_element = soup.find(id=bulk_id_value)
            if target_element:
                # find the following paragraph element
                next_para = target_element.find_next("p")
                if next_para:
                    # save off the bulk of the stats into the dict
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
        return None

    def pull_stocks_era_price(self):
        """
        Pulls the price data of the self.ticker stock

        Returns:
        dict of the price data of the stock with keys of:
            - 'Rank'
            - 'Day'
            - 'Date'
            - 'Open'
            - 'High'
            - 'Low'
            - 'Close'
            - 'Volume'
            - '% Price Change'
            - 'Amplitude'
            - '% Vol Change'
            - 'Volume / % Price Ratio'
        None - pull failed (check logs)
        """
        return pse_helper(STOCKERA_FMT.format("historical_data", self.ticker))

    def pull_stocks_era_ftd(self):
        """
        Pulls the Failure to Deliver data of the self.ticker stock

        Returns:
        ret_dict - dict of the ftd data of the stock with keys of:
                    - 'Date'
                    - 'Failure to Deliver'
                    - 'Price'
                    - 'Amount (FTD x $)'
                    - 'T+35 Date'
        None - pull failed (check logs)
        """
        ret_dict = pse_helper(STOCKERA_FMT.format("ticker/failure_to_deliver", self.ticker))
        if ret_dict is not None:
            # format the 2 fields that need to be formatted better
            key = "Failure to Deliver"
            ftd_amount = ret_dict.get(key)
            if (ftd_amount is not None) and (len(ftd_amount.split(".")) == 2):
                ftd_amount = ftd_amount.split(".")[0]
                ret_dict[key] = ftd_amount

            key = "Amount (FTD x $)"
            value = ret_dict.get(key)
            if value is not None:
                price = ret_dict.get("Price")
                if price is not None:
                    calculated_amount = int(ftd_amount) * float(price)
                    ret_dict[key] = f"${calculated_amount:.2f}"
        return ret_dict


def find_element_with_partial_text(soup, text):
    """
    finds the first element in the soup that has a specific string in its text

    Arguments:
    soup (BeautifulSoup): the soup of the website
    text (str): the text to find somewhere in the target elements text

    Return:
    None if the string was not found in an element
    PageElement that has the text if found
    """
    for element in soup.find_all(string=True):
        if text in element:
            return element
    return None

def find_element_by_id_with_pattern(soup, pattern):
    """Finds an element with an id that matches a regex pattern

    Arguments:
    soup (BeautifulSoup): the soup of the website
    pattern (str): the regex pattern to use to find the id

    Returns:
    None if element not found
    PageElement with that id if found
    """
    pattern_re = re.compile(pattern)
    return soup.find(id=pattern_re)

def get_soup(url):
    """gets the soup of a webpage

    Arguments:
    url (str): the url to get the soup of
    returns BeautifulSoup of the website
    """
    try:
        response = requests.get(url)
        # check for any HTTP errors
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except requests.exceptions.RequestException as ex:
        custom_log(f"Error fetching the webpage - {ex}")

def get_day_dict(soup, days_from_today):
    """
    extracts the specific day info from soup that has a table that represents
    days from today and then back per <tr>

    Arguments:
    soup (BeautifulSoup) - the soup of the webpage
    days_from_today (int) - the target day represented as days before today

    Returns:
    dict representing that day for the stock ticker (keys depend on what the
    <tr> of the website has for representation of days)
    None - if the day info not found (check logs)
    """
    data_dict = None
    # find all <tr> in the table
    tr_elements = soup.select("tbody tr")
    if tr_elements is None:
        custom_log("soup did not have any <tr>s for days")
    else:
        # find the <tr> we are looking for
        target_tr = None
        for ind, table_row in enumerate(tr_elements):
            if ind == days_from_today:
                target_tr = table_row
                break

        if target_tr:
            data_dict = {}
            # get data from <th> and <td> for a dictionary of this day
            th_elements = soup.select("thead th")
            td_elements = target_tr.select("td")
            for t_header, value in zip(th_elements, td_elements):
                key = t_header.text.strip()
                value = value.text.strip()
                data_dict[key] = value
        else:
            custom_log(f"day {days_from_today} not found in soup")
    return data_dict


def pse_helper(link):
    """Helper for pulling from stocksera. Pulls stock info from a specific day

    NOTE: the website needs a table that represents days from today and then
    back per <tr>

    Arguments:
    link(str) - the link to pull day data from

    Returns:
    dict of that stocks daily information found in the sites table
    None if pull failed
    """
    soup = get_soup(link)
    if soup is not None:
        return get_day_dict(soup, 0)
    return None
