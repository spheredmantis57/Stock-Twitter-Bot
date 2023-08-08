import unittest
from os.path import dirname, join
from functools import partial
from unittest.mock import patch
from stock_data.pull_data import StockData
from bs4 import BeautifulSoup
from dataclasses import dataclass

SITE_DIR = join(dirname(__file__), "sites")
SITE_FILE_F = partial(join, SITE_DIR)

@dataclass
class TestData:
    ticker: str
    expected_result: dict
    expected_pass: bool

CE_LINK = "{}ChartExchange.html"

class TestStockData(unittest.TestCase):
    def _helper_pull_test(self, link, test_data, pull_func):
        with open(SITE_FILE_F(link)) as file_ptr:
            html_contents = file_ptr.read()
        stock = StockData(test_data.ticker)
        with patch('stock_data.pull_data.get_soup') as mock_get_soup:
            mock_get_soup.return_value = BeautifulSoup(html_contents, "html.parser")
            if pull_func == 0:
                result = stock.pull_chart_exchange()
        if test_data.expected_pass:
            self.assertEqual(result, test_data.expected_result)
        else:
            self.assertNotEqual(result, test_data.expected_result)

    def test_pull_chart_exchange_amc_pass(self):
        test_data = TestData("AMC", {"Cost to Borrow": "243.94%"}, True)
        link = CE_LINK.format(test_data.ticker)
        self._helper_pull_test(link, test_data, 0)

    def test_pull_chart_exchange_gme_pass(self):
        test_data = TestData("GME", {"Cost to Borrow": "5.22%"}, True)
        link = CE_LINK.format(test_data.ticker)
        self._helper_pull_test(link, test_data, 0)

    def test_pull_chart_exchange_fail(self):
        test_data = TestData("BAD", {"Cost to Borrow": "Doesn't Matter"}, False)
        link = CE_LINK.format(test_data.ticker)
        self._helper_pull_test(link, test_data, 0)

    def test_pull_frankenz_amc_pass(self):
        pass

    def test_pull_frankenz_gme_pass(self):
        pass

    def test_pull_frankenz_fail(self):
        pass

if __name__ == '__main__':
    unittest.main()
