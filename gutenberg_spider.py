import scrapy
import re
import nltk
from nltk.tokenize import word_tokenize
from scrapy.crawler import CrawlerProcess

nltk.download('punkt') ## not sure this is the correct way to import this

class GutenbergSpider(scrapy.Spider):
    name = "gutenberg_spider"
    start_urls = ["https://www.gutenberg.org/ebooks/search/?query=fiction"]
    count = 0

    custom_settings = {
        'FEEDS': {
            'gutenberg_texts.csv': {
                'format': 'csv',
                'fields': ['Chapter', 'Text'],
            },
        },
    }

    def parse(self, response):
        bookLinks = response.css(".booklink a::attr(href)").getall()
        for bookLink in bookLinks[:20]:  # Limit to first 20 books
            yield response.follow(bookLink, callback=self.parseBook)

    def parseBook(self, response):
        txtLink = response.css("a[href$='txt.utf-8']::attr(href)").get() # Find all links with href ending in 'txt.utf-8'
        if txtLink:
            yield response.follow(txtLink, callback=self.parseText)

    def parseText(self, response):
        bookText = response.body.decode("utf-8")
        chapters = getChapters(bookText)

        for chapterText in chapters:
            cleanedText = cleanText(chapterText)

            numWords = len(cleanedText.split()) # Count the number of words in the chapter


            if numWords >= 20: # Check if the number of words is at least 20

                self.count = self.count+1
                chapterData = {
                    'Chapter': self.count,
                    'Text': cleanedText,
                }

                yield chapterData

def getChapters(text):
    chapters = re.split(r"(?:Chapter|CHAPTER)\s+(?:\d+|[IVXLCDM]+)", text) # Split the book text by "Chapter" or "CHAPTER" followed by a number or Roman numeral

    return chapters

def cleanText(text):
    cleanedText = re.sub(r"[^\w\s'-]", "", text)
    cleanedText = re.sub(r"\d+", "", cleanedText) # Remove special characters and numbers

    tokens = word_tokenize(cleanedText)
    cleanedText = " ".join(tokens)

    return cleanedText

def main():
    # Run the spider
    process = CrawlerProcess()
    process.crawl(GutenbergSpider)
    process.start()

if __name__ == "__main__":
    main()
