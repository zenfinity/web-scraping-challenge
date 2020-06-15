from splinter import Browser
from bs4 import BeautifulSoup
import requests
import os
import re
import pandas as pd
import time


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape_info():
    browser = init_browser()

    

    #Get first news headline and summary text
    #------------------------------------------
    # URL of page to be scraped
    url = "https://mars.nasa.gov/news"

    browser.visit(url)

    time.sleep(1)

    html = browser.html

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(html,'html.parser')

    article_titles = []
    for div in soup.find_all('div', attrs={'class':'content_title'}):
        article_titles.append(div.find('a'))
    
    article_summary = soup.find('div', attrs={'class': 'article_teaser_body'})
    print(f"Headline: {article_titles[1].text} Article summary: {article_summary.text}")
    
    # Close the browser after scraping
    browser.quit()

    #Get Featured Image
    #------------------------------------------

    url_featured_image = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url_featured_image)
    time.sleep(1)
    html_featured_image = browser.html
    soup_featured_image = BeautifulSoup(html_featured_image,'html.parser')

    #Need to grab the url from the src tag of the wallpaper, then format to a full url
    details_link = soup_featured_image.find('article', class_='carousel_item')
    details_link_parsed = details_link['style'][22:-1].strip(')').strip("'")
    domain_link = url_featured_image.split("/")
    featured_image_url = f"{domain_link[0]}//{domain_link[2]}{details_link_parsed}"

    # Return results
    mars_info = {'News':
                    {'Headline': article_titles[1].text,
                    'Summary': article_summary.text},
                'FeaturedImage': featured_image_url
                }
    return mars_info
