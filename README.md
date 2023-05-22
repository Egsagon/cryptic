# Cryptic

File viewer for encrypted images (crappy version).

### Usage

Considering a file structure like this:

```
└ source/
  └ ...
  └ repo1/
  └ repo2/
  └ cryptic/
    └ cryptic.py
    └ ...
```

##### Note: Where any image folder would be in the `source/` folder, e.g `repo1/` or `repo2/`.

##### Note: The `cryptic.py` file has to be executed from the `cryptic/` directory.

After its launch, the app will ask for a private key
for decrypting files. It will be able to fetch any directory placed directly in the `source/`
directory and containing encrypted images.

The app displays for each image its index out of all the files of the directory and its dimensions.

#### Bindings

Items will be displayed one after another and scrolling can be done using the arrow left/right keys
or the mouse wheel.

When pressing `Enter` on an image, a catagory menu will be shown where you can add the current image
to an existing category or create a new one.

When pressing `M2` on an image, you can delete it from the repository.

When pressing `Space` on an image, you can quickly apply a category to an image
without going through the category menu. That default category is set when using
the binding for the first time on a repository.

#### Actions

Following actions are possible though the status bar buttons:

- TARGET: Select the target repository.
- FULL: Toggle fullscreen.
- GOTO: Go to a specific image index
- RAND: Select a random chunk of k images and open them in a virtual directory.
- SAVE: Save the decrypted version of the current image to the pc.
- KEY: change the private key. Useful when using multiple directories encrypted with multiple keys.
- CAT: Select all the files of a certain category that are present in the current repository.
- GLOB CAT: Same as CAT but fetches all images saved to the category without taking care of the current directory.

### Installation

- CD to the `source/` directory
- Clone this repository
- CD into the repository
- Launch the `cryptic.py` file.
