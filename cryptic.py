'''
Cryptic

github.com/Egsagon/cryptic
'''

CONFIG = './conf.json'
INSTALL = False

import os
import sys
import json
import random

# Install modules if needed
if INSTALL:
    py = sys.executable
    os.system(py + ' -m pip install Pillow tk fast_file_encryption')

from pathlib import Path
from PIL import Image, ImageTk

import tkinter as tk
import tkinter.messagebox as tkmb
import tkinter.filedialog as tkfd

import fast_file_encryption as ffe


class App(tk.Tk):
    
    def __init__(self, key: str = None) -> None:
        '''
        Initialises the app.
        '''
        
        # Create the window
        super().__init__()
        self.title('Cryptic')
        self.size_ratio()
        self.config(bg = '#000')
        
        # Bindings
        self.bind('<Left>', self.next)
        self.bind('<Right>', self.prev)
        self.bind('<MouseWheel>', self.wheel)
        self.bind("<Button-4>", self.wheel)
        self.bind("<Button-5>", self.wheel)
        self.bind('<Button-3>', self.delete)
        self.bind('<Return>', self.add)
        
        self.protocol("WM_DELETE_WINDOW", self.stop)
        
        # Load config
        if not os.path.exists(CONFIG):
            with open(CONFIG, 'w') as file:
                file.write('{}')
        
        self.categories = json.load(open(CONFIG))
        
        # Widgets
        bar = tk.Frame(self, bg = '#000', bd = 1, relief = 'sunken', height = 40)
        
        color = dict( bg = '#000', fg = '#fff' )
        
        # Infos
        self.stat = tk.Label(bar, text = 'Cryptic - github.com/Egsagon', **color)
        self.stat.pack(side = 'left')
               
        buttons = {
            'TARGET': self.load_dir,
            'FULL': self.size_toggle,
            'GOTO': self.goto,
            'RAND': self.chunk,
            'SAVE': self.save,
            'CAT': self.cat
        }
        
        for tx, cmd in buttons.items():
            tk.Button(bar, text = tx, command = cmd).pack(side = 'right')
        
        bar.pack(side = 'bottom', fill = 'x')
        
        self.image: tk.Label = None
        
        # Variables
        self.index = 0
        self.cache = Path('./cache/')
        self.image_cache = {}
        
        self.key: object = None
        self.key_path: str = None
        self.decryptor: ffe.Decryptor = None
        
        self.dir: Path = None
        self.files: list[str] = None
        self.extensions = ('.png', '.jpg', '.jpeg')
        
        # Select directory and key
        
        if key is None:
            self.load_RSA()
        
        # Directly load key
        else:
            self.key = ffe.read_private_key(Path(key))
            self.key_path = key
        
        # self.load_dir()
        
        # Load first image
        self.update()
    
    def chunk(self, *_) -> None:
        '''
        Loads a random chunk of files.
        '''
        
        def on_confirm(*_) -> None:
            
            size = int(spin.get())
            
            self.files = random.sample(self.files, size)
            
            self.index = 0
            self.update()
            popup.destroy()
            
            tkmb.showinfo('Chunk generated', f'Sampled {size} files!')
        
        popup = tk.Toplevel(self)
        
        tk.Label(popup, text = 'Select chunk size')
        
        spin = tk.Spinbox(popup, from_ = 1, to = len(self.files) - 1)
        spin.pack()
        spin.focus()
        
        # Confirm and cancel buttons
        tk.Button(popup, text = 'OK', command = on_confirm).pack()
        tk.Button(popup, text = 'X', command = popup.destroy).pack()
        
        popup.mainloop()
    
    def size_ratio(self, *_) -> None:
        '''
        Change the window size to floating.
        '''
        
        ratio = .5
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        
        # Optimal ratio
        w = int( sw * ratio )
        h = int( sh * ratio )
        x = int( ( sw * (1 - ratio) ) // 2 )
        y = int( ( sh * (1 - ratio) ) // 2 )
        
        self.geometry(f'{w}x{h}+{x}+{y}')
    
    def size_toggle(self, *_) -> None:
        '''
        Toggle between fullscreen and ratio.
        '''
        
        attr = self.attributes('-fullscreen')
        self.attributes('-fullscreen', not attr)
        
        self.update()
    
    def load_RSA(self, *_) -> None:
        '''
        Load the private key.
        '''
        
        path = tkfd.askopenfilename(title = 'Private RSA Key')
        
        if not path:
            tkmb.showerror('Invalid', 'No file selected, exiting.')
            return self.stop()
        
        try:
            self.key = ffe.read_private_key(Path(path))
            self.key_path = path
        
        except Exception as err:
            tkmb.showerror('Failed to load key', repr(err))
            self.load_RSA()
    
    def load_dir(self, *_) -> None:
        '''
        Load a directory to decrypt.
        '''
        
        path = tkfd.askdirectory(title = 'Enctypted directory')
        self.dir = Path(path)
        
        if not path: return
        
        self.files = [file for file in os.listdir(path)
                      if file.endswith(self.extensions)]
        
        # Sort by creation date
        # self.files.sort(key = os.path.getmtime)
        
        if not self.files:
            return tkmb.showinfo('Emtpy directory',
                                 'No images found in ' + path)
        
        # Create cache and decryptor
        self.cache.mkdir(exist_ok = 1)
        self.decryptor = ffe.Decryptor(self.key)
        
        # Display the image
        self.index = 0
        
        # There really is no way to remove this
        self.prev()
        self.prev()
        self.next()
        self.next()
        
    def get(self, *_) -> Image:
        '''
        Load the current image to the cache
        or decrypt it and returns it.
        '''
        
        # Get the current encrypted file
        file = self.files[ self.index ]
        
        cached = self.cache / file
        
        # Load image from cache
        if cached in self.image_cache:
            image = self.image_cache[cached]
        
        # Decrypt image to cache
        else:
            self.decryptor.copy_decrypted(
                source = self.dir / file,
                destination = cached
            )
            
            image = Image.open(cached)
            self.image_cache[cached] = image
        
        # Update
        return image
    
    def resize(self, image: Image.Image,
               width: int, height: int) -> Image.Image:
        '''
        Resizes an image.
        '''
        
        ratio = min(width / image.width, height / image.height)
        
        return image.resize(
            size = (int(image.width * ratio),
                    int(image.height * ratio)),
            resample = Image.LANCZOS
        )
    
    def update(self, *_) -> None:
        '''
        Update the app.
        '''
        
        if self.files is None or not len(self.files):
            return self.stat.config(text = 'In no/empty directory')
        
        # Load and resize the image
        original = self.get()
        
        image = self.resize(original,
                            self.winfo_width(),
                            self.winfo_height())
        
        photo = ImageTk.PhotoImage(image)
        
        # Create the image label
        if self.image is None:
            self.image = tk.Label(self, image = photo, bg = '#000')
            self.image.pack(expand = True, fill = 'both', padx = 5, pady = 5)
        
        # Update the image label
        else:
            self.image.config(image = photo)
            self.image.image = photo
        
        # Update the status bar
        file = str(self.dir / self.files[ self.index ])
        cats = ', '.join([cat for cat, els in self.categories.items() if file in els])
        
        sep = '   '
        
        text = f'{self.index + 1} / {len(self.files)}{sep}RSA: {self.key_path}'
        text += f'{sep}DIR: {self.dir}{sep}CAT: {cats}'
        text += f'{sep}W/H: {original.width}/{original.height}'
        
        self.stat.config(text = text)
    
    def next(self, *_) -> None:
        '''
        Move to the next image.
        '''
        
        if self.index > 0:
            self.index -= 1
            self.update()
    
    def prev(self, *_) -> None:
        '''
        Move to the previous image.
        '''
        
        if self.index < len(self.files) - 1:
            self.index += 1
            self.update()
    
    def wheel(self, ev = None) -> None:
        '''
        Change image according to the mouse wheel.
        '''
        
        if ev.num == 5 or ev.delta == -120:
            self.prev()
        
        if ev.num == 4 or ev.delta == 120:
            self.next()
    
    def delete(self, *_) -> None:
        '''
        Remove the current image.
        '''
        
        # Confirmation popup
        if not tkmb.askyesno('Confirm', 'Delete Image?'): return
        
        # Delete file
        name = Path( self.files.pop(self.index) )
        
        file = self.dir / name
        cache = self.cache / name
        
        print('Deleting', file)
        file.unlink()
        cache.unlink()
        
        # Change to next file
        # self.prev()
        self.update()
    
    def stop(self, *_) -> None:
        '''
        Terminates the process and clear the cache.
        '''
        
        path = self.cache
        
        # Remove files
        if path.exists():
            for file in path.glob('*'):
                print('Deleting', file)
                file.unlink()
            
            path.rmdir()
        
        # Write config
        with open(CONFIG, 'w') as file:
            file.write(json.dumps(self.categories,
                                  indent = 3))
        
        # Stop the app
        self.destroy()
        exit()

    def add(self, *_) -> None:
        '''
        Add the current file to a specific category.
        '''
        
        # Get current file path
        path = str(self.dir / self.files[ self.index ])
        
        # Get available categories
        cats = [f'{name} ({len(files)} entries)' for name, files in self.categories.items()]
        
        def onclick(*_) -> None:
            
            name = entry.get()
            
            if not name:
                name = li.selection_get().split(' (')[0]
            
            if name in self.categories:
                self.categories[name] += [ path ]
        
            else:
                self.categories[name] = [ path ]
            
            popup.destroy()
            self.update()
        
        popup = tk.Toplevel(self)
        # x, y = self.winfo_pointerxy()
        # popup.geometry(f'+{x - 5}+{y - 5}')
        # popup.overrideredirect(1)
        
        tk.Label(popup, text = 'Select category:').pack()
        
        li = tk.Listbox(popup)
        for i, el in enumerate(cats): li.insert(i, el)
        li.pack()
        
        entry = tk.StringVar()
        
        tk.Label(popup, text = 'New category:').pack()
        
        box = tk.Entry(popup, textvariable = entry)
        box.pack()
        
        tk.Button(popup, text = 'OK', command = onclick).pack()
        tk.Button(popup, text = 'X', command = popup.destroy).pack()
        
        box.bind('<Return>', onclick)
        li.bind('<Return>', onclick)
        
        li.focus()

        popup.mainloop()

    def goto(self, *_) -> None:
        '''
        Goto a specific index.
        '''
        
        def confirm(*_) -> None:
            # Called when done
            
            self.index = int(entry.get()) - 1
            popup.destroy()
            self.update()
        
        popup = tk.Toplevel(self)
        popup.overrideredirect(1)
        
        x, y = self.winfo_pointerxy()
        popup.geometry(f'200x20+{x - 100}+{y - 10}')
        
        entry = tk.Spinbox(popup, from_ = 1, to = len(self.files))
        entry.pack(side = 'left')
        entry.focus()
        
        popup.bind('<FocusOut>', lambda *_: popup.destroy)

        # Confirm or cancel buttons
        tk.Button(popup, text = 'X', command = popup.destroy).pack(side = 'right')
        tk.Button(popup, text = 'OK', command = confirm).pack(side = 'right')
        
        popup.mainloop()

    def save(self, *_) -> None:
        '''
        Save as decrypted to a path.
        '''
        
        path = tkfd.asksaveasfilename()
        
        if not path: return
        
        self.get().save(path)
    
    def cat(self, *_) -> None:
        '''
        Open all files from a category from the current target.
        '''
        
        # Get available categories
        cats = [f'{name} ({len(files)} entries)' for name, files in self.categories.items()]
        
        def onclick(*_) -> None:
            # Get the files
            
            name = li.selection_get().split(' (')[0]
            
            filtered = []
            for file in self.files:
                path = str(self.dir / file)
                cats = [cat for cat, els in self.categories.items() if path in els]
                
                if name in cats:
                    filtered += [file]
            
            self.files = filtered
        
            self.update()
            popup.destroy()
            
            tkmb.showinfo('Operation', f'Loaded cat "{name}"!')
        
        popup = tk.Toplevel(self)

        tk.Label(popup, text = 'Select category:').pack()
        
        li = tk.Listbox(popup)
        for i, el in enumerate(cats): li.insert(i, el)
        li.pack()
        
        tk.Button(popup, text = 'OK', command = onclick).pack()
        tk.Button(popup, text = 'X', command = popup.destroy).pack()
        
        li.bind('<Return>', onclick)
        li.focus()

        popup.mainloop()


if __name__ == '__main__':
    
    if '-key' in sys.argv:
        app = App(sys.argv[-1])
    
    else:
        app = App()
    
    app.mainloop()

# EOF
