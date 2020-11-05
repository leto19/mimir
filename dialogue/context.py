import wikipedia, requests
from bs4 import BeautifulSoup

def init():
  global s_books
  s_books = []

  global s_book_index
  s_book_index = -1

  global confirmed_booked
  confirmed_book = None


def is_book_present(user_utterance):
  '''
  Searches for the book title on wikipedia and retrieves the author name 
  if match is found.
  '''
  init()

  blacklist = ["i am reading", "it is called"]
  for n_gram in blacklist:
    user_utterance = user_utterance.replace(n_gram, '')
  
  wikipedia_suggested = wikipedia.search(user_utterance + " (novel)", results=3)

  print(wikipedia_suggested)
  
  for (i, title) in list(enumerate(wikipedia_suggested)):
    try:
      url = wikipedia.page(title).url
      html_text = requests.get(url).text
      soup = BeautifulSoup(html_text, 'html.parser')
      info_box = soup.find_all("table", { "class": "infobox" })[0] # I think there is only ever 1
      author_data = info_box.find(lambda t: t.text.strip() == "Author").parent.select('td')
      author_name = author_data[0].text
      book_title = title.replace(" (novel)", "").replace(" (book)", "")
      
      global s_books
      s_books.append({ "title": book_title, "author": author_name })
    except Exception as e: 
      print(e)
      print("Suggestion {} failed.".format(i+1))

  if len(s_books) == 0:
    return False

  print(s_books)

  return True


def suggest_book():
  global s_book_index
  s_book_index += 1

  s_book_title = s_books[s_book_index]['title']
  s_book_author = s_books[s_book_index]['author']

  return "Is that {} by {}?".format(s_book_title, s_book_author)


def confirm_book():
  global confirmed_book
  confirmed_book = s_books[s_book_index]

  # It may be appriate to collect relevant resources on the book here

  return "Great, let me know if you have any questions."


def is_suggested_book():
  return s_book_index != (len(s_books) - 1)