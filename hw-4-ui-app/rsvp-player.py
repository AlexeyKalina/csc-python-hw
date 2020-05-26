import hashlib
import json
import os
from tkinter import filedialog, messagebox, Tk, StringVar, IntVar, Label, Menu
import chardet


class Text:
    def __init__(self, file_hash, content, position=0):
        self.file_hash = file_hash
        self._words = content.split()
        self.position = position

    def current(self):
        return self._words[self.position]

    def next(self):
        self.position += 1
        return self._words[self.position]

    def has_next(self):
        return self.position < len(self._words) - 1

    def prev(self):
        self.position -= 1
        return self._words[self.position]

    def has_prev(self):
        return self.position > 0


class Player:
    def __init__(self, history_path='history.json'):
        self.stopped = True
        self.text = None
        self._wpm_step = 10
        self._init_window()
        self._bind_handlers()
        self._load_history(history_path)

    def launch(self):
        self._tk.mainloop()
        self._update_history()
        with open(self._history_path, 'w') as outfile:
            json.dump(self._history, outfile)

    def _load_history(self, history_path):
        self._history_path = history_path
        self._history = dict()
        if os.path.isfile(history_path):
            with open(history_path, 'r') as file:
                self._history = json.load(file)

    def _init_window(self):
        self._tk = Tk()
        self._tk.title("RSVP Player")
        self._tk.geometry('500x180')
        self._word = StringVar()
        self._wpm = IntVar(value=100)
        Label(self._tk, textvariable=self._word, font=("Courier", "24")).pack(pady=50)
        Label(self._tk, text='wpm:', font=("Courier", "12")).pack()
        Label(self._tk, textvariable=self._wpm, font=("Courier", "12")).pack()
        menu_bar = Menu(self._tk)
        file_menu = Menu(menu_bar)
        file_menu.add_command(label="Open", command=self._do_open_file)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self._tk.config(menu=menu_bar)

    def _bind_handlers(self):
        self._tk.bind('<space>', self._do_space)
        self._tk.bind('<Left>', self._do_left)
        self._tk.bind('<Right>', self._do_right)
        self._tk.bind('<Up>', self._do_up)
        self._tk.bind('<Down>', self._do_down)

    def _do_up(self, _):
        self._wpm.set(self._wpm.get() + self._wpm_step)

    def _do_down(self, _):
        self._wpm.set(self._wpm.get() - self._wpm_step)

    def _do_space(self, _):
        if self.text is not None:
            self.stopped = not self.stopped
            if not self.stopped:
                self._show()

    def _do_left(self, _):
        if self.text is not None and self.stopped and self.text.has_prev():
            self._word.set(self.text.prev())

    def _do_right(self, _):
        if self.text is not None and self.stopped and self.text.has_next():
            self._word.set(self.text.next())
            self._tk.update()

    def _do_open_file(self):
        file = filedialog.askopenfilename(title="Select file for reading")
        if os.path.isfile(file):
            try:
                raw_data = open(file, 'rb').read()
                encoding = chardet.detect(raw_data)['encoding']
                content = raw_data.decode(encoding=encoding)
                self._update_history()
                position = 0
                file_hash = hashlib.sha256(raw_data).hexdigest()
                if file_hash in self._history:
                    position = self._history[file_hash]['position']
                    self._wpm.set(self._history[file_hash]['wpm'])
                self.text = Text(file_hash, content, position)
                self._word.set(self.text.current())
            except Exception:
                messagebox.showerror('Error', 'Select another file please')

    def _update_history(self):
        if self.text is not None:
            self._history[self.text.file_hash] = {
                'position': self.text.position,
                'wpm': self._wpm.get()
            }

    def _show(self):
        if self.text is not None and not self.stopped:
            if self.text.has_next():
                word = self.text.next()
                self._word.set(word)
                self._tk.after(self._calculate_delay(word), self._show)
            else:
                self.stopped = True

    LONG_WORD_LEN = 12

    def _calculate_delay(self, word):
        delay = 60_000 / self._wpm.get()
        additional_delay = delay / 2
        if len(word) > self.LONG_WORD_LEN:
            delay += additional_delay
        if word.endswith(('.', '?', '!')):
            delay += additional_delay
        return int(delay)


Player().launch()
