# -*- coding: utf-8 -*-
import scrapy


class SongsSpider(scrapy.Spider):
    name = "songs"
    start_urls = ['http://songmeanings.com/artist/directory']

    def parse(self, response):
        directory_links = response.css('div[id=alphabet-list] > ul > li > a::attr(href)').extract()
        for alphabet_link in directory_links:
            next_link = response.urljoin(alphabet_link)
            yield scrapy.Request(next_link, callback=self.parse_directory)

    def parse_directory(self, response):
        artist_links = response.css('div[id=artistslist] > table > tbody > tr > td > a::attr(href)').extract()
        pagination_links = response.css('div[id=pagination] > a').extract()

        for pagination_link in pagination_links:
            page_link = response.urljoin(pagination_link)
            yield scrapy.Request(page_link, callback=self.parse_directory)

        for artist_page in artist_links:
            next_link = response.urljoin(artist_page)
            yield scrapy.Request(next_link, callback=self.parse_artist)


    def parse_artist(self, response):
        songs_links = response.css('tbody[id=songslist] > tr > td > a::attr(href)').extract()
        for song_page in songs_links:
            next_link = response.urljoin(song_page)
            yield scrapy.Request(next_link, callback=self.parse_song)

    def parse_song(self, response):
        yield {
            'artist': response.css('ul.breadcrumbs > li > a::text').extract()[0],
            'song': response.css('ul.breadcrumbs > li::text').extract()[6],
            'lyric': response.css('div.holder.lyric-box::text').extract(),
            'tags': response.css('ul[id=tags-list] > li > a > strong::text').extract()
        }
