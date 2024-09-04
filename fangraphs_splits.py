from selenium import webdriver
import os
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from itertools import product
from datetime import datetime, timedelta

class FangraphsScraper:
    def __init__(self):
        # Setup WebDriver options
        self.options = Options()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument('log-level=3')

        # Initialize the Service and WebDriver
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

        # Define the download path
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")

    def generate_urls(self):
        # Define the variables
        handedness = {
            "all": "",
            "RHP": 2,
            "LHP": 1
        }

        time_of_day = {
            "anytime": "",
            "day": ",90",
            "night": ",91"
        }

        # Today's date and the start day ranges
        self.end_day = datetime.today()
        start_day_deltas = [7, 14, 30, 60, 90]

        # Function to generate the URL with the given parameters
        def generate_url(hand, time, start_date):
            link = "https://www.fangraphs.com/leaders/splits-leaderboards?splitArr={2}{,90}&splitArrPitch=&autoPt=false&splitTeams=false&statType=team&statgroup=2&startDate={2024-03-01}&endDate={2024-11-01}&players=&filter=&groupBy=season&wxTemperature=&wxPressure=&wxAirDensity=&wxElevation=&wxWindSpeed=&position=B&sort=23,1"
            # Replace the placeholders
            link = link.replace("{2}", f"{hand}")
            link = link.replace("{,90}", f"{time}")
            link = link.replace("{2024-03-01}", start_date.strftime("%Y-%m-%d"))
            link = link.replace("{2024-11-01}", self.end_day.strftime("%Y-%m-%d"))
            
            return link

        # Generate all combinations of handedness, time_of_day, and start_day
        url_info = []
        for hand, time, delta in product(handedness.items(), time_of_day.items(), start_day_deltas):
            start_date = self.end_day - timedelta(days=delta)
            url = generate_url(hand[1], time[1], start_date)
            url_info.append({
                "url": url,
                "hand": hand[0],
                "time": time[0],
                "start_date": start_date.strftime("%Y-%m-%d"),
                "delta": delta
            })
        
        return url_info

    def download_csv(self, link_info):
        try:
            # Navigate to the webpage
            self.driver.get(link_info["url"])
            time.sleep(3)  # Adjust the sleep time if necessary

            # Find the CSV download button by XPath and click it
            csv_xpath = '//*[@id="react-drop-test"]/div[2]/a'
            csv_element = self.driver.find_element("xpath", csv_xpath)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", csv_element)
            self.driver.execute_script("arguments[0].click();", csv_element)

            # Wait for the download to complete (adjust based on download speed)
            time.sleep(2)

            # Get the latest downloaded CSV file
            csv_files = [f for f in os.listdir(self.download_path) if f.endswith('.csv')]
            latest_file = max([os.path.join(self.download_path, f) for f in csv_files], key=os.path.getctime)

            return latest_file

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def move_file(self, source, link_info):
        try:
            # Create a unique filename
            end_date = self.end_day.strftime("%Y-%m-%d")
            filename = f"{end_date}_{link_info['hand']}_{link_info['time']}_{link_info['delta']}days.csv"
            destination_path = os.path.join("C:\\Projects\\mlb_matchups\\data", filename)
            os.rename(source, destination_path)
            print(f"File saved to {destination_path}")
        except Exception as e:
            print(f"An error occurred while moving the file: {e}")

    def scrape_and_download(self):
        # Generate the URLs with additional info
        urls_info = self.generate_urls()

        # Scrape and download CSVs for each URL
        for link_info in urls_info:
            latest_file = self.download_csv(link_info)
            if latest_file:
                self.move_file(latest_file, link_info)

    def quit(self):
        # Close the WebDriver
        self.driver.quit()

# Example of usage
if __name__ == "__main__":
    # Initialize the scraper object
    scraper = FangraphsScraper()

    # Scrape and download CSVs for generated URLs
    scraper.scrape_and_download()

    # Close the WebDriver
    scraper.quit()
