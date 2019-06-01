import itertools
import time
from collections import defaultdict

from flask import Flask, request

app = Flask(__name__)

index = defaultdict(list)


def tokenise(words):
    return []


@app.route("/query")
def api():
    query = request.args['text']
    words = query.split()
    return "Success!"


def build_index():
    global index
    reviews = []
    with open("review_data.txt") as f:
        review_lines = []
        file_index = 0
        for line in f:
            file_index += 1
            review_lines.append(line)
            if file_index == 9:
                review = build_review(review_lines)
                reviews.append(review)
                file_index = 0

    for review in reviews:
        for word in review.words:
            index[word].append(review)

    for key, value in index.items():
        index[key] = sorted(value, key=lambda x: x.id)


def build_review(lines):
    productId = lines[0].split(':')[1]
    userId = lines[1].split(':')[1]
    profileName = lines[2].split(':')[1]
    helpfulness = lines[3].split(':')[1]
    score = lines[4].split(':')[1]
    time = lines[5].split(':')[1]
    summary = lines[6].split(':')[1]
    text = lines[7].split(':')[1]
    review = Review(productId, userId, profileName, helpfulness, score, time, summary, text)
    return review


class Review(object):
    newid = iter(itertools.count())

    def __init__(self, productId, userId, profileName, helpfulness, score, time, summary, text):
        self.id = next(Review.newid)
        self.productId = productId.lstrip()
        self.userId = userId.lstrip()
        self.profileName = profileName.lstrip()
        self.helpfulness = helpfulness.lstrip()
        self.score = score.lstrip()
        self.time = time.lstrip()
        self.summary = summary.lstrip()
        self.text = text.lstrip()
        self._words = None

    @property
    def json(self):
        json = {
            "product/productId": self.productId,
            "review/userId": self.userId,
            "review/profileName": self.profileName,
            "review/helpfulness": self.helpfulness,
            "review/score": self.score,
            "review/time": self.time,
            "review/summary": self.summary,
            "review/text": self.text
        }
        return json

    @property
    def words(self):
        if self._words:
            return self._words
        tokens = tokenise(self.text)
        self._words = tokens
        return self._words


if __name__ == '__main__':
    print("Starting to Build index")
    start = time.time()
    build_index()
    end = time.time()
    print("index is created")
    print("took {} seconds to build index".format(end - start))
    print("starting webservice")
    app.run()
