import scrapy
import json
from scrapy.http import Request
from datetime import datetime

class MlbMatchupsSpider(scrapy.Spider):
    name = "mlb_matchups"
    allowed_domains = ["baseballsavant.mlb.com"]
    start_urls = ["https://baseballsavant.mlb.com/probable-pitchers"]

    def __init__(self, *args, **kwargs):
        super(MlbMatchupsSpider, self).__init__(*args, **kwargs)
        self.matchups = []
        self.start_time = None

    def start_requests(self):
        self.start_time = datetime.now()
        yield from super().start_requests()

    def parse(self, response):
        parent_div = response.css('#homepage-new_probable-pitchers > div.article-template > div.template__content.template--two-column__content--one')
        mod_divs = parent_div.css('div.mod')
        number_of_matchups = len(mod_divs)
        self.log(f'Number of matchups for the day: {number_of_matchups}')

        for matchup in mod_divs:
            game_info = matchup.css('div.game-info h2::text').get()
            away_team = game_info.split('@')[0].strip()
            home_team = game_info.split('@')[1].strip()
            date = matchup.css('span.date::text').get()
            time_stadium_info = matchup.css('span.time::text').get()
            time = time_stadium_info.split('|')[0].strip()
            stadium = time_stadium_info.split('|')[1].strip()
            preview_link = matchup.css('span:nth-child(4) > a::attr(href)').get()
            if preview_link:
                preview_link = response.urljoin(preview_link)

            pitchers = matchup.css('div.player-info')
            away_pitcher_details = pitchers[0] if len(pitchers) >= 1 else None
            home_pitcher_details = pitchers[1] if len(pitchers) >= 2 else None

            if away_pitcher_details:
                away_pitcher_name = away_pitcher_details.css('h3 a::text').get()
                away_pitcher_link = response.urljoin(away_pitcher_details.css('h3 a::attr(href)').get())
                away_pitcher_number = away_pitcher_details.css('span.number::text').get()[1:]
                away_pitcher_throws = away_pitcher_details.css('span.throws::text').get().split(': ')[1]
                away_stats = self.extract_pitcher_stats(matchup, 'div.col.one')
            else:
                away_pitcher_name = away_pitcher_link = away_pitcher_number = away_pitcher_throws = None
                away_stats = None

            if home_pitcher_details:
                home_pitcher_name = home_pitcher_details.css('h3 a::text').get()
                home_pitcher_link = response.urljoin(home_pitcher_details.css('h3 a::attr(href)').get())
                home_pitcher_number = home_pitcher_details.css('span.number::text').get()[1:]
                home_pitcher_throws = home_pitcher_details.css('span.throws::text').get().split(': ')[1]
                home_stats = self.extract_pitcher_stats(matchup, 'div.col.two')
            else:
                home_pitcher_name = home_pitcher_link = home_pitcher_number = home_pitcher_throws = None
                home_stats = None

            self.matchups.append({
                'away_team': away_team,
                'home_team': home_team,
                'date': date,
                'time': time,
                'stadium': stadium,
                'away_pitcher_name': away_pitcher_name,
                'away_pitcher_link': away_pitcher_link,
                'away_pitcher_number': away_pitcher_number,
                'away_pitcher_throws': away_pitcher_throws,
                'away_stats': away_stats,
                'home_pitcher_name': home_pitcher_name,
                'home_pitcher_link': home_pitcher_link,
                'home_pitcher_number': home_pitcher_number,
                'home_pitcher_throws': home_pitcher_throws,
                'home_stats': home_stats,
                'preview_link': preview_link
            })

    def extract_pitcher_stats(self, matchup, col_class):
        stats = {}
        headers = matchup.css(f'{col_class} table:nth-child(7) > thead > tr > th::text').getall()
        for i, header in enumerate(headers):
            header_cleaned = header.strip()
            stat_value = matchup.css(f'{col_class} table:nth-child(7) > tbody > tr > td:nth-child({i+1})::text').get()
            if stat_value:
                stat_value = stat_value.strip()
            stats[header_cleaned] = stat_value

        headers = matchup.css(f'{col_class} table:nth-child(8) > thead > tr > th::text').getall()
        for i, header in enumerate(headers):
            header_cleaned = header.strip()
            stat_value = matchup.css(f'{col_class} table:nth-child(8) > tbody > tr > td:nth-child({i+1})::text').get()
            if stat_value:
                stat_value = stat_value.strip()
            stats[header_cleaned] = stat_value

        return stats

    def close(self, reason):
        with open('matchups.json', 'w', encoding='utf-8') as f:
            json.dump(self.matchups, f, ensure_ascii=False, indent=4)

        end_time = datetime.now()
        runtime = end_time - self.start_time
        self.log(f'Runtime: {runtime}')
        self.log('Matchups saved to matchups.json')
