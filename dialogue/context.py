import wikipedia, requests
from bs4 import BeautifulSoup

def init():
  global s_book_index
  s_book_index = 0

  global s_book_title
  s_book_title = None

  global s_book_author
  s_book_author = None

  global CONFIRMED_BOOK_TITLE
  CONFIRMED_BOOK_TITLE = None

  global CONFIRMED_BOOK_AUTHOR
  CONFIRMED_BOOK_AUTHOR = None


def is_book_present(user_utterance):
  '''
  Searches for the book title on wikipedia and retrieves the author name 
  if match is found.
  '''

  blacklist = ["i am reading", "it is called"]
  for n_gram in blacklist:
    user_utterance = user_utterance.replace(n_gram, '')
  
  wikipedia_suggested = wikipedia.search(user_utterance + " novel", results=3)
  
  for (i, title) in list(enumerate(wikipedia_suggested)):
    try:
      url = wikipedia.page(title).url
      html_text = requests.get(url).text
      soup = BeautifulSoup(html_text, 'html.parser')
      info_box = soup.find_all("table", { "class": "infobox" })[0] # I think there is only ever 1
      author_data = info_box.find(lambda t: t.text.strip() == "Author").parent.select('td')
      author_name = author_data[0].text
      book_title = title.replace(" (novel)", "").replace(" (book)", "")
      global s_book_index
      s_book_index = i
      break
    except:
      print("Suggestion {} failed.".format(i))
      if i == len(wikipedia_suggested):
        return False

  global s_book_title 
  s_book_title = book_title
  global s_book_author
  s_book_author = author_name

  return True

def suggest_book():
  return "Is that {} by {}?".format(s_book_title, s_book_author)

def confirm_book():
  global CONFIRMED_BOOK_AUTHOR
  CONFIRMED_BOOK_AUTHOR = s_book_author

  global CONFIRMED_BOOK_TITLE
  CONFIRMED_BOOK_TITLE = s_book_title
  return "Great, let me know if you have any questions."