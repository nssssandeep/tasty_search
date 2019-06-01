# tasty_search

Required:
1. Python 3.7 (https://www.python.org/downloads/f)
2. Flask (do pip install Flask) (http://flask.pocoo.org/)

run the file tasty_search.py and it will create index and starts the server.

open google chrome and enter below link.
"http://127.0.0.1:5000/query?text=some_text" (some_text should your prefered query string)

It will give json response of list of reviews. We can use json viewer to beautify and test responses.

http://jsonviewer.stack.hu/

Sample URL's:(check proof folder)
1. http://127.0.0.1:5000/query?text=Twizzlers
2. http://127.0.0.1:5000/query?text=we were on and brought


The code contains below.
1. API endpoint to return queried data
2. tokeniser to convert text to tokens (pretty basic one. should use NLTK)
3. indexing to index data(inverted index)

takes around 0.4s to build index for 2000 reviews and <100ms to return response.
