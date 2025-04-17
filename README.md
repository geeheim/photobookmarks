# photobookmarks
This is a tool to update the referenced files in mac os photos app. It is heavily influenced by https://github.com/RhetTbull/RepairPhotosBookmarks.

This version was tested on macOS 15.4 (Sequoia)

# Introduction
Photos has two modes how to manage the locoation of photos. 

1. Photos are copied into the media library, in this case you don't need this tool.
2. The imported photos are not copied into your library, they are stored on your harddisk/NAS/USB drive/...

In the second case you can get into trouble if you move your files into a new location, e.g.:
1. You have a new mac
2. you want to move your files to a new SSD 
3. Your harddisk is broken and you restore your photos from a backup
4. ...

In photos you can relocate photos one by one, which is not feasible if you manage 1000+ photos.
That's why I created this little tool.

# How to use it
The reference to a file/photo is stored in a "Bookmark" [https://developer.apple.com/documentation/professional-video-applications/using-bookmark-data]. These Bookmarks can only be created by the app
which is using it. Therefore the first step is to create a new library with all moved files. You could also
add much more files. 
Open photos by pressing holding the 'alt' key and press the "Create New ..." button to create a new library. 
Ensure that the setting "Copy Items to the Photo library" is disabled.
From the menu choose 'File -> Import' and select the folder with your moved files/photos. You can import all 
photos at once. Time to get a coffee.

In the meantime you can install the script with `pip install update_photo_bookmarks`. 
The script needs the current library as well as the just created library with the new locations.
The script checks for each referenced image if there is a match in the new library. An image is considerd
as equal if the original name and the timestamp (usually time when taking the picture) match. If that is the case
all references will be updated in the current library. 

    This scripts updates photo bookmarks in an MacOS photo library

    options:
    -h, --help            show this help message and exit
    -u UPDATED_BOOKMARK_LIBRARY_PATH, --updated_bookmark_library_path UPDATED_BOOKMARK_LIBRARY_PATH
                            Path to the photo library with updated bookmarks
    -p PHOTOS_LIBRARY_PATH, --photos_library_path PHOTOS_LIBRARY_PATH
                            Path to the iCloud photo library which should be modified
    -v, --verbose         Enable verbose output
    -d, --dry_run         Do not make any changes, just print what would be done
    -o OUTPUT_FILE, --output_file OUTPUT_FILE
                            Path to the output destination

Example how to use it:

    update_photo_bookmarks.py -u 'tmp/2024_updates.photoslibrary' -p '~/pictures/Fotos Library-fixed.photoslibrary'


# Notes
Of course I suggest to have a backup of your library before running this script.

This is my first python project, happy if you find any issues or have suggestions for improvement. Happy coding! 


