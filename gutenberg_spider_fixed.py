import scrapy
import re
import nltk
from nltk.tokenize import word_tokenize
from scrapy.crawler import CrawlerProcess

# Download nltk punkt tokenizer
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class GutenbergSpider(scrapy.Spider):
    name = "gutenberg_spider"
    start_urls = ["https://www.gutenberg.org/ebooks/search/?query=fiction"]
    count = 0

    custom_settings = {
        'FEEDS': {
            'gutenberg_texts.csv': {
                'format': 'csv',
                'fields': ['Chapter', 'Text'],
                'overwrite': True,
            },
        },
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 1,  # Be nice to the server
        'CONCURRENT_REQUESTS': 1,
    }

    def parse(self, response):
        bookLinks = response.css(".booklink a::attr(href)").getall()
        # Limit to first 20 books for reasonable dataset size
        for bookLink in bookLinks[:20]:
            yield response.follow(bookLink, callback=self.parseBook)

    def parseBook(self, response):
        # Find all links with href ending in 'txt.utf-8'
        txtLink = response.css("a[href$='txt.utf-8']::attr(href)").get()
        if txtLink:
            yield response.follow(txtLink, callback=self.parseText)

    def parseText(self, response):
        try:
            bookText = response.body.decode("utf-8")
            chapters = getChapters(bookText)

            for chapterText in chapters:
                cleanedText = cleanText(chapterText)
                numWords = len(cleanedText.split())

                # Check if the chapter has at least 20 words
                if numWords >= 20:
                    self.count += 1
                    chapterData = {
                        'Chapter': self.count,
                        'Text': cleanedText,
                    }
                    yield chapterData
        except Exception as e:
            self.logger.error(f"Error processing text: {e}")

def getChapters(text):
    # Split by "Chapter" or "CHAPTER" followed by a number or Roman numeral
    chapters = re.split(r"(?:Chapter|CHAPTER)\s+(?:\d+|[IVXLCDM]+)", text)
    # Filter out very short chapters
    return [ch for ch in chapters if len(ch.strip()) > 100]

def cleanText(text):
    # Remove special characters but keep basic punctuation
    cleanedText = re.sub(r"[^\w\s'.,!?-]", "", text)
    # Remove extra numbers but keep them if they're part of words
    cleanedText = re.sub(r"\b\d+\b", "", cleanedText)
    # Remove extra whitespace
    cleanedText = re.sub(r"\s+", " ", cleanedText)
    
    # Tokenize and rejoin
    try:
        tokens = word_tokenize(cleanedText)
        cleanedText = " ".join(tokens)
    except Exception:
        # If tokenization fails, just clean whitespace
        cleanedText = cleanedText.strip()
    
    return cleanedText

def main():
    # Run the spider
    process = CrawlerProcess()
    process.crawl(GutenbergSpider)
    process.start()

if __name__ == "__main__":
    main()
