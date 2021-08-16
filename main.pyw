from typing import Dict
import dictionaries
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter.messagebox import showerror
import sqliter
from requests.exceptions import RequestException
from random import Random


class StartFrame(Frame):
    def __init__(self, master) -> None:
        Frame.__init__(self, master)
        f = Frame(self)
        self.img = ImageTk.PhotoImage(Image.open('icons/black_sonic_4096.png').resize((200, 200)))
        Label(f, image=self.img).pack(side=LEFT)
        Label(f, text='Fast typing', font='Helvetica 30').pack(side=LEFT)
        f.pack()
        self.dict_combo = ttk.Combobox(self,
                                       values=list(
                                           dictionaries.DICTIONARIES.keys()),
                                       state='readonly')
        self.dict_combo.set(next(dictionaries.DICTIONARIES.keys().__iter__()))
        self.dict_combo.pack(pady=10)
        start = Button(
            self,
            text='Start',
            command=lambda: self.master.show_testframe(self.dict_combo.get()))
        start.pack()
        self.headings = ['Id', 'Time', 'Dictionary', 'Speed', 'Misstakes']
        self.table = ttk.Treeview(self,
                                  columns=self.headings,
                                  displaycolumns=self.headings,
                                  selectmode='browse',
                                  show='headings')
        for i in self.headings:
            self.table.heading(i, text=i, anchor=CENTER)
            self.table.column(i, anchor=CENTER, width=100)
        for i in sqliter.get_data():
            self.table.insert('', END, values=i)
        self.scroll = Scrollbar(self, command=self.table.yview, relief=SUNKEN)
        self.table.config(yscrollcommand=self.scroll.set)
        self.scroll.pack(side=RIGHT, fill=Y, pady=5)
        self.table.pack(fill=BOTH, padx=5, pady=5)


class TestFrame(Frame):
    def __init__(self, master, type_of_dictionary) -> None:
        backgrounds = [
            '#afdce6', '#b9d478', '#bacace', '#f5d27c', '#cc5c48', '#d4a50d',
            '#fbc979', '#83699f', '#064bed'
        ]
        Frame.__init__(self, master, bg=Random().choice(backgrounds))
        self.type_of_dictionary = type_of_dictionary
        self.time_left = 5 * 60
        self.chars = 0
        self.time_passed = 1
        self.start = False
        self.pos = 0
        self.misstake = 0
        f = Frame(self)
        f.pack(pady=20)
        self.clock = Label(f, text='5:0')
        self.misstakes = Label(f, text='Misstakes: 0')
        self.speed = Label(f, text='Speed: 0')
        self.clock.pack(side=LEFT, padx=3)
        self.speed.pack(side=LEFT, padx=3)
        self.misstakes.pack(side=LEFT, padx=3)
        Frame(self).pack(pady=100)
        self.text = Text(self,
                         font='Helvetica 14',
                         background='#f5f5f5',
                         height=3)
        self.text.insert('1.0', '\n\n')
        self.text_data = dictionaries.DICTIONARIES[type_of_dictionary](
        ).get_data().split('\n')
        self.text_next_line = 3
        for i in range(min(3, len(self.text_data))):
            self.text.insert(f'{i+1}.0', self.text_data[i])
        self.text.config(state=DISABLED)
        self.text.bind('<KeyPress>', self.onpress)
        self.text.focus_set()
        self.text.tag_config('cur', background='#b0c4de')
        self.text.tag_config('red', foreground='red')
        self.text.tag_config('passed',
                             foreground='#19ff19',
                             background='#f5f5f5')
        self.text.pack()
        Frame(self).pack(pady=90)
        self.exit_button = Button(self,
                                  text='Exit',
                                  command=lambda: master.show_resultsframe(
                                      {
                                          'time': self.time_passed,
                                          'chars': self.chars,
                                          'misstake': self.misstake,
                                          'dictionary': self.type_of_dictionary
                                      }),
                                  width=8,
                                  height=2)
        self.exit_button.pack(pady=13)

    def update_clock(self):
        self.time_left -= 1
        self.time_passed += 1
        if not self.time_left:
            return self.master.show_resultsframe({
                'time':
                self.time_passed,
                'chars':
                self.chars,
                'misstake':
                self.misstake,
                'dictionary':
                self.type_of_dictionary
            })
        self.clock.config(text=f'{self.time_left // 60}:{self.time_left % 60}')
        self.speed.config(
            text=f'Speed: {int(self.chars * 60 // self.time_passed)}')
        self.clock.after(1000, self.update_clock)

    def onpress(self, event=None):
        if not self.start:
            self.update_clock()
            self.start = True
        if event.char == '':
            return
        if event.char == self.text.get(f'1.{self.pos}', f'1.{self.pos + 1}'):
            self.text.tag_remove('cur', f'1.{self.pos}', f'1.{self.pos + 1}')
            self.text.tag_remove('red', f'1.{self.pos}', f'1.{self.pos + 1}')
            self.text.tag_add('passed', f'1.{self.pos}', f'1.{self.pos + 1}')
            self.pos += 1
            self.text.tag_add('cur', f'1.{self.pos}', f'1.{self.pos + 1}')
            self.chars += 1
            self.speed.config(
                text=f'Speed: {int(self.chars * 60 // self.time_passed)}')
        else:
            self.text.tag_add('red', f'1.{self.pos}', f'1.{self.pos + 1}')
            self.misstake += 1
            self.misstakes.config(text=f'Misstakes: {self.misstake}')
        if self.text.get(f'1.{self.pos}', f'1.{self.pos + 1}') == '':
            self.pos = 0
            self.text.config(state=NORMAL)
            self.text.delete('1.0', '2.0')
            if self.text_next_line < len(self.text_data):
                self.text.insert(END, '\n')
                self.text.insert('3.0', self.text_data[self.text_next_line])
                self.text_next_line += 1
            self.text.tag_add('cur', '1.0')
            self.text.config(state=DISABLED)
            if self.text.get('1.0',
                             END).strip() == '' and self.text_next_line >= len(
                                 self.text_data):
                self.master.show_resultsframe({
                    'time':
                    self.time_passed,
                    'chars':
                    self.chars,
                    'misstake':
                    self.misstake,
                    'dictionary':
                    self.type_of_dictionary
                })


class Window(Tk):
    def __init__(self) -> None:
        Tk.__init__(self)
        self.title('Fast typing')
        self.icon = ImageTk.PhotoImage(Image.open('icons/black_sonic_24.png'))
        self.iconphoto(False, self.icon)
        self.geometry('940x579')
        self.resizable(0, 0)
        self.start = StartFrame(self)
        self.curframe = self.start
        self.curframe.pack(fill=BOTH)

    def show_startframe(self):
        if self.curframe == self.start:
            self.curframe.pack_forget()
        else:
            self.curframe.destroy()
        self.curframe = self.start
        self.curframe.pack(fill=BOTH)

    def show_testframe(self, type_of_dictionary) -> None:
        if self.curframe == self.start:
            self.curframe.pack_forget()
        else:
            self.curframe.destroy()
        try:
            self.curframe = TestFrame(self, type_of_dictionary)
            self.curframe.pack(fill=BOTH)
        except RequestException as e:
            showerror('tk', 'Can\'t connect to the server')
            self.show_startframe()

    def show_resultsframe(self, data) -> None:
        if self.curframe == self.start:
            self.curframe.pack_forget()
        else:
            self.curframe.destroy()
        self.curframe = ResultsFrame(self, data)
        self.curframe.pack(fill=BOTH)


class ResultsFrame(Frame):
    def __init__(self, master: Window, data):
        Frame.__init__(self, master)
        Frame(self).pack(pady=100)
        f = Frame(self)
        Label(f,
              text=str(int(data['chars'] * 60 // data['time'])),
              font='Helvetica 30').pack()
        Label(f, text='chars per minute').pack()
        Label(f, text=f'Misstakes: {data["misstake"]}').pack()
        Label(f, text=f'Dictionary: {data["dictionary"]}').pack()
        Button(f,
               text='OK',
               command=master.show_startframe,
               width=15,
               height=2).pack()
        f.pack(anchor=CENTER)
        sqliter.add_result(int(data['chars'] * 60 // data['time']),
                           data['misstake'], data['dictionary'])
        master.start.table.delete(*master.start.table.get_children())
        for i in sqliter.get_data():
            master.start.table.insert('', END, values=i)


if __name__ == '__main__':
    Window().mainloop()
