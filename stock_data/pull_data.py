import re
from common.custom_logging import custom_log
from bs4 import BeautifulSoup
import requests

MODE = "AMC"
SS_SCORE = "Short Squeeze Score"

def stock_config_gme():
    global MODE
    MODE = "GME"

def stock_config_amc():
    global MODE
    MODE = "AMC"

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
                return {f"Cost to Borrow": value_element.text}
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

def pull_stocks_era_ftd():
    ret_dict = pse_helper(f"https://stocksera.pythonanywhere.com/ticker/failure_to_deliver/?quote={MODE}")
    # format a couple fields
    if ret_dict is not None:
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

def pull_stocks_era_price():
    return pse_helper(f"https://stocksera.pythonanywhere.com/historical_data/?quote={MODE}")
