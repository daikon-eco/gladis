import json
import os
import pickle
import platform
from datetime import date, timedelta, datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from crawler.logins import LOGINS, URL

ONE_WEEK = 8
KEYWORDS = {"gmaps": "+Montr%C3%A9al,+QC"}
DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    os.path.join("saves", "db.json"),
)

"""
Implements a Crawler that can load a webdriver, load/save/update the database and run a full search.
Please note that this Class is not intended to work alone.
You should create a subclass for every website you want to scrap (e.g. Inies), which inherits from Crawler.
See the SubCrawler Class for an exemple.
"""


class Crawler:
    def __init__(self, website="", headless=True, db_path=DEFAULT_DB_PATH):
        """
        Args:
            website (str): The name of the website you want to scrap. Should match with the keys of the `LOGINS` dictionnary from `logins.py`, e.g.: 'facebook'
            headless (bool): Set to False if you want the browser to run with a GUI (meaning a window will pop-up). Defaults to True.
            db_path (str): The path to the JSON database. Defaults to ./saves/db.json from the package root.
        """
        self.website = website
        try:
            self.email = LOGINS[website]["id"]
            self.password = LOGINS[website]["pass"]
        except:
            print(
                f"You should first put your login and password for {website} inside"
                f"{os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logins.py')}"
            )
            self.email = "id"
            self.password = "pwd"
        self.db_path = db_path
        self.load_driver(headless=headless)
        self.main_url = URL.get(website, "")
        self.items_links = []
        self.load_db()

    def load_driver(self, headless=True):
        """Load the webdriver.

        Args:
            headless (bool): Set to False if you want the browser to run with a GUI (meaning a window will pop-up). Defaults to True.
        """
        # Handle the 'Allow notifications box':
        options = Options()
        options.add_argument("--disable-infobars")
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")
        options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )
        if headless:
            options.add_argument("--headless")
        system_name = platform.system()  # Linux, Mac, Windows
        system_arch = platform.machine()  # arm, amd64, ...
        if system_name == "Linux" and system_arch == "amd64":  # if Docker
            options.add_argument("window-size=1024,768")
            options.add_argument("--no-sandbox")

        try:
            if system_name == "Linux" and system_arch == "armv7l":  # if Raspberry Pi
                # browser is Chromium
                options.BinaryLocation = "/usr/bin/chromium-browser"
                # custom chromedriver for Raspberry
                driver_path = "/usr/bin/chromedriver"
            else:
                driver_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                    os.path.join("driver", "chromedriver"),
                )
            self.driver = webdriver.Chrome(
                service=Service(driver_path), options=options
            )
            self.driver.implicitly_wait(10)
        except:
            print(
                "Error: Check that your chromedriver fits with your browser version and your system architecture"
            )

    def quit_driver(self):
        """Quit the webdriver."""
        self.driver.quit()

    def save_cookies(self):
        """Save cookies from current session.
        The cookies are saved in ./saves/cookies-<WEBSITE_NAME>.pkl from package root.
        """
        cookies_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            "saves",
            f"cookies-{self.website}.pkl",
        )
        with open(cookies_path, "wb") as cookies_file:
            pickle.dump(self.driver.get_cookies(), cookies_file)

    def load_cookies(self):
        """Load the cookies previously saved so that the webdriver don't need to log in every time it opens a webdriver for `self.website`."""
        self.driver.get(self.main_url)
        cookies_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            "saves",
            f"cookies-{self.website}.pkl",
        )
        with open(cookies_path, "rb") as cookies_file:
            cookies = pickle.load(cookies_file)
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def log_in(self):
        """Get the webdriver to the main page so that it can log in.
        The full version of this method needs to be implemented inside each subclass, as the way to log in is different from one website to another.
        """
        self.driver.get(self.main_url)

    def get_items_links(self, **kwargs):
        """Get links (i.e. url) of ads matching the search criteria.
        The full version of this method needs to be implemented inside each subclass, as the way to look for matching ads is different from one website to another.

        Args:
            **kwargs: You search criteria, depending on the website you're scrapping (eg. minimum price, number of bedrooms, ...).
                      This is managed at the Subscraper Class level (e.g. Facebook Class)
        Returns:
            list: A list of all the flats url (or items links) that match the search criteria.
        """
        return self.items_links

    def get_item_details(self, item_url, **kwargs):
        """Go to the item url with the webdriver and scrap as much details as possible about the item.
        The full version of this method needs to be implemented inside each subclass, as the way to get these details is different from one website to another.

        Args:
            item_url (str): The url (or link) of the item.
            **kwargs: Additional search criteria, e.g. `remove_first_floor`.
                      See the implementation of the method inside each SubScraper class for additional details.

        Returns:
            dict: A dictionnary with all the item details.
        """
        item_details = {}
        item_details["url"] = item_url
        self.driver.get(item_url)
        return item_details

    def item_details_to_string(self, item_details):
        """Get a string representation of an item details (address, price, description, ...).

        Args:
            item_details (dict): A dictionnary with all the item details.

        Returns:
            str: A string representation of these details.
        """
        sentence = ""
        for key, value in item_details.items():
            if key not in ("images", "state") and value != "":
                sentence += f"{key}: {value} \n"
        sentence += "\n  " + "=" * 40 + "\n  " + "=" * 40 + "\n"
        return sentence

    def item_details_to_html(self, item_details):
        """Get a html representation of an item details (address, price, description, ...).
        The main difference from the string representation is that you get a clickable Google Maps url for the address, and a clickable url for the item link.

        Args:
            item_details (dict): A dictionnary with all the item details.

        Returns:
            str: A html representation of these details.
        """
        sentence = ""
        for key, value in item_details.items():
            if key not in ("images", "state") and value != "":
                if key == "url":
                    sentence += f"{key}: <a target='_blank' href='{value}'>{value[-15:-1]}</a> \n"
                elif key == "address":
                    href = f"""https://www.google.com/maps/place/{value.replace(" ", "+").replace("'", "+")},{KEYWORDS["gmaps"]}"""
                    sentence += (
                        f"{key}: <a target='_blank' href='{href}'>{value}</a> \n"
                    )
                elif key == "price":
                    sentence += f"{key}: {value} $ \n"
                elif key == "surface":
                    sentence += f"{key}: {value} m² \n"
                else:
                    sentence += f"{key}: {value} \n"
        return sentence

    def is_old(self, item_details):
        """Return True if the item has been published more than a week ago.

        Args:
            item_details (dict): A dictionnary with all the item details.
        """
        return (
            item_details.get("published")
            == (date.today() - timedelta(days=ONE_WEEK)).isoformat()
        )

    def is_duplicate(self, item_details):
        """Return True if the item has previously been seen (i.e. this item already exists inside the database but with a different url).
        It can happens when people repost their ads every week or so, in order for their ads to be on top page.

        Args:
            item_details (dict): A dictionnary with all the item details.
        """
        all_description = [data[-1] for data in self.db["data"] if data[-1] != ""]
        return item_details.get("description") in all_description

    def is_swap(self, item_details):
        """Return True if the item is about swapping flats instead of renting one.

        Args:
            item_details (dict): A dictionnary with all the item details.
        """
        return any(
            swap in item_details.get("description", "").lower()
            for swap in ("swap", "transfer", "échange", "exchange")
        )

    def is_first_floor(self, item_details):
        """Return True if the item is on the ground floor (also called first floor in America).

        Args:
            item_details (dict): A dictionnary with all the item details.
        """
        return any(
            ff in item_details.get("description", "").lower()
            for ff in (
                "ground floor",
                "first floor",
                "rdc",
                "rez-de-chaussée",
                "rez de chaussée",
            )
        )

    def update_db(self, max_items=30, to_html=False, **kwargs):
        """Go to every items links from `self.items_links` and scrap every details from theses pages.
        Then, save all these details inside the database and return string or html representations of these.

        Args:
            max_items (int): The maximum number of items you want to scrap for each run. It is good use to not set it too high, to avoid getting banned from the website. Defaults to 30.
            to_html (bool): If set to True, return a list of html representations of the items details. Defaults to False.
            **kwargs: Additional search criteria for the get_item_details() method, e.g. `remove_first_floor`.
                      See the implementation of the method inside each SubScraper class for additional details.

        Returns:
            list: A list of all the string or html representations of the items details. It is usefull for printing all the details from the new flats you found.
        """
        items_details = []
        cnt = 0
        for item_url in self.items_links[:max_items]:
            item_details = self.get_item_details(item_url, **kwargs)
            self.db["data"].append(
                [item_details.get(feature, "") for feature in self.db["columns"]]
            )
            if item_details.get("state") == "new":
                # If the ad is interesting
                cnt += 1
                if to_html:
                    items_details.append(self.item_details_to_html(item_details))
                else:
                    items_details.append(self.item_details_to_string(item_details))
            if not cnt % 10:
                self.save_db()
        print(
            f"{date.today().strftime('%Y-%m-%d')} {datetime.now().strftime('%H:%M:%S')} - {cnt} new ads"
        )
        self.save_db()
        self.items_links = []
        return items_details

    def load_db(self):
        """Load the JSON database and assign it to `self.db` as a dictionnary."""
        if os.path.isfile(self.db_path):  # if the db's json exists, load it
            with open(self.db_path, "r") as db_file:
                self.db = json.load(db_file)
        else:  # if it doesn't exist, create a raw one and save it
            self.db = {
                "columns": [
                    "url",
                    "state",
                    "published",
                    "price",
                    "bedrooms",
                    "surface",
                    "address",
                    "furnished",
                    "images",
                    "description",
                ],
                "data": [],
            }
            self.save_db()

    def save_db(self):
        """Save the database dictionnary as a JSON file."""
        try:
            with open(self.db_path, "w") as db_file:
                json.dump(self.db, db_file)
        except:
            print(
                f"Error while trying to save the database to `{self.db_path}`. Please use a valid path, e.g. `./data/db.json`"
            )

    def run(self, to_html=False, max_items=30, **kwargs):
        """Main method to run a full search : log in, get links, scrap all the links, update the database with the new ads, quit the webdriver.

        Args:
            to_html (bool): If set to True, return a list of html representations of the items details. Defaults to False.
            max_items (int): The maximum number of items you want to scrap for each run. It is good use to not set it too high, to avoid getting banned. Defaults to 30.
            **kwargs: You search criteria, depending on the website you're scrapping (eg. minimum price, number of bedrooms, ...)

        Returns:
            list: A list of all the string or html representations of the items details. It is usefull for printing all the details from the new flats you found.
        """
        # cookies_path = os.path.join(
        #     os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
        #     "saves/cookies.pkl",
        # )
        # if not os.path.isfile(cookies_path):
        #     self.log_in()
        # else:
        #     self.load_cookies()
        self.log_in()
        self.get_items_links(**kwargs)
        items_details = self.update_db(max_items=max_items, to_html=to_html)
        self.quit_driver()
        return items_details
