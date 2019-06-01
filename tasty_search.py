import functools
import itertools
import json
import re
import time
from collections import defaultdict, Counter

from flask import Flask, request

app = Flask(__name__)

index = defaultdict(list)


def get_items_upto_count(counter, n):
    data = counter.most_common()
    try:
        data[n - 1]
    except IndexError:
        return (data, {})
    val = data[n - 1][1]
    return (list(itertools.takewhile(lambda x: x[1] > val, data)),
            list(itertools.takewhile(lambda x: x[1] == val, data)))


def cleanup_text(text):
    text = re.sub(r"<[^>]*>", " ", text)
    text = re.sub(r"[^A-Za-z0-9]", " ", text)
    text = text.lower()
    return text


def tokenise(text):
    text = cleanup_text(text)
    words = text.split()
    return set(words)


@app.route("/query")
def api():
    query = request.args['text']
    words = set(cleanup_text(query).split())
    matches = []
    for word in words:
        matches.append(index.get(word, []))
    counters = [Counter(i) for i in matches]
    final_counter = functools.reduce(lambda x, y: x + y, counters)
    high_score, equal_score = get_items_upto_count(final_counter, 20)
    high_score = [score[0] for score in high_score]
    equal_score = [score[0] for score in equal_score]
    if equal_score:
        equal_score = sorted(equal_score, key=lambda x: float(x.score), reverse=True)
    reviews = high_score + equal_score
    if len(reviews) > 20:
        reviews = reviews[:20]
    reviews = [review.json for review in reviews]
    response = {'hits': len(reviews),
                'query': request.args['text'],
                'reviews': reviews}
    return json.dumps(response)


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
                review_lines = []

    for review in reviews:
        for word in review.words:
            index[word].append(review)

    for key, value in index.items():
        index[key] = sorted(value, key=lambda x: x.id)


def build_review(lines):
    productId = lines[0].split(':', 1)[1]
    userId = lines[1].split(':', 1)[1]
    profileName = lines[2].split(':', 1)[1]
    helpfulness = lines[3].split(':', 1)[1]
    score = lines[4].split(':', 1)[1]
    time = lines[5].split(':', 1)[1]
    summary = lines[6].split(':', 1)[1]
    text = lines[7].split(':', 1)[1]
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

    def __str__(self):
        return "Review id={id} summary={summary}".format(id=self.id, summary=self.summary)

    __repr__ = __str__


if __name__ == '__main__':
    print("Starting to Build index")
    start = time.time()
    build_index()
    end = time.time()
    print("index is created")
    print("took {} seconds to build index".format(end - start))
    print("starting webservice")
    app.run()
