# linkedin-job-scraper

Outline: This project consists of a python script that scrapes the latest LinkedIn job postings given specific search criteria and returns its findings in an easy to read/write CSV format. There is an additonal script included that compiles, preprocesses and analyzes the scraped data to determine the most sought after skills requested by employers from the jobs scraped as a result of running the previous script.

**WARNING:** Scraping and the use of bots on the LinkedIn platform is **NOT** allowed and a clear violation of their User Agreements. Use at your own risk as they reserve the right to **BLOCK** users if they detect any unwanted guests attempting to scrape data from their services.

## linkedin_scraper.py
Utilizes Selenium's web browser automation for ChromeWebDriver to navigate and sift through job listings and scrape relevant details out.

### Usage and Setup
1) Edit the existing ```.env``` file with your LinkedIn login credentials under which the bot will sign-in. Do **NOT** use your main credentials as there is risk involved and could result in account punishment. Creating a burner account to go along with is **HIGHLY** recommended!

2) Change the search parameters to meet your needs for the type of job postings you would like to scrape.
   ```
   keyword, location, remote, date_posted = ["machine learning engineer", "United States", "2", "r2592000"]
   ```
    remote param values: "1" = On-site, "2" = Remote, "3" = Hybrid <br>
    date_posted param values: "r86400" = Past 24 Hours, "r604800" = Past Week, "r2592000" = Past Month

Uncomment ```# chrome_options.add_argument("--headless")``` if you would like to run in headless mode otherwise you can watch the script step through each action along the way. In the ```log``` directory you can view a recap of the scripts progress as well as any errors it may have encountered. The ```data``` directory contains the end job posting results in a CSV file format named by date and time of execution.

## data_analysis.py
Concatenates files in the ```data``` directory and performs data analysis by leveraging the pandas library, visualization with seaborn/matplotlib.

