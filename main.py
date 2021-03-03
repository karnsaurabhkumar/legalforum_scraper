# import numpy as np
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
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
            self.driver = webdriver.Chrome(options=options)
        except:
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        print('starting the browser')

    def close(self):
        self.driver.quit()

    def fetch_landing_page(self):
        self.driver.get(self.url)
        print(f'Browsing: {self.url}')

    def get_topic_links(self):
        return [(x.get_attribute('href'), x.text) for x in self.driver.find_elements_by_class_name("subject")]


def validate_url(url):
    return (validators.url(url)) & ('?' not in url)


class subject_page():
    def __init__(self, topic, start_url):
        self.topic = topic
        self.start_url = start_url
        self.page_visited = []
        self.page_not_visited = []

    def setup(self):
        options = Options()
        options.add_argument('--headless')
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        try:
            self.driver = webdriver.Chrome(ChromeDriverManager(), options=options)
        except:
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.driver.get(self.start_url)
        self.page_visited.append(self.start_url)
        for page_url in self.nav_pages():
            self.page_not_visited.append(page_url)
        print(f'Getting data for subject: {self.topic}')

    def close(self):
        self.driver.quit()

    def goto_page(self, url):
        print(f"Going to page: {url}")
        self.driver.get(url)
        self.page_visited.append(url)
        self.page_visited = list(dict.fromkeys(self.page_visited))

    def nav_pages(self):
        pages = [element.get_attribute('href') for element in self.driver.find_elements_by_class_name('navPages')]
        return pages

    def next_page(self):
        nav_pages = self.nav_pages()
        if len(nav_pages) != 0:
            next_link = list(set(nav_pages) - set(self.page_visited))[0]
            return next_link
        else:
            return False

    def fetch_links(self):
        self.setup()
        while True:
            if validate_url(self.next_page()):
                self.goto_page(self.next_page())
            else:
                break

        self.close()
        return self.page_visited


class get_post_data():
    def __init__(self, start_url):
        self.start_url = start_url
        self.page_visited = []
        self.conversation_data = []

    def fetch_dat(self, driver):
        driver.get(self.start_url)
        dat = [element.text for element in driver.find_elements_by_class_name('inner')]
        self.conversation_data.append(dat)
        return dat


if __name__ == "__main__":
    URL = "http://www.legalserviceindia.com/lawforum/"
    lawforum = landing_page(URL)
    lawforum.setup()
    lawforum.fetch_landing_page()
    subject_links = lawforum.get_topic_links()
    lawforum.close()

    link, topic = subject_links[0]
    subject = subject_page(topic=topic, start_url=link)
    print(len(subject.fetch_links()))
