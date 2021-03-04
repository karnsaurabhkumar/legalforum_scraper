# import numpy as np
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import logging
import validators
import chromedriver_binary

logging.basicConfig(filename='run.log', encoding='utf-8', level=logging.INFO)


class landing_page():
    def __init__(self, URL):
        self.url = URL

    def setup(self):
        options = Options()
        options.add_argument('--headless')
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)
        print('starting the browser')

    def close(self):
        self.driver.quit()

    def fetch_landing_page(self):
        self.driver.get(self.url)
        print(f'Browsing: {self.url}')

    def get_topic_links(self):
        return [(x.get_attribute('href'), x.text) for x in self.driver.find_elements_by_class_name("subject")]


def validate_url(url):
    return (validators.url(url)) and ('?' not in url)


class subject_page():
    def __init__(self, topic, start_url):
        self.topic = topic
        self.start_url = start_url
        self.page_visited = []
        self.page_not_visited = []
        self.post_urls = []

    def setup(self):
        options = Options()
        options.add_argument('--headless')
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)

        self.goto_page(self.start_url)
        self.page_visited.append(self.start_url)
        for page_url in self.nav_pages():
            self.page_not_visited.append(page_url)
        print(f'Getting data for subject: {self.topic}')

    def close(self):
        self.driver.quit()

    def goto_page(self, url):
        print(f"Going to page: {url}")
        self.driver.get(url)
        if '.php?' not in url:
            post_links = self.get_post_url()
            for post_link in post_links:
                self.post_urls.append(post_link)
        else:
            self.post_urls.append(url)
        self.page_visited.append(url)
        self.page_visited = list(dict.fromkeys(self.page_visited))

    def nav_pages(self):
        pages = [element.get_attribute('href') for element in self.driver.find_elements_by_class_name('navPages')]
        return pages

    def get_post_url(self):
        preview_elements = self.driver.find_elements_by_class_name('preview')
        return [element.find_element_by_tag_name('a').get_attribute('href') for element in preview_elements]

    def fetch_links(self):
        self.setup()
        valid_links = list(set(self.page_not_visited) - set(self.page_visited))
        c = 0
        while valid_links:
            self.goto_page(valid_links[0])
            logging.info(valid_links[0])
            for page_url in self.nav_pages():
                self.page_not_visited.append(page_url)
            self.page_not_visited = list(dict.fromkeys(self.page_not_visited))
            valid_links = list(set(self.page_not_visited) - set(self.page_visited))
            if c % 10 == 0:
                self.driver.close()
                self.setup()
            c += 1

        self.close()
        return self.post_urls


if __name__ == "__main__":
    URL = "http://www.legalserviceindia.com/lawforum/"
    lawforum = landing_page(URL)
    lawforum.setup()
    lawforum.fetch_landing_page()
    subject_links = lawforum.get_topic_links()
    lawforum.close()

    options = Options()
    options.add_argument('--headless')
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    for link, topic in subject_links:
        subject = subject_page(topic=topic, start_url=link)
        subject_post_links = subject.fetch_links()
        print(f'Links fetched. Total count: {len(subject_post_links)}')
        print(f'fetching conversation data now!')
        driver = webdriver.Chrome(options=options)
        logging.info(topic)
        for i, url in enumerate(subject_post_links):
            print(f'{100.0*i/len(subject_post_links)}%', end='\r', flush=True)
            driver.get(url)
            dat = [element.text for element in driver.find_elements_by_class_name('inner')]
            logging.info(dat)
        driver.quit()
        print(f'Fetched data for {topic}')
