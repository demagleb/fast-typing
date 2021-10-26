import time
from tkinter import Label
from bs4 import BeautifulSoup
import requests
from PIL import ImageFont
from tkinter.filedialog import askopenfile


def format_text(text: str):
    font = ImageFont.truetype("fonts/helvetica.ttf", 14, encoding="unic")
    MAXLEN = 700
    text = text.replace('—', '-').replace('«', '"').replace('»', '"')
    text = text.splitlines(0)
    res = [[]]
    lastlen = len(res[0])
    for line in text:
        line = line.split()
        for word in line:
            sz = font.getsize(" " + word)[0]
            if lastlen == 0 or lastlen + sz < MAXLEN:
                res[-1].append(" " + word)
                lastlen += sz
            else:
                res.append([word])
                lastlen = sz - font.getsize(" ")[0]
        res.append([])
        lastlen = 0
    res = ["".join(i).strip() for i in res]

    return "\n".join(filter(lambda i: i, res))


class FileDictionary:
    def __init__(self) -> None:
        with askopenfile(mode="r", filetypes=[("Text file", "*.txt")]) as file:
            if file != None:
                self.text = file.read(5000)
            else:
                self.text = ""

    def get_data(self):
        return format_text(self.text)


class RandomTextEnglishDictionary:
    def __init__(self) -> None:
        resp = requests.get("https://randomtextgenerator.com/")
        soup = BeautifulSoup(resp.text, "lxml")
        self.text = soup.find(id="randomtext_box").text

    def get_data(self):
        return format_text(self.text)


class RandomTextRussianDictionary:
    def __init__(self) -> None:
        self.text = ''
        for _ in range(3):
            session = requests.session()
            site = session.get('https://nocover.ru/')
            site_soup = BeautifulSoup(site.text, 'lxml')
            getbook_method = site_soup.find('div', id='footer').find(
                'a', class_="dlink").get('onclick')
            bookid, passageid = (i.strip()
                                 for i in getbook_method[9:-1].split(','))
            name_page = session.post('https://nocover.ru/getname/',
                                     data={
                                         'bookid': bookid,
                                         'passageid': passageid
                                     })
            name_soup = BeautifulSoup(name_page.text, 'lxml')
            book = name_soup.find('div').text
            self.text += book + '\n'
            for i in site_soup.find('div', class_='text').find_all('p'):
                self.text += i.text + '\n'

    def get_data(self):
        return format_text(self.text)


DICTIONARIES = {
    "Random Text (english)": RandomTextEnglishDictionary,
    "Случайный текст (русский)": RandomTextRussianDictionary,
    "Text from file": FileDictionary
}
