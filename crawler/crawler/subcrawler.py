import os
import random
from datetime import date, timedelta
from time import sleep

from crawler.crawler import Crawler, ONE_WEEK

from selenium.webdriver.common.by import By


MAX_SURFACE = 200  # The max surface after which it is considered that the surface is actually in square feet and not square metre.
WEBSITE_NAME = "<WEBSITE_NAME"
KEYWORDS = {
    "day": "jours",
    "week": "semaine",
    "montreal": "Montréal, QC",
    "surface(ft2)": "pieds carrés",
    "see_more": "Voir plus",
    "see_less": "Voir moins",
    "next_img": "Voir l’image suivante",
}

"""
An example Subcrawler class (heriting from Scraper) with all the method needed to be implemented to work properly within the flatfindr library.
One new website to scrap == One new Subcrawler class (e.g. Facebook, Kijiji, etc.).
"""


class Subcrawler(Crawler):
    def __init__(
        self,
        **kwargs,
    ):
        """
        Args:
            headless (bool): Set to False if you want the browser to run with a GUI (meaning a window will pop-up). Defaults to True.
            db_path (str): The path to the JSON database. Defaults to ./saves/db.json from the root of the flatfindr library.
            slow (bool): Set to True if you want the wole process to run slowly by adding a lot of waiting times inside the methods.
                         This is particularly usefull if you're running the scripts on a slow machine, e.g. a Rasbery Pi, so that the webpages don't switch to fast for it to get the details.
                         Defaults to False.
        """
        super().__init__(website=WEBSITE_NAME, **kwargs)

    def log_in(self):
        """Log in the website."""
        super().log_in()
        if self.slow:
            sleep(random.uniform(2, 2.5))
        try:
            email_input = self.driver.find_element(By.ID, "email")
            email_input.send_keys(self.email)
            sleep(random.uniform(0.2, 0.5))
            password_input = self.driver.find_element(By.ID, "pass")
            password_input.send_keys(self.password)
            sleep(random.uniform(0.2, 0.5))
            login_button = self.driver.find_element(By.XPATH, "//*[@type='submit']")
            login_button.click()
            sleep(random.uniform(2, 3))
            # self.save_cookies()
        except Exception:
            print(
                "Some exception occurred while trying to find username or password field"
            )

    def get_items_links(
        self,
        min_price=1_200,
        max_price=1_750,
        min_bedrooms=2,
        lat=45.5254,
        lng=-73.5724,
        radius=2,
        scroll=10,
    ):
        """Get links (i.e. url) of ads matching the search criteria.

        Args: (you can add as many as you want)
            min_price (int): The minimum price of your next apartment. Defaults to 1_200.
            max_price (int): The maximum price of your next apartment. Defaults to 1_750.
            min_bedrooms (int): The minimum number of bedrooms of your next apartment. Defaults to 2.
            lat (float): The latitude of your prefered position for your next apartment. Defaults to 45.5254.
            lng (float): The longitude of your prefered position for your next apartment. Defaults to -73.5724.
            radius (int): The radius around your prefered position, in km. Defaults to 2.
            scroll (int): The number of scrollings (or new pages) you want to do (or go to) before stopping looking for new ads. Defaults to 10.

        Returns:
            list: A list of all the flats url (or items links) that match the search criteria.
        """
        rentals = "/marketplace/category/propertyrentals?"
        price = f"minPrice={min_price}&maxPrice={max_price}"
        bedrooms = f"&minBedrooms={min_bedrooms}"
        pos = f"&exact=false&latitude={lat}&longitude={lng}&radius={radius}"
        self.driver.get(self.main_url + rentals + price + bedrooms + pos)
        if self.slow:
            sleep(random.uniform(5, 7))

        seen_links = [data[0] for data in self.db["data"]]

        for _ in range(scroll):
            try:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                sleep(random.uniform(1.5, 2))
            except:
                pass

        if self.slow:
            sleep(random.uniform(2, 3))
        all_href = self.driver.find_elements(By.XPATH, "//a[@href]")
        for item in all_href:
            try:
                item_url = item.get_attribute("href")
                if "/marketplace/item/" in item_url:
                    item_url = item_url[: item_url.find("?")]
                    # If this item has never been scraped before, we add it
                    if item_url not in seen_links and item_url not in self.items_links:
                        self.items_links.append(item_url)
            except:
                pass

        return self.items_links

    def get_item_publication_date(self):
        """Get the item publication date.

        Returns:
            str: The publication day, in isoformat, e.g. '2022-02-11'
        """
        detail = self.driver.find_element(
            By.XPATH, "//div[@itemprop='datePosted']"
        ).text
        if KEYWORDS["day"] in detail:  # if published less than a week ago
            try:
                publication_day = int(detail[20])
            except:
                print("Error while casting publication day")
                # we consider that the ad has been published today
                publication_day = 0
        elif KEYWORDS["week"] in detail:
            # if published more than a week ago, we use 8 as default
            publication_day = ONE_WEEK
        else:
            # if published less than a day ago, we use 0 as default
            publication_day = 0
        # Cast into a date
        return (date.today() - timedelta(days=publication_day)).isoformat()

    def get_item_price(self):
        """Get the item price from an input string.

        Returns:
            int: The item price, e.g. 1300
        """
        detail = self.driver.find_element(By.XPATH, "//span[@itemprop='price']").text
        try:
            return int(detail[:5].replace(" ", ""))
        except:
            print("Error while casting price")
            return 0

    def get_item_address(self):
        """Get the item address from an input string.

        Returns:
            str: The item address, without the city, province, ... e.g. '5510 Avenue Stirling'.
        """
        detail = self.driver.find_element(By.XPATH, "//span[@itemprop='price']").text
        return detail.replace(KEYWORDS["montreal"], "").replace(", ", "")

    def get_item_surface(self):
        """Get the item surface, in m2.

        Returns:
            int: The item surface, in m2.
        """
        detail = self.driver.find_element(By.XPATH, "//span[@itemprop='size']").text
        try:
            surface = int(detail[:4].replace(" ", ""))
        except:
            print("Error while casting surface")
            return 0
        if KEYWORDS["surface(ft2)"] in detail or surface > MAX_SURFACE:
            # if square feet (considering that a surface > MAX_SURFACE is necessarily in ft2)
            surface = round(surface / 10.764)
        return surface

    def get_item_bedrooms(self):
        """Get the item number of bedrooms.

        Returns:
            int: The item number of bedrooms, e.g. 2.
        """
        detail = self.driver.find_element(
            By.XPATH, "//span[@itemprop='roomAttribute']"
        ).text
        try:
            return int(detail[0])
        except:
            print("Error while casting number of bedrooms")
            return 0

    def get_item_furnished(self):
        """Get the item description about being furnished or not.

        Returns:
            str: A string with the information about the flat being furnished or not, e.g. 'Not furnished'.
        """
        return self.driver.find_element(By.XPATH, "//span[@itemprop='furnished']").text

    def get_item_description(self):
        """Get the item description.

        Returns:
            str: A string with the item description.
        """
        buttons = self.driver.find_elements(By.XPATH, "//div[@role='button']")
        # Click on 'see more' button to get the full description
        _ = [
            button.click() for button in buttons if button.text == KEYWORDS["see_more"]
        ]
        sleep(random.uniform(0.5, 0.9))
        detail = self.driver.find_element(
            By.XPATH, "//div[@class='showMoreWrapper']"
        ).text
        return detail.replace(KEYWORDS["see_less"], "")

    def get_item_images(self):
        """Get the item images/photos/pictures, as a list of url.

        Returns:
            list: A list of all the item images url.
        """
        images = []
        cnt = 0
        while cnt < 30:
            # to avoid infinite loop, we stop after 30 clicks
            try:
                img = self.driver.find_element(
                    By.XPATH, "//img[@referrerpolicy='origin-when-cross-origin']"
                )
                img_url = img.get_attribute("src")
                if any(size in img_url for size in ("p720x720", "s960x960")):
                    # If a picture of the apartment
                    if img_url not in images:  # if unseen
                        images.append(img_url)
                    else:
                        break  # if already seen
            except:
                print("Error while scraping images")
            cnt += 1
            try:
                next_button = self.driver.find_element(
                    By.XPATH, f"//div[@aria-label='{KEYWORDS['next_img']}']"
                )
                next_button.click()
                sleep(random.uniform(1, 1.2))
            except:  # only 1 picture for this ad so there is no next button
                break
        return images

    def get_item_details(self, item_url, remove_swap=True, remove_first_floor=True):
        """Go to the item url with the webdriver and scrap as much details as possible about the item.

        Args:
            item_url (str): The url (or link) of the item.
            remove_swap (bool): Set to False if you want to see ads about swaping apartments. Defaults to True.
            remove_first_floor (bool): Set to False if you want to see ads with flats on ground floor. Defaults to True.

        Returns:
            dict: A dictionnary with all the item details.
        """
        item_details = super().get_item_details(item_url)
        if self.slow:
            sleep(random.uniform(5, 5.5))

        item_details["published"] = self.get_item_publication_date()
        item_details["price"] = self.get_item_price()
        item_details["address"] = self.get_item_address()
        item_details["surface"] = self.get_item_surface()
        item_details["bedrooms"] = self.get_item_bedrooms()
        item_details["furnished"] = self.get_item_furnished()
        item_details["description"] = self.get_item_description()

        if any(
            (
                self.is_old(item_details),
                self.is_duplicate(item_details),
                self.is_swap(item_details) and remove_swap,
                self.is_first_floor(item_details) and remove_first_floor,
            )
        ):
            # We are not interested by this ads
            item_details["state"] = "NI"
            item_details["description"] = ""
            item_details["images"] = []
        else:
            item_details["state"] = "new"
            item_details["images"] = []  # self.get_item_images()
        return item_details
