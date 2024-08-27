from selenium import webdriver
import requests
webdriver.Chrome
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
from selenium.webdriver.chrome.service import Service
import time


import json
import os

# Global Variables
options = Options()
#options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument('log-level=3')

# Initialize the Service
service = Service(ChromeDriverManager().install())

# Initialize WebDriver without the 'desired_capabilities' argument
driver = webdriver.Chrome(service=service, options=options)


link = "https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=2,90&splitArrPitch=&autoPt=false&splitTeams=false&statType=team&statgroup=2&startDate=2024-03-01&endDate=2024-11-01&players=&filter=&groupBy=season&wxTemperature=&wxPressure=&wxAirDensity=&wxElevation=&wxWindSpeed=&position=B&sort=23,1"
'''
RHP      : https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=2&splitArrPitch=&autoPt=false&splitTeams=false&statType=team&statgroup=1&startDate=2024-03-01&endDate=2024-11-01&players=&filter=&groupBy=season&wxTemperature=&wxPressure=&wxAirDensity=&wxElevation=&wxWindSpeed=&position=B&sort=23,1
RHP DAY  : https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=2,90&splitArrPitch=&autoPt=false&splitTeams=false&statType=team&statgroup=1&startDate=2024-03-01&endDate=2024-11-01&players=&filter=&groupBy=season&wxTemperature=&wxPressure=&wxAirDensity=&wxElevation=&wxWindSpeed=&position=B&sort=23,1 
RHP NIGHT: https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=2,91&splitArrPitch=&autoPt=false&splitTeams=false&statType=team&statgroup=1&startDate=2024-03-01&endDate=2024-11-01&players=&filter=&groupBy=season&wxTemperature=&wxPressure=&wxAirDensity=&wxElevation=&wxWindSpeed=&position=B&sort=23,1
'''

'''
LHP      : https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=1&splitArrPitch=&autoPt=false&splitTeams=false&statType=team&statgroup=1&startDate=2024-03-01&endDate=2024-11-01&players=&filter=&groupBy=season&wxTemperature=&wxPressure=&wxAirDensity=&wxElevation=&wxWindSpeed=&position=B&sort=23,1
LHP DAY  : https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=1,90&splitArrPitch=&autoPt=false&splitTeams=false&statType=team&statgroup=1&startDate=2024-03-01&endDate=2024-11-01&players=&filter=&groupBy=season&wxTemperature=&wxPressure=&wxAirDensity=&wxElevation=&wxWindSpeed=&position=B&sort=23,1 
LHP NIGHT: https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=1,91&splitArrPitch=&autoPt=false&splitTeams=false&statType=team&statgroup=1&startDate=2024-03-01&endDate=2024-11-01&players=&filter=&groupBy=season&wxTemperature=&wxPressure=&wxAirDensity=&wxElevation=&wxWindSpeed=&position=B&sort=23,1
'''

# Function to generate dynamic date range
def generate_dates(days_before):
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_before)).strftime('%Y-%m-%d')
    return start_date, end_date

# Example of dynamic URL generation based on date range
start_date, end_date = generate_dates(7)  # Change 7 to 10, 14, or 30 as needed

# Navigate to the webpage
driver.get(link)
time.sleep(10)  # Adjust the sleep time if necessary
csv_xpath = '//*[@id="react-drop-test"]/div[2]/a'
csv_element = driver.find_element("xpath", csv_xpath)
driver.execute_script("arguments[0].scrollIntoView(true);", csv_element)

# Use JavaScript to click the element
driver.execute_script("arguments[0].click();", csv_element)

# Wait for the download to complete (adjust based on download speed)
time.sleep(5)

# Move the file to the desired directory
download_path = os.path.join(os.path.expanduser("~"), "Downloads")
files = os.listdir(download_path)
csv_files = [f for f in files if f.endswith('.csv')]

# Assuming the latest file is the one you just downloaded
latest_file = max([os.path.join(download_path, f) for f in csv_files], key=os.path.getctime)

# Destination path in your project
destination_path = os.path.join("C:\\Projects\\mlb_matchups\\mlb\\data", os.path.basename(latest_file))
os.rename(latest_file, destination_path)

print(f"File saved to {destination_path}")

# Close the WebDriver
driver.quit()