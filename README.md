# Stock Market Game Dashboard
An alternative dashboard for the [Stock Market Game](https://www.stockmarketgame.org/) that provides easier viewing and more insights

# Overview
This program accepts a username and password, scrapes the data from the Stock Market Game site, and presents it in a lovely view. (See picture below)

![Main Overview of Dashboard](screenshots/main.png)

# Installation & Setup
First, clone the repo and install the dependencies with [pipenv](https://pipenv.readthedocs.io/en/latest/)

`pipenv install`

Start the Flask server (stocks/app,py) and it should be up and running

# Features

The top of the Dashboard has four main bubbles

- General Info: Team Name, Date Updated, and links to other sections
- Rankings: The rank held for the Region and Coordinator rankings
- Total Money: Gives a general overview of how much money is stored in stocks, shorts, and cash.
- General Stock Info: Stock Count, Top Performer, and Worst Performer; The performers have links for more detail

### Stock Breakdown

This section provides information for each stock owned. It provides

- Stock Type (Short or Long)
- Shares Owned
- Original Purchase Price
- Current Stock Price (as of yesterday's closing price)
- Unrealized Gains/Losses
- And a button to update the current stock price

An example can be seen in the photo below

![Example of Stock Breakdown](screenshots/breakdown.png)

### Recent Transactions

This section just shows the four most recent transactions from the "Transaction Notes" Page.

![Example of Recent Transactions](screenshots/recent.png)

### Realized Gains/Losses

This pulls data from the Realized Gains/Losses page. It just shows stocks you've bought, then sold, and how well you ended up doing.