import requests
from bs4 import BeautifulSoup as bs
import pickle
import pandas as pd
from datetime import datetime
import streamlit as st 
import seaborn as sns
import matplotlib.pyplot as plt 

st.set_page_config(layout="wide")

## Save list_movie_data in with pickle
def save_data(filename, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

## Load pickle file data 
def load_data(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
    
#function for scraping infobox
def scrape(url):
    page = requests.get(url)
    toScrape = bs(page.content, 'html.parser')
    movie_details = toScrape.find(class_='infobox vevent')
    rows = movie_details.find_all('tr') 
    movie_data = {}

    title = rows[0].find('th').get_text()
    movie_data['Title'] = title
    for i, row in enumerate(rows):
        try:
            if i <= 1:
                continue
            elif row.find('th').get_text() == 'Based on':
                continue
            elif row.find('th').get_text() == 'Starring':
                clean_tags(row)
                movie_data['Starring'] = clean(row)
                movie_data['Lead'] = movie_data['Starring'][0]
            elif 'Production' in row.find('th').get_text():
                clean_tags(row)
                movie_data['Production companies'] = clean(row)
            elif row.find('th').get_text() == 'Running time':
                clean_tags(row)
                movie_data['Running_time_min'] = clean(row)
            elif row.find('th').get_text() == 'Release date':
                clean_tags(row)
                date = clean(row).strip()
                dt = dt_conversion(date)
                movie_data['Release_date_dt'] = dt
                movie_data['Release_month'] = dt.month
            elif row.find('th').get_text() == 'Budget':
                budget = money_convert(row)
                movie_data['Budget'] = budget
            elif row.find('th').get_text() == 'Box office':
                money = money_convert(row)
                movie_data['Box_office'] = money
            else:
                clean_tags(row)
                column = row.find('th').get_text(' ', strip=True)
                data = clean(row)
                movie_data[column] = data
        except:
            pass
        
    op_rating = get_op_and_rating(title)
    movie_data['Box_office_opening'] = op_rating[0]
    movie_data['Rating'] = op_rating[1]
        
    return movie_data
    
    
    
#grab opening box office numbers and MPAA rating from Box Office Mojo given movie title
def get_op_and_rating(title):
    search_page = requests.get('https://www.boxofficemojo.com/search/?q='+title)
    search_page_content = bs(search_page.content, 'html.parser')
    search_list = search_page_content.find_all('a')
    path = ''
    for li in search_list:
        if li.get_text() == title:
            path = li['href']
            break
        elif title[:10] in li.get_text():
            path = li['href']
            break
            
    if path == '':
        path = search_list[14]['href']
    
    
    data = [None,'Unknown']
    movie_page = requests.get('https://www.boxofficemojo.com'+path)
    movie_page_content = bs(movie_page.content, 'html.parser')
    table_links = movie_page_content.find_all('a')
    for li in table_links:
        if '$' in li.get_text():
            opening_box = float(li.get_text().replace('$', '').replace(',', ''))
            data[0] = opening_box
            break
            
    spans = movie_page_content.find_all('span')
    for span in spans:
        if 'MPAA' in span.get_text():
            rating = span.find_next('span').get_text()
            data[1] = rating
            break
    return data  


#Convert date str to datetime object
def dt_conversion(date):
    patterns = ['%B %d, %Y', '%d %B %Y']
    for pat in patterns:
        try:
            return datetime.strptime(date, pat)
        except:
            pass
    return none


#remove troublesome tags
def clean_tags(content):
    t = ['sup', 'span']
    tags = content.find_all(t)
    for tag in tags:
        tag.decompose()

def money_convert(row):
    multiplier = 1
    money_str = row.find('td').get_text().replace('\xa0', ' ')
    if '£' in money_str:
        multiplier = 1.41
    elif '€' in money_str:
        multiplier = 1.21
        
        
    if 'million' in money_str:
        if '(' in money_str:
            money_str = money_str.split('(')[0].replace('$','').replace('£', '')
        if '-' in money_str:
            number = float(money_str.split('-')[0].replace('$','').replace('£', ''))
            return number * multiplier * (10**6)
        if '–' in money_str:
            number = float(money_str.split('–')[0].replace('$','').replace('£', ''))
            return number * multiplier * (10**6)
        else:
            number = float(money_str.split(' ')[0].replace('$','').replace('£', ''))
            return number * multiplier * (10**6)
    elif 'billion' in money_str:
        if '(' in money_str:
            money_str = money_str.split('(')[0].replace('$','').replace('£', '')
        if '-' in money_str:
            number = float(money_str.split('-')[0].replace('$','').replace('£', ''))
            return number * multiplier * (10**9)
        if '–' in money_str:
            number = float(money_str.split('–')[0].replace('$','').replace('£', ''))
            return number * multiplier * (10**9)
        else:
            number = float(money_str.split(' ')[0].replace('$','').replace('£', ''))
            return number * multiplier * (10**9)
    else:
        number = float(money_str.replace(',','').replace('$','').replace('£', ''))
        return number * multiplier


#function to clean data scraped from wikipedia infobox
def clean(row):
    if row.find('th').get_text() == 'Release date':
        if row.find('td').get_text()[0].isdigit() == True:
            return row.find('td').get_text().split(',')[0].replace('\xa0', ' ').strip('\n').strip(' ')  
        return row.find('td').get_text().split('(')[0].replace('\xa0', ' ').strip('\n').strip(' ')                                                                                         
    elif row.find('th').get_text() == 'Running time':
        return int(row.find('td').get_text().split(' ')[0])
    elif row.find('br'):
        return [text for text in row.find('td').stripped_strings]
    elif row.find('li'):
        return [li.get_text(' ', strip=True).replace('\xa0', ' ') for li in row.find_all('li')]
    return row.find('td').get_text()


st.sidebar.subheader('Hollywood Feature Film Box Office Predictor')
st.sidebar.write("""
    This simple WebApp productionizes a Box Office predictive model that runs underneath it to predict the Total Box Office of a film 
    with a mean absolute error of ~ $45 Million. Production companies and individuals can use this model to evaluate the performance
    of a film at the Box Office.
""")
st.sidebar.subheader('Dataset')
st.sidebar.write("""
    This self collected dataset consists of all Hollywood feature films released from 1990 through 2019 - a dataset nearing 
    5000 entries scraped from Wikipedia using the python library Beautiful Soup. All movie data is scraped from the Wikipedia
    movie infobox. The information scraped consists of movie Title,  Director, Producer, Cast, Production Companies, Release Date,
    Budget, Box Office, Opening Box Office, Rating and a few other keys. Entries without a Release Date, Budget, Box Office, or 
    Opening Box Office were dropped from the dataframe with regards to the model's training.
""")
st.sidebar.subheader('Model')
st.sidebar.write("""
    The model utilizes python library SciKit Learn to build a Random Forest Regression trained on the aforementioned dataset.
    The dataset is split into train and test sets with 20% of the data reserved for testing and 80% for training. A grid search
    was used to find the optimal parameter set for the Random Forest Regression.
""")

all_data = pd.read_csv('./Data/all_movie_data_cleaned.csv')


col1, col2 = st.beta_columns([1,1])
with col1:
    st.write("""
        # Exploratory Data Analysis
        """)
    dfsum_expander = st.beta_expander(label='Total Box Office Revenue and Movie Production Budget from 1990 - 2019', expanded=True)
    heatmap_expander = st.beta_expander(label='Correlation Heatmap of Relevant Predictors')
    lead_expander = st.beta_expander(label='Aggregate Lead actor credits by actor')
    op_month_expander = st.beta_expander(label='Aggregate Opening Box Office by release month')
    total_month_expander = st.beta_expander(label='Aggregate Total Box Office by release month')
    actor_revenue_expander = st.beta_expander(label='Aggregate Total Box Office by lead actor')
    
    with dfsum_expander:
        st.write("""
        * The amount of money spent on movie production from 1990 through 2019 was at least $189,949,985,979.  
        * The amount of Box Office Revenue earned from all Hollywood movies from 1990 through 2019 is at least $574,063,234,637.
        """)
        all_data.sum()[['Budget','Box_office']]
        
    with heatmap_expander:
        st.write("""
        * Production Budget(Budget), Total Box Office(Box_office), and Opening Box Office(Box_office_opening) all highly correlated.  
        * Run time(Running_time_min) correlates most with Production Budget but not much with other variables.
        """)
        
        # create correlation matrix
        corr_matrix = all_data[['Release_month', 'Running_time_min', 'Budget', 'Box_office_opening', 'Box_office']].corr()

        # create dataframe correlation heatmap
        fig, ax = plt.subplots(figsize=(2,2))
        cmap = sns.diverging_palette(230, 20, as_cmap=True)
        res = sns.heatmap(corr_matrix, ax=ax, cmap=cmap, vmax=.9, center=0,
                    square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot_kws={'size': 1})
        st.write(fig)
        
    with lead_expander:
        st.write("""
        * Nicholas Cage, Bruce Willis and Johnny Depp are the only actors to recieve more than 35 lead actor credits with 
            Nicholas Cage totaling 40.  
        """)
        # select actors who appeared in a WB movie more than 3 times
        actors_freq = all_data.groupby('Lead').count()
        actors = actors_freq[actors_freq['Title'] > 20]
        actors = actors[['Title']].sort_values(by=['Title'], ascending=False)

        # create seaborn barplot with x = actors, y = #of occurences
        a4_dims = (11.7, 8.27)
        fig, ax = plt.subplots(figsize=a4_dims)
        chart = sns.barplot(x=actors.index, y=actors['Title'], ax=ax)
        chart.set_xticklabels(chart.get_xticklabels(), rotation=90)
        st.write(fig)
        
    with total_month_expander:
        st.write("""
        * June is the month with the greatest aggregate Total Box Office over this 30 year period. Followed by May then December.
        * January is the month with the lowest aggregate Total Box Office over this 30 year period. Followed by February then August.
        """)
        # aggregate box office metrics by release months
        box_bymonth = all_data.groupby('Release_month').sum()[['Box_office_opening','Box_office']]
        print(box_bymonth)

        # create seaborn barplot with x = release month, y = total box office, opening box office
        a4_dims = (11.7, 8.27)
        fig, ax = plt.subplots(figsize=a4_dims)
        chart = sns.barplot(x=box_bymonth.index, y=box_bymonth['Box_office'], ax=ax)
        chart.set_xticklabels(chart.get_xticklabels(), rotation=90)
        st.write(fig)
        
    with op_month_expander:
        st.write("""
        * May is the month with the greatest aggregate Opening Box Office over this 30 year period. Followed by June then July.
        * January is the month with the lowest aggregate Opening Box Office over this 30 year period. Followed by August then October.
        """)
        a4_dims = (11.7, 8.27)
        fig, ax = plt.subplots(figsize=a4_dims)
        chart = sns.barplot(x=box_bymonth.index, y=box_bymonth['Box_office_opening'], ax=ax)
        chart.set_xticklabels(chart.get_xticklabels(), rotation=90)
        st.write(fig)
        
    with actor_revenue_expander:
        st.write("""
        * This dataframe aggregates the Total Box Office of Each Lead Actor. The value is 
        the summation of Revenue earned by each movie they have Starred in with Lead actor credit.
        * Robert Downey Jr has the highest aggregate Total Box Office at $11,609,100,000.
        """)
        actors_revenue = all_data.groupby('Lead').sum()
        actors_revenue = actors_revenue[['Box_office']].sort_values(by=['Box_office'], ascending=False)
        actors_revenue
    
with col2:
    

    st.write("""
        **How to use:** 
        
        In the input text field below , paste in a wikipedia url of the film in question. The model will predict its 
        Gross Box Office and display it. 
        
        **The model will not work if the movie has not finished its opening weekend or it does not have a release date, 
        budget, or box Office visible on Wikipedia.**
    """)
                     
    url = st.text_input('Paste Url Here')

    if url:

        test_movie_data = []
        #list_movie_data.append(scrape(#some wikipedia link to movie infobox))
        test_movie_data.append(scrape(url))

        # Delete irrelevant columns
        df = pd.DataFrame(test_movie_data) 
        while True:
            try:
                df.drop(df.columns[21], axis=1, inplace = True)
            except:
                break
        df.drop(df.columns[[2,3,6,7,8,9,10]], axis=1, inplace = True)
        df = df.set_index('Title')  

        all_data = pd.read_csv('./Data/all_movie_data_dropna.csv')
        model = load_data('./Models/RandomForestRegressionModel.pickle')

        # concat test_data and all_data to get correct dummy variables
        data = pd.concat([all_data, df])
        index = len(data.index)
        df_model = data[['Release_month', 'Budget', 'Box_office_opening', 'Box_office', 'Rating']]
        actual = data.iloc[index-1].Box_office
        df_dum = pd.get_dummies(df_model).drop('Box_office', axis=1)
        movie = df_dum.iloc[index-1]

        st.write("""
        **Prediction:**
        """)
        prediction = model.predict(movie.values.reshape(1,-1))
        st.text(str(prediction))
        st.write("""
        **Actual Current Box Office:**
        """)
        st.text(str(actual))
        
        diff = prediction - actual
        if abs(diff) < 45000000:
            st.text('This movie is performing near expectations')
        elif diff > 0: 
            st.text('This movie is performing below expectations')
        else:
            st.text('This movie is performing above expectations')