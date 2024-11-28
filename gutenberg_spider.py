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
            'gutenberg_texts_2.csv': {
                'format': 'csv',
                'fields': ['Paragraph', 'Text'],
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
        paragraphs = getParagraphs(bookText)  ## Modify: Split the book text into paragraphs

        for paragraphText in paragraphs:
            cleanedText = cleanText(paragraphText)

            numWords = len(cleanedText.split()) # Count the number of words in the paragraph

            if numWords >= 20: # Check if the number of words is at least 20

                self.count = self.count+1
                paragraphData = {
                    'Paragraph': self.count,
                    'Text': cleanedText,
                }

                yield paragraphData

def getParagraphs(text):
    paragraphs = re.split(r'\n\s*\n', text)  ## Modify: Split the text into paragraphs based on two or more newline characters
    return paragraphs

def cleanText(text):
    cleanedText = re.sub(r"[^\w\s'-]", "", text)
    cleanedText = re.sub(r"\d+", "", cleanedText) # Remove special characters and numbers
    cleanedText = cleanedText.replace('_', ' ')      # Remove underscores
    cleanedText = cleanedText.replace('--', ' ')      # Remove --


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
