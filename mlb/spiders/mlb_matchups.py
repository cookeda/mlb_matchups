import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

class MlbMatchupsScraper:
    def __init__(self):
        self.matchups = []
        self.start_time = None

    async def run(self):
        self.start_time = datetime.now()
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto("https://baseballsavant.mlb.com/probable-pitchers")

            await page.wait_for_selector('#homepage-new_probable-pitchers > div.article-template > div.template__content.template--two-column__content--one')
            parent_div = await page.query_selector('#homepage-new_probable-pitchers > div.article-template > div.template__content.template--two-column__content--one')
            mod_divs = await parent_div.query_selector_all('div.mod')
            number_of_matchups = len(mod_divs)
            print(f'Number of matchups for the day: {number_of_matchups}')

            for matchup in mod_divs:
                game_info = await matchup.query_selector('div.game-info h2')
                game_info_text = await game_info.inner_text()
                away_team, home_team = map(str.strip, game_info_text.split('@'))

                date = await matchup.query_selector('span.date')
                date_text = await date.inner_text()

                time_stadium_info = await matchup.query_selector('span.time')
                time_stadium_info_text = await time_stadium_info.inner_text()
                time, stadium = map(str.strip, time_stadium_info_text.split('|'))

                preview_link_elem = await matchup.query_selector('span:nth-child(4) > a')
                preview_link = await preview_link_elem.get_attribute('href') if preview_link_elem else None
                if preview_link:
                    preview_link = page.urljoin(preview_link)

                pitchers = await matchup.query_selector_all('div.player-info')
                away_pitcher_details = pitchers[0] if len(pitchers) >= 1 else None
                home_pitcher_details = pitchers[1] if len(pitchers) >= 2 else None

                if away_pitcher_details:
                    away_pitcher_name_elem = await away_pitcher_details.query_selector('h3 a')
                    away_pitcher_name = await away_pitcher_name_elem.inner_text()
                    away_pitcher_link = await away_pitcher_name_elem.get_attribute('href')
                    away_pitcher_number_elem = await away_pitcher_details.query_selector('span.number')
                    away_pitcher_number = await away_pitcher_number_elem.inner_text()[1:]
                    away_pitcher_throws_elem = await away_pitcher_details.query_selector('span.throws')
                    away_pitcher_throws = (await away_pitcher_throws_elem.inner_text()).split(': ')[1]
                    away_stats = await self.extract_pitcher_stats(matchup, 'div.col.one')
                else:
                    away_pitcher_name = away_pitcher_link = away_pitcher_number = away_pitcher_throws = None
                    away_stats = None

                if home_pitcher_details:
                    home_pitcher_name_elem = await home_pitcher_details.query_selector('h3 a')
                    home_pitcher_name = await home_pitcher_name_elem.inner_text()
                    home_pitcher_link = await home_pitcher_name_elem.get_attribute('href')
                    home_pitcher_number_elem = await home_pitcher_details.query_selector('span.number')
                    home_pitcher_number = await home_pitcher_number_elem.inner_text()[1:]
                    home_pitcher_throws_elem = await home_pitcher_details.query_selector('span.throws')
                    home_pitcher_throws = (await home_pitcher_throws_elem.inner_text()).split(': ')[1]
                    home_stats = await self.extract_pitcher_stats(matchup, 'div.col.two')
                else:
                    home_pitcher_name = home_pitcher_link = home_pitcher_number = home_pitcher_throws = None
                    home_stats = None

                self.matchups.append({
                    'away_team': away_team,
                    'home_team': home_team,
                    'date': date_text,
                    'time': time,
                    'stadium': stadium,
                    'away_pitcher_name': away_pitcher_name,
                    'away_pitcher_link': page.urljoin(away_pitcher_link) if away_pitcher_link else None,
                    'away_pitcher_number': away_pitcher_number,
                    'away_pitcher_throws': away_pitcher_throws,
                    'away_stats': away_stats,
                    'home_pitcher_name': home_pitcher_name,
                    'home_pitcher_link': page.urljoin(home_pitcher_link) if home_pitcher_link else None,
                    'home_pitcher_number': home_pitcher_number,
                    'home_pitcher_throws': home_pitcher_throws,
                    'home_stats': home_stats,
                    'preview_link': preview_link
                })

            await browser.close()
            self.save_matchups()

    async def extract_pitcher_stats(self, matchup, col_class):
        stats = {}
        headers_elems = await matchup.query_selector_all(f'{col_class} table:nth-child(7) > thead > tr > th')
        for i, header_elem in enumerate(headers_elems):
            header_cleaned = (await header_elem.inner_text()).strip()
            stat_value_elem = await matchup.query_selector(f'{col_class} table:nth-child(7) > tbody > tr > td:nth-child({i+1})')
            stat_value = (await stat_value_elem.inner_text()).strip() if stat_value_elem else None
            stats[header_cleaned] = stat_value

        headers_elems = await matchup.query_selector_all(f'{col_class} table:nth-child(8) > thead > tr > th')
        for i, header_elem in enumerate(headers_elems):
            header_cleaned = (await header_elem.inner_text()).strip()
            stat_value_elem = await matchup.query_selector(f'{col_class} table:nth-child(8) > tbody > tr > td:nth-child({i+1})')
            stat_value = (await stat_value_elem.inner_text()).strip() if stat_value_elem else None
            stats[header_cleaned] = stat_value

        return stats

    def save_matchups(self):
        with open('matchups.json', 'w', encoding='utf-8') as f:
            json.dump(self.matchups, f, ensure_ascii=False, indent=4)

        end_time = datetime.now()
        runtime = end_time - self.start_time
        print(f'Runtime: {runtime}')
        print('Matchups saved to matchups.json')

if __name__ == "__main__":
    scraper = MlbMatchupsScraper()
    asyncio.run(scraper.run())
