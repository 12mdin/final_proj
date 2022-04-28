# 507 Final Project
This project aims to build a program that allow users to get more detailed information about the Covid cases in each country. 

## API Key
You can get your API key from https://rapidapi.com/api-sports/api/covid-193/

## Required Packages 
```ruby
from bs4 import BeatifulSoup
import requests
import sqlite3
import plotly.graph_objects as go
```

## Data Structure 
1. Data fetching
* Call rapidapi API for covid cases information
* Scrape WorldMeters for country code
2. Data storing
* Create a database
* Save country code into country_info table
* Save covid cases into covid_cases table
3. Presentation 
* Use plotly for vis

## Data Presentation 
The program will provide users four different vis options, users will enter number 1 to 4 to select which vis to look at. After select a vis, users are able to further select different countries to see more detailed information. 

Visualizations include:
1. A map showing the total covid cases of each country.
2. A bar plot showing the detailed cases of a selected country (total cases, total recovered, total deaths).
3. A pie chart showing the percentage of recovered cases and death cases. 
4. A bar plot showing the population and total tests of a selected country. 
