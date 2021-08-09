# Quantitative-Momentum


## Purpose:
To identify stocks on the S&P 500 index with the highest quantitative. This algorithm identifies the stocks with the highest momentum based off 1-year, 6-month, 3-month and 1-month Price return percentiles which have been calculated using the price returns provided via IEX Cloud API. A mean percentile score is calculated, this is the value used to rank stock momentum. The top 100 stocks with the highest mean percentile scores are then sorted in the database and wriiten onto an Excel file which will appear in the program directory.


## Built with:



![image](https://user-images.githubusercontent.com/49504460/128783133-df34fd74-e23e-4d6e-b93d-b93bfe1bcc01.png)


## Getting Started:

Install any version of Python3 on any IDE of your choice(Jupyterlabs, PyCharm e.t.c)
The following libraries needed to be added to your python interpreter
Pandas 1.2.5 
scipy 1.6.2
xlsxwriter 1.4.4
requests 2.25.1

