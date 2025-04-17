import pytest
from update_photo_bookmarks.photos_db import *
import pathlib
import unittest
import sqlite3
import tempfile
import os

def test_get_all_referenced_photos():
    ref = get_all_referenced_photos(pathlib.Path("./tests/test_data"))
    print(ref)
    assert len(ref) == 8

def test_get_photo_info():
    conn, cur = open_photo_db(pathlib.Path("./tests/test_data"))
    photo_info = get_photo_info(cur, "2021-01-01 00:00:00", "test.jpg")
    assert len(photo_info) == 0
    photo_info = get_photo_info(cur, 671368029, "DSCF8331.RAF")
    assert photo_info != None
    print(photo_info)
    conn.close()
    
class TestPhotosDB(unittest.TestCase):
    def setUp(self):
        # Create a temporary SQLite database for testing
        self.db_path = tempfile.NamedTemporaryFile(delete=False).name
        conn, c = open_photo_db(self.db_path)
        c.execute("CREATE TABLE ZFILESYSTEMVOLUME (Z_PK INTEGER PRIMARY KEY, ZNAME TEXT, ZUUID TEXT, ZVOLUMEUUIDSTRING TEXT)")
        c.execute("INSERT INTO ZFILESYSTEMVOLUME (ZNAME, ZUUID, ZVOLUMEUUIDSTRING) VALUES (?, ?, ?)", ('Volume1', 'UUID1', 'VolUUID1'))
        conn.commit()
        conn.close()

    def tearDown(self):
        # Clean up the temporary database
        os.unlink(self.db_path)

    def test_read_zfilesystemvolume_data(self):
        data = read_zfilesystemvolume_data(self.db_path)
        self.assertIn('VolUUID1', data)
        row = data['VolUUID1']
        self.assertEqual(row['ZNAME'], 'Volume1')
        self.assertEqual(row['ZUUID'], 'UUID1')
        self.assertEqual(row['ZVOLUMEUUIDSTRING'], 'VolUUID1')

if __name__ == "__main__":
    pytest.main()