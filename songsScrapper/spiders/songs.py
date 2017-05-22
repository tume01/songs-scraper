# -*- coding: utf-8 -*-
import scrapy


class SongsSpider(scrapy.Spider):
    name = "songs"
    start_urls = ['http://songmeanings.com/artist/directory']
    visited_urls = []

    def parse(self, response):
        directory_links = response.css('div[id=alphabet-list] > ul > li > a::attr(href)').extract()
        for alphabet_link in directory_links:
            next_link = response.urljoin(alphabet_link)
            if next_link not in self.visited_urls:
                self.visited_urls.append(next_link)
                yield scrapy.Request(next_link, callback=self.parse_directory)

    def parse_directory(self, response):
        artist_links = response.css('div[id=artistslist] > table > tbody > tr > td > a::attr(href)').extract()
        pagination_links = response.css('div[id=pagination] > a::attr(href)').extract()
        print(pagination_links)
        for pagination_link in pagination_links:
            page_link = response.urljoin(pagination_link)
            if page_link not in self.visited_urls:
                self.visited_urls.append(page_link)
                yield scrapy.Request(page_link, callback=self.parse_directory)

        for artist_page in artist_links:
            next_link = response.urljoin(artist_page)
            if next_link not in self.visited_urls:
                self.visited_urls.append(next_link)
                yield scrapy.Request(next_link, callback=self.parse_artist)


    def parse_artist(self, response):
        songs_links = response.css('tbody[id=songslist] > tr > td > a::attr(href)').extract()
        songs_names = response.css('tbody[id=songslist] > tr > td > a::text').extract()
        user_info_list = response.css('ul.song-info > li > a::text').extract()
        genre = ""
        song_name = ""

        if len(user_info_list) > 1:
            genre = user_info_list[1]

        for index in range(len(songs_links)):
            if index % 2 is 0:
                song_page = songs_links[index]
                song_name = songs_names[index]
                next_link = response.urljoin(song_page)
                if next_link not in self.visited_urls:
                    self.visited_urls.append(next_link)
                    yield scrapy.Request(next_link, callback=self.parse_song, meta={'title': song_name, 'genre': genre})

    def parse_song(self, response):
        tags = response.css('ul[id=tags-list] > li > a > strong::text').extract()
        if len(tags) > 0:
            yield {
                'artist': response.css('ul.breadcrumbs > li > a::text').extract_first(),
                'title': response.meta['title'],
                'lyric': response.css('div.holder.lyric-box::text').extract(),
                'tags': tags,
                'genre': response.meta['genre'],
                'url': response.url,
                'album': response.css('li[id=bread_albums] > a::text').extract_first(),
                'points': response.css('div.total_votes::text').extract_first(),
                'comments': response.css('ul.comments-list > li > div > div.text::text').extract(),
            }