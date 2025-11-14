import scrapy
from scrapy.crawler import CrawlerProcess
import re
import nltk
from nltk.tokenize import word_tokenize
import json

nltk.download('punkt')

class GutenbergSpider(scrapy.Spider):
    name = "gutenberg_spider"
    start_urls = ["https://www.gutenberg.org/ebooks/search/?query=fiction"]

    def parse(self, response):
        # Get the book links from the current page
        book_links = response.css(".booklink a::attr(href)").getall()
        for book_link in book_links[:20]:  # Limit to the first 10 book links
            yield response.follow(book_link, callback=self.parse_book)

    def parse_book(self, response):
        # Find the link with href ending in 'txt.utf-8'
        txt_link = response.css("a[href$='txt.utf-8']::attr(href)").get()
        if txt_link:
            yield response.follow(txt_link, callback=self.parse_text)

    def parse_text(self, response):
        # Extract the book text and clean it before yielding
        book_text = response.body.decode("utf-8")
        chapters = extract_chapters(book_text)

        # Check if the number of chapters is odd, if so, remove the last chapter
        while len(chapters) % 5 != 0:
            chapters.pop()

        for chapter_text in chapters:
            cleaned_text = clean_text(chapter_text)
            yield {"text": cleaned_text}

def extract_chapters(text):
    # Split the book text into chapters using the word "Chapter" as the delimiter
    chapters = re.split(r"Chapter\s+\d+", text)
    # Filter out empty chapters and trim leading/trailing spaces
    chapters = [chapter.strip() for chapter in chapters if chapter.strip()]
    return chapters

def clean_text(text):
    # Remove special characters, punctuation, and numbers
    cleaned_text = re.sub(r"[^\w\s'-]", "", text)
    cleaned_text = re.sub(r"\d+", "", cleaned_text)

    # Tokenize the text using nltk word tokenizer with custom rules
    tokens = word_tokenize(cleaned_text)
    cleaned_text = " ".join(tokens)

    return cleaned_text

def main():
    # Run the spider to get the book texts and save the cleaned texts to a JSON file
    process = CrawlerProcess(settings={
        "USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "FEED_FORMAT": "json",
        "FEED_URI": "gutenberg_texts.json",
    })
    process.crawl(GutenbergSpider)
    process.start()

if __name__ == "__main__":
    main()
