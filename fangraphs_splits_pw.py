import asyncio
import os
from playwright.async_api import async_playwright
from itertools import product
from datetime import datetime, timedelta

class FangraphsScraper:
    def __init__(self):
        # Define the download path
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.end_day = datetime.today()

    def generate_urls(self):
        # Define the variables
        handedness = {
            "RHP": 2,
            "LHP": 1,
            "ALL": ""
        }

        time_of_day = {
            "day": ",90",
            "night": ",91",
            "anytime": ""
        }

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

    async def download_csv(self, page, link_info):
        try:
            # Navigate to the webpage
            await page.goto(link_info["url"])
            await page.wait_for_timeout(3000)  # Adjust the sleep time if necessary

            # Find the CSV download button by XPath and click it
            csv_xpath = '//*[@id="react-drop-test"]/div[2]/a'
            await page.wait_for_selector(csv_xpath)
            csv_element = await page.query_selector(csv_xpath)
            await csv_element.scroll_into_view_if_needed()
            await csv_element.click()

            # Wait for the download to complete (adjust based on download speed)
            await page.wait_for_timeout(2000)

            # Get the latest downloaded CSV file
            csv_files = [f for f in os.listdir(self.download_path) if f.endswith('.csv')]
            latest_file = max([os.path.join(self.download_path, f) for f in csv_files], key=os.path.getctime)

            return latest_file

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    async def move_file(self, source, link_info):
        try:
            # Create a unique filename
            end_date = self.end_day.strftime("%Y-%m-%d")
            filename = f"{end_date}_{link_info['hand']}_{link_info['time']}_{link_info['delta']}days.csv"
            destination_path = os.path.join("C:\\Projects\\mlb_matchups\\data", filename)
            os.rename(source, destination_path)
            print(f"File saved to {destination_path}")
        except Exception as e:
            print(f"An error occurred while moving the file: {e}")

    async def scrape_and_download(self):
        # Generate the URLs with additional info
        urls_info = self.generate_urls()

        # Track failed downloads
        failed_downloads = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Scrape and download CSVs for each URL
            for link_info in urls_info:
                latest_file = await self.download_csv(page, link_info)
                if latest_file:
                    await self.move_file(latest_file, link_info)
                else:
                    # Track the failed combination
                    failed_downloads.append(link_info)

            await browser.close()

        # Summary of failed downloads
        if failed_downloads:
            print("\nSummary of failed downloads:")
            for failed in failed_downloads:
                print(f"Handedness: {failed['hand']}, Time of Day: {failed['time']}, Start Date: {failed['start_date']}, URL: {failed['url']}")
        else:
            print("All downloads completed successfully.")

# Example of usage
if __name__ == "__main__":
    # Initialize the scraper object
    scraper = FangraphsScraper()

    # Scrape and download CSVs for generated URLs
    asyncio.run(scraper.scrape_and_download())
