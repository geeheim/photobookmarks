#!/usr/bin/env python3
import argparse
import sqlite3
import os
import shutil
import logging
import sys
from .photos_db import *
import uuid
logger=logging.getLogger(__name__)


def update_or_merge_volume_table(connection, original_volume, temp_volume) -> tuple[int, int]:
    """ Compare volume information, add all missing volume entries from temp volume in original volume"""
    c = connection.cursor()
    lut = dict() # lookup dict for old and new volume keys
    for temp_uuid in temp_volume.keys():
        old_entry = temp_volume[temp_uuid]
        if temp_uuid not in original_volume:
            logger.info  ("adding Volume with uuid ", temp_uuid)
            new_uuid = str(uuid.uuid4()).upper()
            z_ent = get_entity_id_from_photos_database(c, "FileSystemVolume")
            z_opt = 1
            volume_name = old_entry["ZNAME"]
            volume_uuid = old_entry["ZVOLUMEUUIDSTRING"]
            c.execute("INSERT INTO ZFILESYSTEMVOLUME (Z_ENT, Z_OPT, ZNAME, ZUUID, ZVOLUMEUUIDSTRING) VALUES (?, ?, ?, ?, ?)",
                            (z_ent, z_opt, volume_name, new_uuid, volume_uuid))
            z_new_pk = c.lastrowid
            lut[old_entry['Z_PK']] = z_new_pk
            c.execute("UPDATE Z_PRIMARYKEY SET Z_MAX = ? WHERE Z_NAME = ?",(z_new_pk, "FileSystemVolume",))
        else:
            original_entry = original_volume[temp_uuid]
            lut[old_entry['Z_PK']] = original_entry['Z_PK']
    return lut

            
def update_bookmarks(cursor: sqlite3.Cursor, originals: List[PhotoInfo], update: PhotoInfo, volume_lut: dict) -> dict:
    """Update a bookmark in the photos db """

    for original_photo in originals:
        # updating the bookmark of all originals
        logger.info(f"Updating bookmark for {original_photo.asset_filename}")
        logger.debug(f"Original UUID: {original_photo.path_relative_to_volume}, Update UUID: {update.path_relative_to_volume}")
        logger.debug(f"Old Volume PK: {original_photo.volume_pk}, New Volume PK: {volume_lut[update.volume_pk]}")
        cursor.execute(
            "UPDATE ZFILESYSTEMBOOKMARK SET ZBOOKMARKDATA = ?, ZPATHRELATIVETOVOLUME = ? WHERE Z_PK = ?",
            (bytes(update.bookmark_data), update.path_relative_to_volume, original_photo.fsbookmark_pk))
        
        cursor.execute("UPDATE ZINTERNALRESOURCE SET ZFILESYSTEMVOLUME = ? WHERE ZFILESYSTEMBOOKMARK = ?",
            (volume_lut[update.volume_pk], original_photo.fsbookmark_pk))
        
        if not (original_photo.asset_filename.endswith(".HEIC", ) and original_photo.path_relative_to_volume.endswith(".MOV")):
            # it is not a live image so we also update the asset filename
            cursor.execute("UPDATE ZASSET SET ZDIRECTORY =?, ZFILENAME =? WHERE Z_PK = ?", 
                (update.asset_directory, update.asset_filename, original_photo.asset_pk),
             )  
        else:
            logger.info("Skipping update of asset filename for live image: %s", original_photo.asset_filename)
       
    

def main():
    parser = argparse.ArgumentParser(prog="update_photo_bookmarks",
                                     description="This scripts updates photo bookmarks in an MacOS photo library")
    parser.add_argument("-u", "--updated_bookmark_library_path", type=str, required=True,
                        help="Path to the photo library with updated bookmarks")
    parser.add_argument("-p", "--photos_library_path", type=str, required=True,
                        help="Path to the iCloud photo library which should be modified")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    parser.add_argument("-d", "--dry_run", action="store_true",
                        help="Do not make any changes, just print what would be done")
    parser.add_argument("-o", "--output_file", type=str,
                        help="Path to the output destination")
    args = parser.parse_args()

    # Set up basic configuration for logging
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    stream=sys.stdout, # Log messages to a file
                    )

    photos_library = args.photos_library_path
    updated_bookmarks = args.updated_bookmark_library_path
    # set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    # check if library exists
    if not os.path.exists(photos_library):
        print(f"Error: {photos_library} does not exist")
        return 1
    # check if updated_bookmarks exists
    if not os.path.exists(updated_bookmarks):
        print(f"Error: {updated_bookmarks} does not exist")
        return 1

    # copy photo_library_path to output_file if it is provided
    if args.output_file:
        if os.path.exists(args.output_file):
            logger.warning("Output file already exists. Overwriting...")
            shutil.rmtree(args.output_file)
        shutil.copytree(args.photos_library_path, args.output_file)
        photos_library = args.output_file
    else:
        photos_library = args.photos_library_path

    # get volume information
    original_volume = read_zfilesystemvolume_data(photos_library)
    updates_volume = read_zfilesystemvolume_data(updated_bookmarks)

    # get all referenced photos
    bm_updates = get_all_referenced_photos(updated_bookmarks)
    db, cur = open_photo_db(photos_library)

    volume_lut = update_or_merge_volume_table(db, original_volume, updates_volume)

    updated_bookmarks = 0
    for bm_update in bm_updates:
        orig_photo_info = get_photo_info(cur, bm_update.date_created, bm_update.path_relative_to_volume)
        if len(orig_photo_info) > 0:
            # photo exists in the database
            update_bookmarks(cur, orig_photo_info, bm_update, volume_lut)
            updated_bookmarks += 1
        else:
            # photo does not exist in the database
            logger.debug(f"Photo {bm_update.path_relative_to_volume} does not exist in the database")
    
    if args.dry_run:
        logger.info("Dry run mode: no changes will be made to the database.")
    else:
        db.commit()
    db.close()
    logger.info(f"Updated {updated_bookmarks} bookmarks.")

if __name__ == "__main__":
    main()