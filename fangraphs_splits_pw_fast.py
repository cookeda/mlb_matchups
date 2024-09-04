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
        handedness = {"RHP": 2, "LHP": 1, "ALL": ""}
        time_of_day = {"day": ",90", "night": ",91", "anytime": ""}
        start_day_deltas = [7, 14, 30, 60, 90]

        def generate_url(hand, time, start_date):
            link = ("https://www.fangraphs.com/leaders/splits-leaderboards?splitArr={2}{,90}"
                    "&splitArrPitch=&autoPt=false&splitTeams=false&statType=team&statgroup=2"
                    "&startDate={2024-03-01}&endDate={2024-11-01}&players=&filter=&groupBy=season"
                    "&wxTemperature=&wxPressure=&wxAirDensity=&wxElevation=&wxWindSpeed="
                    "&position=B&sort=23,1")
            link = link.replace("{2}", f"{hand}")
            link = link.replace("{,90}", f"{time}")
            link = link.replace("{2024-03-01}", start_date.strftime("%Y-%m-%d"))
            link = link.replace("{2024-11-01}", self.end_day.strftime("%Y-%m-%d"))
            return link

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

    async def close_interfering_dialogs(self, page):
        try:
            # Check for and close any dialogs that might be blocking
            close_button = await page.query_selector('button[aria-label="Close"]')
            if close_button:
                await close_button.click()
                await page.wait_for_timeout(500)  # Give it a moment to close
        except:
            pass

    async def download_csv(self, page, link_info):
        try:
            await page.goto(link_info["url"])
            await self.close_interfering_dialogs(page)
            csv_xpath = '//*[@id="react-drop-test"]/div[2]/a'
            await page.wait_for_selector(csv_xpath)

            # Use JavaScript to click the element directly
            await page.evaluate('''document.querySelector('//*[@id="react-drop-test"]/div[2]/a').click()''')
            
            await page.wait_for_download()  # Ensure download is complete
            csv_files = [f for f in os.listdir(self.download_path) if f.endswith('.csv')]
            latest_file = max([os.path.join(self.download_path, f) for f in csv_files], key=os.path.getctime)
            return latest_file

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    async def move_file(self, source, link_info):
        try:
            end_date = self.end_day.strftime("%Y-%m-%d")
            filename = f"{end_date}_{link_info['hand']}_{link_info['time']}_{link_info['delta']}days.csv"
            destination_path = os.path.join("C:\\Projects\\mlb_matchups\\data", filename)
            os.rename(source, destination_path)
            print(f"File saved to {destination_path}")
        except Exception as e:
            print(f"An error occurred while moving the file: {e}")

    async def scrape_and_download(self):
        urls_info = self.generate_urls()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            for link_info in urls_info:
                latest_file = await self.download_csv(page, link_info)
                if latest_file:
                    await self.move_file(latest_file, link_info)
                else:
                    print(f"Failed to download for {link_info['url']}")

            await browser.close()

# Example of usage
if __name__ == "__main__":
    scraper = FangraphsScraper()
    asyncio.run(scraper.scrape_and_download())
