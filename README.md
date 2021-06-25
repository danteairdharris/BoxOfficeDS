# Box Office Predictive Model
## Project Overview
This simple WebApp productionizes a Box Office predictive model that runs underneath it to predict the Total Box Office of a film with a mean absolute error of ~ $45 Million. Production companies and individuals can use this model to evaluate the performance of a film at the Box Office.

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
