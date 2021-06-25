# Box Office Predictive Model
## Project Overview
This simple WebApp productionizes a Box Office predictive model that runs underneath it to predict the Total Box Office of a film with a mean absolute error of ~ $45 Million. Production companies and individuals can use this model to evaluate the performance of a film at the Box Office.

### How to use the Web App:
* Paste in a wikipedia url of the film in question. (Example: https://en.wikipedia.org/wiki/Avengers:_Endgame) The model will predict its Gross Box Office and display it, the current Box Office, and a performance evaluation based on those two figures.
![alt text](https://github.com/danteairdharris/BoxOfficeDS/blob/master/howto.png)

## Data Collection
I used Beautiful Soup python library to built a script to scrape the relevant data from Wikipedia and Box Office Mojo. With each movie, the following data was scraped(if applicable):
* Title
* Producer/Director
* Cast
* Language
* Country 
* Release Date
* Running Time
* Budget
* Box Office
* Opening Box Office
* MPAA Rating 

## Data Cleaning
Here are some tasks that were tackled in the cleaning process:
* Converted Release Date to python date-time object 
* Parsed Budget anf Box Office data to ensure a numeric representation of the money.
* Parsed Strings to strip whitespace and unwanted characters and compound features with multiple values into lists.
* Simple Feature Engineering to Extract release month from Release Date date-time object

## Exploratory Data Analysis
![alt text](https://github.com/danteairdharris/BoxOfficeDS/blob/master/totalbudget.png)
![alt text](https://github.com/danteairdharris/BoxOfficeDS/blob/master/releasemonth.png)
![alt text](https://github.com/danteairdharris/BoxOfficeDS/blob/master/heatmap.png)

## Model
The model utilizes python library SciKit Learn to build a Random Forest Regression and Linear Regression trained on the aforementioned dataset.
* The features passed to the model include Release Month, Budget, Box Office Opening, and Rating. 
* The dataset is split into train and test sets with 20% of the data reserved for testing and 80% for training. 
* A grid search was used to find the optimal parameter set for the Random Forest Regression.
* The model determined the RF regression performed better with a MAE of ~ $45 Million

## Productionization
Used Streamlit to quickly and cleanly deploy the model for use [Here](https://box-office-predictive-model.herokuapp.com/).
