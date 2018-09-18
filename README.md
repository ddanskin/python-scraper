# Airfare Scraper
This command line python program scrapes airfare prices for a round-trip flight from a given origin to a given destination with dates given for departure and return flights. This project was built for educational purposes only and would run into problems with large scale use, the most likely of which would be being blocked by the website.

# To Use
Download the program. In the command line type:
`python3 scraper.py [origin airport code] [destination airport code] [depart date MM/DD/YYYY] [return date MM/DD/YYYY]`

![scraper_preview](https://user-images.githubusercontent.com/6474602/41045424-62b3a52a-6976-11e8-980c-20c901b5c36a.png)

Result file will look like this:
![scrape_data_preview](https://user-images.githubusercontent.com/6474602/41045627-babfce2e-6976-11e8-85d8-92a25b140885.png)

# Built with the following python packages
* Requests
* ArgParse 
* json 
* lxml 
* Collections

# Acknowledgements
Special thanks to Scrape Hero and Hackernoon for providing  excellent scraping tutorials

# License
MIT &copy; ddanskin
