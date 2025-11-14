import scrapy
import re
import nltk
from nltk.tokenize import word_tokenize
from scrapy.crawler import CrawlerProcess
import gensim
from gensim import corpora
from gensim.models import LdaModel
from nltk import pos_tag, ne_chunk
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer




nltk.download('punkt') ## not sure this is the correct way to import this

class GutenbergSpider(scrapy.Spider):
    name = "gutenberg_spider"
    start_urls = ["https://www.gutenberg.org/ebooks/search/?query=fiction"]
    count = 0

    custom_settings = {
        'FEEDS': {
            'gutenberg_texts.csv': {
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
        txtLink = response.css("a[href$='txt.utf-8']::attr(href)").get()
        subjects = response.css("td[property='dcterms:subject'] a::text").getall()  # Extract subjects
        if txtLink:
            yield response.follow(txtLink, callback=self.parseText, meta={'subjects': subjects})



    def parseText(self, response):
        bookText = response.body.decode("utf-8")
        paragraphs = getParagraphs(bookText)
        subjects = response.meta['subjects']

        # Tokenize and preprocess the paragraphs
        tokenized_paragraphs = [cleanText(paragraph).split() for paragraph in paragraphs]

        # Create a dictionary and a corpus
        dictionary = corpora.Dictionary(tokenized_paragraphs)
        corpus = [dictionary.doc2bow(paragraph) for paragraph in tokenized_paragraphs]

        # Perform LDA topic modeling
        num_topics = 3  # Choose the number of topics you want
        lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary)

        # Get the topics and NER entities for each paragraph
        paragraph_data = []
        for idx, paragraphText in enumerate(paragraphs):
            cleanedText = cleanText(paragraphText)
            numWords = len(cleanedText.split())

            if numWords >= 20:
                tokenized_paragraph = word_tokenize(cleanedText)
                pos_tags = pos_tag(tokenized_paragraph)
                ner_entities = ne_chunk(pos_tags)

                # Sentiment analysis
                sentiment_analyzer = SentimentIntensityAnalyzer()
                sentiment_scores = sentiment_analyzer.polarity_scores(cleanedText)

                self.count = self.count + 1
                paragraphData = {
                    'Paragraph': self.count,
                    'Text': cleanedText,
                    'Topic': subjects,
                    'LDA_Topics': lda_model.get_document_topics(corpus[idx]),
                    'NER_Entities': ner_entities,
                    'Sentiment_Score': sentiment_scores['compound']  # Add the sentiment score
                }
                paragraph_data.append(paragraphData)


        for data in paragraph_data:
            yield data



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
