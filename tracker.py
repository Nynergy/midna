import copy
import json
import os

from tkinter import *
from tkinter import colorchooser
from tkinter import font
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.messagebox import askyesno, showerror
from PIL import ImageTk, Image, ImageEnhance

from items import Item, ProgressiveItem, ToggleItem, NumberedItem, convertJSONtoItems

COUNTS_DIR = 'img/counts/'
DARKEN_FACTOR = 0.4
IMAGE_SCALE_MIN = 10
IMAGE_SCALE_MAX = 120
TRACKER_FONT = ('Liberation Mono', 8)

FULL_SPAN = 6
HALF_SPAN = FULL_SPAN // 2
THIRD_SPAN = FULL_SPAN // 3

class Tracker:
    def __init__(self, root, state, config):
        self.root = root
        if os.name == 'posix':
            self.root.tk.call('wm', 'iconphoto', self.root._w, PhotoImage('img/midna.ico'))
        elif os.name == 'nt':
            self.root.iconbitmap('img/midna.ico')
        self.root.bind('<Up>',    lambda event: self.moveItem('N'))
        self.root.bind('<Down>',  lambda event: self.moveItem('S'))
        self.root.bind('<Left>',  lambda event: self.moveItem('W'))
        self.root.bind('<Right>', lambda event: self.moveItem('E'))

        self.state = state
        self.config = config
        self.temp_config = copy.deepcopy(self.config)
        self.image_scale = IntVar(value=config['DefaultImageSize'])

    def moveItem(self, direction):
        (x, y) = self.root.winfo_pointerxy()
        widget = self.root.winfo_containing(x, y)
        info = widget.grid_info()
        row = info['row'] - self.titleBarHeight
        column = info['column']

        items = self.state.items
        moved = False

        item_range = range(len(items))
        if row in item_range:
            if direction == 'N' and row != 0:
                temp = items[row-1][column]
                items[row-1][column] = items[row][column]
                items[row][column] = temp
                moved = True
            elif direction == 'S' and row != len(items) - 1:
                temp = items[row+1][column]
                items[row+1][column] = items[row][column]
                items[row][column] = temp
                moved = True
            elif direction == 'W' and column != 0:
                temp = items[row][column-1]
                items[row][column-1] = items[row][column]
                items[row][column] = temp
                moved = True
            elif direction == 'E' and column != len(items[row]) - 1:
                temp = items[row][column+1]
                items[row][column+1] = items[row][column]
                items[row][column] = temp
                moved = True

        if moved:
            self.constructItemButtons()

    def run(self):
        self.root.mainloop()

    def build(self):
        for child in self.root.winfo_children():
            child.destroy()

        self.constructTitleBar()
        self.constructItemButtons()
        self.constructCommandButtons()
        self.constructSliders()
        self.configureRowsAndColumns()

    def constructTitleBar(self):
        self.showTitleBar = self.config['ShowTitleBar']
        self.titleBarHeight = self.showTitleBar

        if self.showTitleBar:
            title = Label(self.root, text='midna', fg=self.config['ForegroundAlt'],
                          bg=self.config['Accent3'], font=TRACKER_FONT)
            title.grid(row=0, column=0, columnspan=FULL_SPAN, sticky='NSEW')

    def constructItemButtons(self):
        items = self.state.items
        for y in range(len(items)):
            for x in range(len(items[y])):
                item = items[y][x]
                new_image = item.get_image_path()
                new_num = self.getItemNum(item)
                self.createItemButton(new_image, x, y, new_num, item.itemText, item.isDark())

    def getItemNum(self, item):
        if isinstance(item, NumberedItem):
            if item.isNotMaxed():
                new_num = item.current_num
            else:
                new_num = -1
        else:
            new_num = None

        return new_num

    def createItemButton(self, filepath, x, y, new_num, itemText, isDark):
        img = self.constructImage(filepath, x, y, new_num, isDark)
        photo = ImageTk.PhotoImage(img)

        label = Label(self.root, image=photo)
        label.image = photo
        label.grid(row=y + self.titleBarHeight, column=x)
        label.configure(bg=self.config["Background"], activebackground=self.config["Focus"],
                        highlightthickness=0)

        button = Button(self.root, image=photo, text=itemText, compound='top')
        button.bind('<Button-1>', lambda event, x=x, y=y: self.forwardState(x, y))  # Left click
        button.bind('<Button-3>', lambda event, x=x, y=y: self.backwardState(x, y)) # Right click
        button.grid(row=y + self.titleBarHeight, column=x, sticky='NSEW')
        button.configure(fg=self.config["ForegroundAlt"], activeforeground=self.config["ForegroundAlt"],
                         bg=self.config["Background"], activebackground=self.config["Focus"],
                         highlightthickness=0, bd=0, font=TRACKER_FONT)

    def constructImage(self, filepath, x, y, new_num, isDark):
        img = Image.open(filepath)
        img = img.resize((self.image_scale.get(), self.image_scale.get()),
                         Image.ANTIALIAS)

        # Handle wallets as a special case
        if 'wallet' in filepath:
            return img

        if new_num:
            if new_num == -1:
                max_num = self.state.items[y][x].max_num
                num_img = Image.open(f'{COUNTS_DIR}{max_num}max.png')
            else:
                num_img = Image.open(f'{COUNTS_DIR}{new_num}.png')
            num_img = num_img.resize((self.image_scale.get(), self.image_scale.get()),
                                     Image.ANTIALIAS)
            img.paste(num_img, (0, 0), num_img)
        if isDark:
            darken = ImageEnhance.Brightness(img)
            img = darken.enhance(DARKEN_FACTOR)

        return img

    def forwardState(self, x, y):
        items = self.state.items
        item = items[y][x]
        item.next_state()
        new_image = item.get_image_path()
        new_num = self.getItemNum(item)
        self.createItemButton(new_image, x, y, new_num, item.itemText, item.isDark())

    def backwardState(self, x, y):
        items = self.state.items
        item = items[y][x]
        item.prev_state()
        new_image = item.get_image_path()
        new_num = self.getItemNum(item)
        self.createItemButton(new_image, x, y, new_num, item.itemText, item.isDark())

    def constructCommandButtons(self):
        items = self.state.items

        commands = [
                    {
                        'text': 'Save State',
                        'command': self.saveStateToFile,
                        'row': len(items) + self.titleBarHeight,
                        'column': HALF_SPAN * 0,
                        'span': HALF_SPAN,
                        'bg': self.config['Accent1']
                    },
                    {
                        'text': 'Load State',
                        'command': self.loadStateFromFile,
                        'row': len(items) + self.titleBarHeight,
                        'column': HALF_SPAN * 1,
                        'span': HALF_SPAN,
                        'bg': self.config['Accent1']
                    },
                    {
                        'text': 'Save Template',
                        'command': self.saveTemplate,
                        'row': len(items) + self.titleBarHeight + 1,
                        'column': THIRD_SPAN * 0,
                        'span': THIRD_SPAN,
                        'bg': self.config['Accent2']
                    },
                    {
                        'text': 'Load Template',
                        'command': self.clearTracker,
                        'row': len(items) + self.titleBarHeight + 1,
                        'column': THIRD_SPAN * 1,
                        'span': THIRD_SPAN,
                        'bg': self.config['Accent2']
                    },
                    {
                        'text': 'Clear Tracker',
                        'command': lambda: self.clearTracker(fullWipe=True),
                        'row': len(items) + self.titleBarHeight + 1,
                        'column': THIRD_SPAN * 2,
                        'span': THIRD_SPAN,
                        'bg': self.config['Accent2']
                    }
                   ]

        for button in commands:
            self.createButton(self.root, button['text'], button['command'], button['row'],
                              button['column'], button['span'], 'NSEW', self.config['Foreground'],
                              button['bg'], self.config['Foreground'], self.config['Focus'])

        self.commandRows = 2
        settings = self.createButton(self.root, 'Settings', self.openSettings,
                                     len(items) + self.titleBarHeight + self.commandRows, FULL_SPAN - 1, 1,
                                     'NSEW', self.config['ForegroundAlt'], self.config['Accent3'],
                                     self.config['Accent4'], self.config['ForegroundAlt'])

    def createButton(self, master, text, command, row, column, span, sticky, fg, bg, afg, abg):
        button = Button(master, text=text, command=command)
        button.grid(row=row, column=column, columnspan=span, sticky=sticky)
        button.configure(fg=fg, bg=bg, activeforeground=afg, activebackground=abg,
                         highlightthickness=0, bd=0, font=TRACKER_FONT)

        return button

    def saveStateToFile(self, filepath=None):
        if not filepath:
            filepath = asksaveasfilename(initialfile='state.json', defaultextension='.json',
                                         filetypes=[('JSON File','*.json'),('All Files','*.*')])
            if not filepath:
                # User canceled out of menu
                return

        tracker_state = self.state.serializeState()

        with open(filepath, 'w') as outfile:
            json.dump(tracker_state, outfile, indent=4)

    def loadStateFromFile(self):
        filepath = askopenfilename(defaultextension='.json',
                                   filetypes=[('JSON File','*.json'),('All Files','*.*')])
        if not filepath:
            return

        with open(filepath) as infile:
            tracker_state = json.load(infile)
            state_items = tracker_state['items']

            self.state.updateItems(state_items)

            self.constructItemButtons()

    def saveTemplate(self):
        answer = askyesno(title='Overwrite Template?',
                          message='Are you sure that you want to overwrite the tracker template?')

        if answer:
            self.saveStateToFile(filepath='template.json')
            tracker_state = self.state.serializeState()
            new_defaults = tracker_state['items']
            self.state.updateDefaults(new_defaults)

    def openSettings(self):
        self.settings = Toplevel(self.root)
        self.temp_config = copy.deepcopy(self.config)
        menu_rows = 0

        # Colors
        fg = self.config['Foreground']
        fa = self.config['ForegroundAlt']
        bg = self.config['Background']
        fc = self.config['Focus']
        a1 = self.config['Accent1']
        a2 = self.config['Accent2']
        a3 = self.config['Accent3']
        a4 = self.config['Accent4']

        color_header = Label(self.settings, text='Colors', fg=fa, bg=a3, font=TRACKER_FONT)
        color_header.grid(row=menu_rows, column=0, columnspan=2, sticky='NSEW')
        menu_rows += 1

        colors = [
                    { 'color': 'Foreground',    'hex': fg, 'fg': bg },
                    { 'color': 'ForegroundAlt', 'hex': fa, 'fg': bg },
                    { 'color': 'Background',    'hex': bg, 'fg': fg },
                    { 'color': 'Focus',         'hex': fc, 'fg': fg },
                    { 'color': 'Accent1',       'hex': a1, 'fg': fg },
                    { 'color': 'Accent2',       'hex': a2, 'fg': fg },
                    { 'color': 'Accent3',       'hex': a3, 'fg': fg },
                    { 'color': 'Accent4',       'hex': a4, 'fg': fg }
                 ]

        for c in colors:
            label = Label(self.settings, text=c['color'], fg=fg, bg=bg, font=TRACKER_FONT)
            label.grid(row=menu_rows, column=0, sticky='NSEW')
            button = self.createButton(self.settings, c['hex'], None, menu_rows, 1, 1, 'NSEW',
                                       c['fg'], c['hex'], c['fg'], c['hex'])
            button.bind('<Button-1>', lambda event, b=button, c=c: self.changeColor(b, c['color']))
            menu_rows += 1

        # Miscellaneous
        misc_header = Label(self.settings, text='Miscellaneous', fg=fa, bg=a3, font=TRACKER_FONT)
        misc_header.grid(row=menu_rows, column=0, columnspan=2, sticky='NSEW')
        menu_rows += 1

        # Default Image Size
        size_label = Label(self.settings, text='Default Image Size', fg=fg, bg=bg, font=TRACKER_FONT)
        size_label.grid(row=menu_rows, column=0, sticky='NSEW')
        size_text = self.temp_config['DefaultImageSize']
        self.size_entry = Entry(self.settings, font=TRACKER_FONT)
        self.size_entry.insert(0, size_text)
        self.size_entry.grid(row=menu_rows, column=1, sticky='NSEW')
        menu_rows += 1

        def validateSize(size):
            return size.isdigit() or size == ""

        val = self.settings.register(validateSize)
        self.size_entry.configure(validate='key', validatecommand=(val, '%P'))

        # Toggle Title Bar
        title_label = Label(self.settings, text='Show Title Bar', fg=fg, bg=bg, font=TRACKER_FONT)
        title_label.grid(row=menu_rows, column=0, sticky='NSEW')
        title_text = 'True' if self.temp_config['ShowTitleBar'] else 'False'
        title_button = self.createButton(self.settings, title_text, None,
                                         menu_rows, 1, 1, 'NSEW', fg, a1, fg, fc)
        title_button.bind('<Button-1>', lambda event, b=title_button: self.toggleTitleBar(b))
        menu_rows += 1

        # Apply Changes
        apply = self.createButton(self.settings, 'Apply Changes', self.applySettings,
                                  menu_rows, 0, 2, 'NSEW', fa, a4, fa, a3)
        menu_rows += 1

        # Add weights
        for i in range(menu_rows):
            self.settings.grid_rowconfigure(i, weight=1)
        for j in range(2):
            self.settings.grid_columnconfigure(j, weight=1)


    def changeColor(self, button, attr):
        (new_rgb, new_hex) = colorchooser.askcolor(color=button.cget('text'), title='Foreground Color')
        if new_hex:
            button.configure(bg=new_hex, activebackground=new_hex, text=new_hex)
            self.temp_config[attr] = new_hex
        self.settings.lift()

    def toggleTitleBar(self, button):
        new_title = 'False' if self.temp_config['ShowTitleBar'] else 'True'
        button.configure(text=new_title)
        self.temp_config['ShowTitleBar'] = False if self.temp_config['ShowTitleBar'] else True

    def applySettings(self):
        new_image_size = int(self.size_entry.get())
        if new_image_size in range(IMAGE_SCALE_MIN, IMAGE_SCALE_MAX + 1):
            self.temp_config['DefaultImageSize'] = new_image_size
            self.config = self.temp_config
            self.writeConfigToFile()
            self.settings.destroy()
            self.build()
            self.openSettings()
        else:
            showerror('Invalid Image Size',
                     f'Default Image Size value of {new_image_size} is invalid. '
                   + f'Please enter a value between {IMAGE_SCALE_MIN} and {IMAGE_SCALE_MAX}.')

    def writeConfigToFile(self):
        with open('config.json', 'w') as outfile:
            json.dump(self.config, outfile, indent=4)

    def clearTracker(self, fullWipe=False):
        if fullWipe:
            self.state.fullWipe()
        else:
            self.state.reset()
        self.build()

    def constructSliders(self):
        scale_label = Label(self.root, text='Image Size', fg=self.config["ForegroundAlt"],
                            bg=self.config["Accent3"], font=TRACKER_FONT)
        scale_label.grid(row=(len(self.state.items) + self.titleBarHeight + self.commandRows),
                         column=0, columnspan=THIRD_SPAN, sticky='NSEW')

        image_scaler = Scale(self.root, orient=HORIZONTAL, activebackground=self.config["ForegroundAlt"],
                             fg=self.config["ForegroundAlt"], bg=self.config["Accent3"], bd=0,
                             troughcolor=self.config["Accent4"], from_=IMAGE_SCALE_MIN, to=IMAGE_SCALE_MAX,
                             showvalue=0, width=21, highlightthickness=0, variable=self.image_scale)
        image_scaler.grid(row=(len(self.state.items) + self.titleBarHeight + self.commandRows),
                               column=THIRD_SPAN, columnspan=HALF_SPAN, sticky='NSEW')
        image_scaler.bind('<ButtonRelease-1>', lambda event: self.constructItemButtons())

    def configureRowsAndColumns(self):
        num_rows = len(self.state.items) + self.titleBarHeight + self.commandRows
        num_cols = len(self.state.items[0])

        for i in range(1, num_rows - 2):
            self.root.grid_rowconfigure(i, weight=1)
        for j in range(num_cols):
            self.root.grid_columnconfigure(j, weight=1)

class State:
    def __init__(self, defaults):
        self.defaults = defaults
        self.reset()

    def reset(self):
        self.items = copy.deepcopy(self.defaults)

    def fullWipe(self):
        for row in self.items:
            for item in row:
                if isinstance(item, ProgressiveItem) or isinstance(item, ToggleItem):
                    item.current_state = 0
                elif isinstance(item, NumberedItem):
                    item.current_num = 0

    def serializeState(self):
        item_states = []
        for row in self.items:
            states = []
            for item in row:
                states.append(item.get_json_state())
            item_states.append(states)
        tracker_state = { 'items': item_states }

        return tracker_state

    def updateItems(self, new_items):
        self.items = copy.deepcopy(convertJSONtoItems(new_items))

    def updateDefaults(self, new_defaults):
        self.defaults = copy.deepcopy(convertJSONtoItems(new_defaults))
