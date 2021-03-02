# import numpy as np
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import validators


class landing_page():
    def __init__(self, URL):
        self.url = URL

    def setup(self):
        options = Options()
        options.add_argument('--headless')
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        try:
            self.driver = webdriver.Chrome(chrome_options=options)
        except:
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        print('starting the browser')

    def close(self):
        self.driver.quit()

    def fetch_landing_page(self):
        self.driver.get(self.url)
        print(f'Browsing: {self.url}')

    def get_topic_links(self):
        return [(x.get_attribute('href'), x.text) for x in self.driver.find_elements_by_class_name("subject")]


class subject_page():
    def __init__(self, topic, start_url):
        self.topic = topic
        self.start_url = start_url
        self.page_visited = []
        self.conversation_data = []

    def setup(self):
        options = Options()
        options.add_argument('--headless')
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        try:
            self.driver = webdriver.Chrome(ChromeDriverManager(), chrome_options=options)
        except:
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        print(f'Getting data for subject: {self.topic}')

    def close(self):
        self.driver.quit()

    def goto_page(self, url):
        print(f"Going to page: {url}")
        self.driver.get(url)
        self.page_visited.append(url)

    def next_page_exists(self):
        nav_pages = set(
            [element.get_attribute('href') for element in self.driver.find_elements_by_class_name('navPages')])
        next_url = list(nav_pages.difference(self.page_visited))
        if (len(next_url != 0) & validators.url(next_url[0])):
            return next_url[0]
        else:
            return False
        # TODO: Add a function to check if the next page exists
        # TODO: Logic -> Get all the pagelinks as a set.
        # Remove all the links that is already on page_visited. Go to the first link on the page_visited.

    def parse_page(self, page):
        pass

    def get_conversation_data(self):
        self.goto_page(url=self.start_url)
        self.conversation_data.append(self.parse_page(self.driver.page_source))
        next_page_url = self.next_page_exists()
        while validators.url(next_page_url):
            self.goto_page(next_page_url)
            self.conversation_data.append(self.parse_page(self.driver.page_source))
            next_page_url = self.next_page_exists()
        # TODO: Parse the current page to see if there exists the next page
        pass


if __name__ == "__main__":
    URL = "http://www.legalserviceindia.com/lawforum/"
    lawforum = landing_page(URL)
    lawforum.setup()
    lawforum.fetch_landing_page()
    subject_links = lawforum.get_topic_links()
    lawforum.close()
    for link, topic in subject_links:
        subject = subject_page(topic=topic, start_url=link)
        subject.setup()
        # TODO: return a dictionary in the format {"q":"some text","a":["answer 1","answer 2"...]}
        subject.get_conversation_data()
        subject.close()

        # TODO: Initialize subject page, extract the data, move to the next page
        pass
