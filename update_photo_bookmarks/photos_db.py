import sqlite3
from typing import Dict, List
import logging
from collections import namedtuple
import pathlib
import os

logger=logging.getLogger(__name__)

# namedtuple to hold the data from the ZFILESYSTEMBOOKMARK table
PhotoInfo = namedtuple(
    "PhotoInfo",
    ["fsbookmark_pk", "asset_pk", "volume_pk", "volume_name", "path_relative_to_volume", "bookmark_data", "asset_directory", "asset_filename", "date_created"],
)

def open_photo_db(fname: str) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Open sqlite database and return connection to the database"""
    try:
        if os.path.isfile(fname):
            sqlite_path = fname
        else:
            sqlite_path = pathlib.Path(fname) / "database/Photos.sqlite"
        conn = sqlite3.connect(str(sqlite_path))
        c = conn.cursor()
    except sqlite3.Error as e:
        raise OSError(f"Error opening {fname}: {e}") from e
    return (conn, c)

def get_all_referenced_photos(db_path: str) -> list[PhotoInfo]:
    """Return all referenced photos in the database"""
    conn, cur = open_photo_db(db_path)
    cur.execute(
        """ SELECT
            ZFILESYSTEMBOOKMARK.Z_PK,
            ZASSET.Z_PK,  
            ZFILESYSTEMVOLUME.Z_PK, 
            ZFILESYSTEMVOLUME.ZNAME, 
            ZFILESYSTEMBOOKMARK.ZPATHRELATIVETOVOLUME, 
            ZFILESYSTEMBOOKMARK.ZBOOKMARKDATA,
            ZASSET.ZDIRECTORY,
            ZASSET.ZFILENAME,
            ZASSET.ZDATECREATED
        FROM ZFILESYSTEMBOOKMARK
        JOIN ZINTERNALRESOURCE ON ZINTERNALRESOURCE.ZFILESYSTEMBOOKMARK = ZFILESYSTEMBOOKMARK.Z_PK
        JOIN ZFILESYSTEMVOLUME ON ZFILESYSTEMVOLUME.Z_PK = ZINTERNALRESOURCE.ZFILESYSTEMVOLUME
        JOIN ZASSET ON ZASSET.Z_PK = ZINTERNALRESOURCE.ZASSET
        WHERE ZASSET.ZSAVEDASSETTYPE = 10
    """)
    results = [PhotoInfo(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]) for row in cur]
    conn.close()
    return results


def get_photo_info(cur: sqlite3.Cursor, ts_created, filename) -> List[PhotoInfo]:
    """Get photo info from database"""
    cur.execute("""
        SELECT ZFILESYSTEMBOOKMARK.Z_PK,
            ZASSET.Z_PK,  
            ZFILESYSTEMVOLUME.Z_PK, 
            ZFILESYSTEMVOLUME.ZNAME, 
            ZFILESYSTEMBOOKMARK.ZPATHRELATIVETOVOLUME, 
            ZFILESYSTEMBOOKMARK.ZBOOKMARKDATA,
            ZASSET.ZDIRECTORY,
            ZASSET.ZFILENAME,
            ZASSET.ZSAVEDASSETTYPE,
            ZASSET.ZDATECREATED
        FROM ZASSET
        JOIN ZINTERNALRESOURCE ON ZINTERNALRESOURCE.ZFILESYSTEMBOOKMARK = ZFILESYSTEMBOOKMARK.Z_PK
        JOIN ZFILESYSTEMVOLUME ON ZFILESYSTEMVOLUME.Z_PK = ZINTERNALRESOURCE.ZFILESYSTEMVOLUME
        JOIN ZFILESYSTEMBOOKMARK ON ZASSET.Z_PK = ZINTERNALRESOURCE.ZASSET
        WHERE ZASSET.ZDATECREATED = ?
        """, (ts_created,))
    rows = cur.fetchall()
    logger.debug("got %d rows for ts_created=%s", len(rows), ts_created)
    entries = []
    for row in rows:
        if os.path.basename(row[4]) == os.path.basename(filename):
            entries.append(PhotoInfo(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
    return entries

def read_zfilesystemvolume_data(photos_db_path: str) -> Dict[int, sqlite3.Row]:
    """Return contents of ZFILESYSTEMVOLUME table as a dict of sqlite3.Row objects"""
    conn, c = open_photo_db(photos_db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()  # need to get cursor again to use row_factory
    c.execute("SELECT Z_PK, ZNAME, ZUUID, ZVOLUMEUUIDSTRING FROM ZFILESYSTEMVOLUME")
    result = {row["ZVOLUMEUUIDSTRING"]: row for row in c.fetchall()}
    conn.close()
    return result

def get_entity_id_from_photos_database(cursor: sqlite3.Cursor, entity: str) -> int:
    """Get the associated Z_ENT entity ID from the Z_PRIMARYKEY table for entity"""
    results = cursor.execute(
        "SELECT Z_ENT FROM Z_PRIMARYKEY WHERE Z_NAME = ?", (entity,)
    ).fetchone()
    if results is None:
        raise ValueError(f"Could not find entity {entity} in Z_PRIMARYKEY table")
    return results[0]
