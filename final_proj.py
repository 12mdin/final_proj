from bs4 import BeautifulSoup
import requests
import json
import sqlite3
import pandas as pd
import plotly.graph_objects as go

CACHE_FNAME = 'cache.json'
CACHE_DICT = {}

API_KEY = '3f54b35ec9msh3f587a3146600ecp1af59ejsn137682d60c7c'
covid_url = 'https://covid-193.p.rapidapi.com/statistics'

DB_NAME = 'covid_stats.sqlite'


### get 3_letter iso country code ###
def build_country_info_dict():
    '''Create a dictionary that contains country names and code
    
    Parameters
    ----------
    None
    
    Return 
    ------
    dict
        key is the country names
        values is country code
    '''
    code_url = 'https://www.worldometers.info/country-codes/'
    response = requests.get(code_url)
    soup = BeautifulSoup(response.text,'html.parser')
    #make_request_with_cache(code_url, soup.prettify())


    country_code = []
    country_name = []
    country_info_dict = {}

    rows = soup.find('table').find_all('tr')
    #print(rows)
    for row in rows:
        if row.find_all('td'):
            #print(row)
            tds = row.find_all('td')
            #print(tds1)
            if not tds:
                continue
            #country_code
            code = tds[3].text.strip()
            #print(code)
            country_code.append(code)

            #country_name
            name = tds[0].text.strip()
            #print(name)
            name = name.replace('-',' ')
            if name == 'Saint Kitts & Nevis':
                name = 'Saint Kitts and Nevis'
        
            if name == 'Saint Pierre & Misquelon':
                name = 'Saint Pierre Misquelon'
            
            if name == 'Sao Tome & Principe':
                name = 'Sao Tome and Principe'
            
            if name == 'St. Vincent & Grenadines':
                name = 'St Vincent Grenadines'
            
            if name == 'Wallis & Futuna':
                name = 'Wallis and Futuna'
            
            if name == 'Czech Republic (Czechia)':
                name = 'Czechia'
            
            country_name.append(name)

    for i in range(len(country_name)):
        country_info_dict[country_name[i]]={
            'country code': country_code[i]
        }
    #print(country_info_dict)
    return country_info_dict

def make_url_request(base_url):
    '''Call the rapid api and returns a json
    
    parameters
    ----------
    base_url: str
        the url used to call the api
        
    returns
    -------
    dict
         a dict of countries 
    '''

    querystring = {"country":"United States"}
    headers = {
        'X-RapidAPI-Host': 'covid-193.p.rapidapi.com',
        'X-RapidAPI-Key': API_KEY
        }      
    response = requests.request("GET", base_url, headers=headers)
    #print(response)
    make_request_with_cache(base_url, response.json())
    return response.json()

def build_covid_dict(covid_json):
    
    all_countries = covid_json['response']
    make_request_with_cache(covid_url, all_countries)

    country_list = []
    total_cases_list = []
    total_deaths_list = []
    total_recovered_list = []
    total_test_list = []
    population_list = []

    #print(all_countries)
    for i in all_countries:
        # get country names
        country = i['country']
        if country == 'USA':
            country = 'United States'
        if country == 'S-Korea':
            country = 'South Korea'
        country = country.replace('-',' ')
        country_list.append(country)

        # get recovered cases
        recovered = i['cases']['recovered']
        if recovered == None:
            recovered = 0
        total_recovered_list.append(recovered)

        # get total
        total = i['cases']['total']
        total_cases_list.append(total)

        # get total death
        total_death = i['deaths']['total']
        if total_death == None:
            total_death = 0
        total_deaths_list.append(total_death)

        # get test
        total_test = i['tests']['total']
        if total_test == None:
            total_test = 0
        total_test_list.append(total_test)

        # get population
        pop = i['population']
        population_list.append(pop)

    covid_info = {}
    for i in range(len(country_list)):
        covid_info[country_list[i]] = {
            'population': population_list[i],
            'total case':total_cases_list[i],
            'recovered':total_recovered_list[i],
            'total death':total_deaths_list[i],
            'total test': total_test_list[i]
        }
    return covid_info

### caching ###
def open_cache():
    '''opens the caceh file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
        
    return cache_dict

def save_cache(cache_dict):
    '''saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    contents_to_write = json.dumps(cache_dict)
    cache_file = open(CACHE_FNAME, 'w')
    cache_file.write(contents_to_write)
    cache_file.close()

def make_request_with_cache(key, value):
    if key in CACHE_DICT.keys():
        print("Using cache")
        return CACHE_DICT[key]
    else:
        print('Fetching')
        CACHE_DICT[key] = value
        save_cache(CACHE_DICT)
        return CACHE_DICT[key]


### database ###
def create_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    drop_country_info_sql='DROP TABLE IF EXISTS "country_info"'
    drop_covid_cases_sql = 'DROP TABLE IF EXISTS "covid_cases"'

    create_country_info_sql = '''
        CREATE TABLE IF NOT EXISTS "country_info" (
            "Country_id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "Country_name" TEXT NOT NULL,
            "Country_code" TEXT NOT NULL
        )
    '''

    create_covid_cases_sql = '''
        CREATE TABLE IF NOT EXISTS "covid_cases" (
            "Country_id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "Country_name" TEXT NOT NULL,
            "Population" INTEGER,
            "Total_cases" INTEGER,
            "Total_recovered" INTEGER,
            "Total_deaths" INTEGER,
            "Total_tests" INTEGER

        )
    '''

    cur.execute(drop_country_info_sql)
    cur.execute(drop_covid_cases_sql)

    cur.execute(create_country_info_sql)
    cur.execute(create_covid_cases_sql)
    conn.commit()
    conn.close()

def add_country_info_sqlite():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    insert_sql = '''
        INSERT INTO country_info 
        VALUES (NULL,?,?)
    ''' 

    code_dict = build_country_info_dict()

    for k,v in code_dict.items():
        cur.execute(insert_sql,[
            k,
            v['country code']
            ]
        )
    conn.commit()
    conn.close()

def add_covid_cases_sqlite():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    insert_sql = '''
        INSERT INTO covid_cases 
        VALUES (NULL,?,?,?,?,?,?)
    ''' 

    covid_dict = build_covid_dict(make_url_request(covid_url))

    #print(covid_dict)
    for k,v in covid_dict.items():
        cur.execute(insert_sql,[
            k,
            v['population'],
            v['total case'],
            v['recovered'],
            v['total death'],
            v['total test']
            ]
        )
    conn.commit()
    conn.close()

def access_cases_table(country_name):
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    if country_name.lower() == "all":
        query = f'''
            SELECT covid_cases.Country_name, country_info.Country_code, covid_cases.Total_cases
            FROM covid_cases
            INNER JOIN country_info ON covid_cases.Country_name=country_info.Country_name
        '''

    else:
        query = f'''
            SELECT Population, Total_cases, Total_recovered, Total_deaths, Total_tests
            FROM covid_cases
            WHERE Country_name = "{country_name.title()}"
        '''

    result = cur.execute(query).fetchall()
    conn.close()
    return result

def access_info_table(country_name):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    if country_name.lower() == 'all':
        query = f'''
            SELECT *
            FROM country_info
        '''
    else:

        query = f'''
            SELECT Country_name, Country_code
            FROM country_info
            WHERE Country_name = "{country_name.title()}"
        '''
        #cur.execute(q,[country_name])
        
    result = cur.execute(query).fetchall()
    conn.close()
    return result

### create vis ###
def cases_map(user_input):
    
    
     
    if user_input.lower() == 'all':
        locations = []
        z = []
        country_name = []

        for d in access_cases_table(user_input):
            z.append(d[2])
            locations.append(d[1])
            country_name.append(d[0])


            fig = go.Figure(data=go.Choropleth(
                locations = locations,
                z = z,
                text = country_name,
                colorscale = 'Blues',
                autocolorscale=False,
                reversescale=False,
                marker_line_color='darkgray',
                marker_line_width=0.5
            ))

            fig.update_layout(
                title_text='Global Covid Cases',
                geo=dict(
                    showframe=False,
                    showcoastlines=False,
                    projection_type='equirectangular'
                )
            )

    return fig.show()

def cases_bar_chart(user_input):
    xvals = ['Total Cases', 'Total Recovered', 'Total Deaths']
    yvals = []

    for d in access_cases_table(user_input):
        yvals.append(d[1])
        yvals.append(d[2])
        yvals.append(d[3]) 

    bar_data = go.Bar(x=xvals, y=yvals)

    basic_layout = go.Layout(title=f"COVID-19 cases in {user_input.title()}",
        xaxis_title = "Types of cases",
        yaxis_title = "Number of People",
        font=dict(
            family="Roboto Slab, monospace",
            size=10,
            color="#000"
            ),
        )   

    fig = go.Figure(data=bar_data, layout=basic_layout)
    
    return fig.show()

def cases_pie_chart(user_input):
    labels = ['Recovered', 'Death', 'Unknown']
    values = []

    for d in access_cases_table(user_input):
        values.append(d[2]) #recovered
        values.append(d[3]) #death
        values.append(d[1]-d[2]-d[3]) #unknown

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    return fig.show()

def pop_test_bar_chart(user_input):
    xvals = ['Population', 'Total Tests']
    yvals = []

    for d in access_cases_table(user_input):
        yvals.append(d[0]) #population
        yvals.append(d[4]) #tests
    #print(yvals)

    bar_data = go.Bar(x=xvals, y=yvals)

    basic_layout = go.Layout(title=f"COVID-19 cases in {user_input.title()}",
        xaxis_title = "Population and Number of Tests",
        yaxis_title = "Number of People",
        font=dict(
            family="Roboto Slab, monospace",
            size=10,
            color="#000"
            ),
        )   

    fig = go.Figure(data=bar_data, layout=basic_layout)

    return fig.show()

if __name__ == "__main__":
    CACHE_DICT = open_cache()
    create_db()
    add_country_info_sqlite()
    add_covid_cases_sqlite()

    status = True
    
    while True:
        while status == True:
            final_input = input('''
Below are four graph options:

[1] Total cases across the world
[2] Detail Covid cases of a selected country
[3] Percentage of recovered and death cases
[4] Population vs. number of tests 

Please enter a number to continue or type 'exit' to quit.
''')
            
            if final_input == 'exit':
                print('Bye')
                break

            elif final_input.isnumeric():
                if final_input == '1':
                    print("Total cases across the world map")
                    final_input = 'all'
                    cases_map(final_input)

                elif final_input == '2':
                    status = False
                    while status == False:

                        print("Bar plot shows detailed Covid cases of a country")
                        country = input("Enter a country name or type 'exit' to quit or type 'back' to the last command: ")
                        if country == 'exit':
                            print('Bye')
                            break
                        elif country =='back':
                            status = True
                        else:
                            cases_bar_chart(country)

                elif final_input == '3':
                    status = False
                    while status == False:

                        print("Pie chart shows the percentage of recovered and death cases")
                        country = input("Enter a country name or type 'exit' to quit or type 'back' to the last command: ")
                        if country == 'exit':
                            print('Bye')
                            break
                        elif country == 'back':
                            status = True
                        else:
                            cases_pie_chart(country)
    
                elif final_input == '4':
                    status = False
                    while status == False:

                        print("Bar plot shows population and number of tests")
                        country = input("Enter a country name or type 'exit' to quit or type 'back' to the last command: ")
                        if country == 'exit':
                            print('Bye')
                            break
                        elif country == 'back':
                            status = True
                        else:
                            pop_test_bar_chart(country)
                    
                else:
                    pass
                
