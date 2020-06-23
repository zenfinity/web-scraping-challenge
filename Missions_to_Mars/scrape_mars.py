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
    #print(f"Headline: {article_titles[1].text} Article summary: {article_summary.text}")
    
    

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


    #Get Weather
    #------------------------------------------
    weather_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(weather_url)
    time.sleep(1)
    html_weather = browser.html
    soup_weather = BeautifulSoup(html_weather,'html.parser')

    mars_weather = ""
    mars_weathers = soup_weather.find_all('span')
    for tag in mars_weathers:
        #print(tag.text)
        if "InSight" in tag.text:
            mars_weather = tag.text
    #print(f"The weather of mars is: {mars_weather}")

    #Get Mars Facts table
    #------------------------------------------
    #Retrieve table
    facts_url = "https://space-facts.com/mars/"
    browser.visit(facts_url)
    time.sleep(1)
    tables = pd.read_html(facts_url)
    df = tables[0]

    #Format table and dump to html
    df.rename(columns={0:"Attribute",1:"Value"},inplace=True)
    df.set_index("Attribute",inplace=True)
    html_table = df.to_html(classes="table")
    html_table.replace('\n', '') #If it looks weird on the page, change to inplace=True 
    print(html_table)
    df.to_html('table.html')

    #Get Hemisphere Images
    #------------------------------------------
    url_hemispheres_start = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    #Grab titles and seperate page links from start page
    browser.visit(url_hemispheres_start)
    html_hemisphereStart = browser.html
    soup_hemisphereStart = BeautifulSoup(html_hemisphereStart,'html.parser')
    #Grab title, and remove blanks
    hemisphereImageTitles = []
    for a in soup_hemisphereStart.find_all('a',href=True, attrs={'class':'itemLink'}):
        hemisphereImageTitles.append(a.text)
    hemisphereImageTitles = list(filter(None, hemisphereImageTitles)) 
    #Grab links from a tags
    hemisphereLinks = []
    for a in soup_hemisphereStart.find_all('a',href=True, attrs={'class':'itemLink'}):
        hemisphereLinks.append(a['href'])
    #remove duplicates
    hemisphereLinks = list(dict.fromkeys(hemisphereLinks))
    #Concatenate base url to get full link
    domain_link_hemisphere = url_hemispheres_start.split("/")
    hemisphereLinks = [f"{domain_link_hemisphere[0]}//{domain_link_hemisphere[2]}{url}"  for url in hemisphereLinks ]

    #Loop through links to grab image urls there

    hemisphereImageLinks = []

    for url in hemisphereLinks:
        browser.visit(url)
        time.sleep(3)
        html_hemisphereImagePage = browser.html
        soup_hemisphereImagePage = BeautifulSoup(html_hemisphereImagePage,'html.parser')
        
        li = soup_hemisphereImagePage.find_all('li')[0]

        hemisphereImageLinks.append(li.a.get('href'))
    
    #Create list of dicts from the two separate lists
    hemisphereImages = []
    hemisphereImages = [{'title' : title, 'img_url':img} for (title,img) in zip(hemisphereImageTitles,hemisphereImageLinks)]



    #All done, gtfo
    #------------------------------------------
    # Close the browser after scraping
    browser.quit()

    # Return results
    mars_info = {'News':
                    {'Headline': article_titles[1].text,
                    'Summary': article_summary.text},
                'FeaturedImage': featured_image_url,
                'Weather': mars_weather,
                'Facts':html_table,
                'HemisphereImages':hemisphereImages
                }
    return mars_info
