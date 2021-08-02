# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 14:05:02 2021

@author: Anand
"""

# Project : Web Scraper Using BeautifulSoup4 and requests
import requests
from bs4 import BeautifulSoup
import pandas
import argparse
import connect

parser = argparse.ArgumentParser()
parser.add_argument("--max_page_num", help="Enter the number of web pages you want to parse:", type=int)
parser.add_argument("--dbname", help="Enter the number of web pages you want to parse:", type=str)
args = parser.parse_args()

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

oyo_link = "https://www.oyorooms.com/hotels-in-hyderabad/?page="

scraped_info_list = []

Max_page_num = args.max_page_num

connect.connect(args.dbname)

for page_num in range(1, Max_page_num):

    url = oyo_link + str(page_num)

    print("GET Request for: " + url)

    req = requests.get(url, headers = headers)

    content = req.content

    soup = BeautifulSoup(content, "html.parser")

    all_hotels = soup.find_all("div", {"class":"hotelCardListing"})

    

    for hotels in all_hotels:
        hotel_dict = {}


        hotel_dict["name"] = hotels.find("h3", {"class": "listingHotelDescription__hotelName"}).text
        hotel_dict["address"] = hotels.find("span", {"itemprop": "streetAddress"}).text
        hotel_dict["price"] = hotels.find("span", {"class": "listingPrice__finalPrice"}).text
        try:
            hotel_dict["rating"] = hotels.find("span", {"class": "hotelRating__ratingSummary"}).text
        except AttributeError:
            hotel_dict["rating"] = None

        parent_amenities_element = hotels.find("div", {"class": "amenityWrapper"})
        
        amenities_list = []

        for amenity in parent_amenities_element.find_all("div", {"class": "amenityWrapper__amenity"}):
            amenities_list.append(amenity.find("span", {"class": "d-body-sm"}).text.strip())

        hotel_dict["amenities"] = ", ".join(amenities_list[:-1])

        scraped_info_list.append(hotel_dict)
        connect.insert(args.dbname, tuple(hotel_dict.values()))
        #print(hotel_name, hotel_address, hotel_price, hotel_rating, amenities_list)

dataframe = pandas.DataFrame(scraped_info_list)
print("Creating cvs file...")
dataframe.to_csv("Oyo.csv")
connect.get_info(args.dbname)