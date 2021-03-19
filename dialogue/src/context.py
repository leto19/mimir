import wikipedia, requests
from bs4 import BeautifulSoup
import sys, os, csv
from difflib import SequenceMatcher

try:
  global mimir_dir
  mimir_dir = os.environ["MIMIR_DIR"]
except KeyError:
  print('Please set the environment variable MIMIR_DIR')
  sys.exit(1)


MIN_TITLE_SIMILARITY = 0.5


def init():
  '''
  Initialises the global variables.
  '''
  global s_books
  s_books = []

  global s_book_index
  s_book_index = -1

  global confirmed_booked
  confirmed_book = None


def get_confirmed_book():
  return confirmed_book


def get_suggested_books_nqa(requested_book):
  with open(mimir_dir + 'nqa_summary_text_files/supported_books.csv', 'r') as file:
    supported_books = list(csv.reader(file))[1:] # [0] is title, [1] is author
    
    similarities = []
    for book_info in supported_books:
      similarities.append(SequenceMatcher(None, book_info[0], requested_book).ratio())
    
    closest_3 = sorted(zip(supported_books, similarities), reverse=True, key=lambda x: x[1])[:3]

    closest_3 = [x for x in closest_3 if x[1] > MIN_TITLE_SIMILARITY]

    for book_info, ratio in closest_3:
      global s_books
      s_books.append({ "title": book_info[0], "author": book_info[1] })


def get_suggested_books_wiki(requested_book):
  # Collect/store wikipedia suggestions based on utterance
  wikipedia_suggested = wikipedia.search(requested_book + " (novel)", results=3)

  #print(wikipedia_suggested)
  
  # For each of the suggestions, parse the wikipedia html to see if the
  # 'author' field exists in the info box on the page - it does for all
  # books with wikipedia pages, so this confirms the book info is correct/available
  for (i, title) in list(enumerate(wikipedia_suggested)):
    try:
      url = wikipedia.page(title, auto_suggest=False).url
      html_text = requests.get(url).text
      soup = BeautifulSoup(html_text, 'html.parser')
      info_box = soup.find_all("table", { "class": "infobox" })[0] # I think there is only ever 1
      author_data = info_box.find(lambda t: t.text.strip() == "Author").parent.select('td')
      author_name = author_data[0].text
      book_title = title.replace(" (novel)", "").replace(" (book)", "")
  
      global s_books
      s_books.append({ "title": book_title, "author": author_name })
    except Exception as e:
      pass 
        # print(e)
        # print("Suggestion {} failed.".format(i+1))


def is_book_present(user_utterance, is_nqa=True):
  '''
  Searches for the book title in narrativeQA or on wikipedia and retrieves 
  the top suggestions. Returns true if any similar books are found, false otherwise. 
  '''
  init()

  # Phrases to remove from the user utterance
  blacklist = ["i am reading", "it is called"]
  for n_gram in blacklist:
    user_utterance = user_utterance.replace(n_gram, '')
  
  if is_nqa:
    get_suggested_books_nqa(user_utterance)
  else:
    get_suggested_books_wiki(user_utterance)

  if len(s_books) == 0:
    return False

  return True


def suggest_book():
  '''
  Returns a string suggesting the next possible book from the suggested books.
  '''
  global s_book_index
  s_book_index += 1

  s_book_title = s_books[s_book_index]['title']
  s_book_author = s_books[s_book_index]['author']

  return "Is that {} by {}?".format(s_book_title, s_book_author)


def confirm_book():
  '''
  Confirms the current suggested book is correct. Returns a string (system response)
  for the transition to the "neutral" state from the "clarify" state.
  '''
  global confirmed_book
  confirmed_book = s_books[s_book_index]

  # It may be appropriate to collect/store relevant resources on the book here

  return "Great, let me know if you have any questions."


def is_suggested_book():
  '''
  Returns true if the current suggested book is the last suggested book.
  '''
  return s_book_index != (len(s_books) - 1)