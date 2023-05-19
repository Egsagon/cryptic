'''
Cryptic
'''

import os
import sys
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
        self.geometry('800x600')
        self.config(bg = '#000')
        
        # Bindings
        self.bind('<Left>', self.next)
        self.bind('<Right>', self.prev)
        self.bind('<MouseWheel>', self.wheel)
        self.bind("<Button-4>", self.wheel)
        self.bind("<Button-5>", self.wheel)
        self.bind('<Button-3>', self.delete)
        
        self.protocol("WM_DELETE_WINDOW", self.stop)
        
        # Widgets
        bar = tk.Frame(self, bg = '#000', bd = 1, relief = 'sunken')
        
        self.stat = tk.Label(bar, text = 'In nowhere', bg = '#000', fg = '#fff')
        move = tk.Button(bar, text = 'Move', command = self.load_dir, bg = '#000', fg = '#fff')
        
        self.stat.pack(side = 'left')
        move.pack(side = 'right')
        
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
        
        self.load_dir()
        
        # Load first image
        # (it does not works without it)
        self.prev()
        self.prev()
        self.next()
        self.next()
    
    def load_RSA(self, *_) -> None:
        '''
        Load the private key.
        '''
        
        path = tkfd.askopenfilename(title = 'Private RSA Key')
        
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
        
        if not path:
            tkmb.showerror('No directory selected, exiting.')
            exit()
        
        self.files = [file for file in os.listdir(path)
                      if file.endswith(self.extensions)]
        
        if not self.files:
            return tkmb.showinfo('Emtpy directory',
                                 'No images found in ' + path)
        
        # Create cache and decryptor
        self.cache.mkdir(exist_ok = 1)
        self.decryptor = ffe.Decryptor(self.key)
        
        # Display the image
        self.index = 0
        self.dir = Path(path)
        self.update()
        
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
               width: int, height: int) -> Image:
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
        
        # Load and resize the image
        image = self.resize(self.get(),
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
        text = f'{self.index + 1} / {len(self.files)} | RSA: {self.key_path} | DIR: {self.dir}'
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
        if not tkmb.askyesno('Delete?', 'Delete file?'): return
        
        # Delete file
        file = Path(self.files[ self.index ])
        print('Deleting', file)
        file.unlink()

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
        
        # Stop the app
        self.destroy()
        exit()


if __name__ == '__main__':
    
    if '--key' in sys.argv:
        app = App(sys.argv[-1])
    
    else:
        app = App()
    
    app.mainloop()

# EOF