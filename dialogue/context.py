import wikipedia, requests
from bs4 import BeautifulSoup

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

def is_book_present(user_utterance):
  '''
  Searches for the book title on wikipedia and retrieves the top suggestions.
  Returns true if any similar books are found on wikipedia, false otherwise. 
  '''
  init()

  # Phrases to remove from the user utterance
  blacklist = ["i am reading", "it is called"]
  for n_gram in blacklist:
    user_utterance = user_utterance.replace(n_gram, '')
  
  # Collect/store wikipedia suggestions based on utterance
  wikipedia_suggested = wikipedia.search(user_utterance + " (novel)", results=3)

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