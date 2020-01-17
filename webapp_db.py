#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  webapp_db.py
#

import sqlite3
import gc

db_path = "envdata.db"

def db_connect():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    print("Connected to envdata.db")

    return c, conn

def db_disconnect(conn):
    conn.close()
    gc.collect()
    print("Disconnected from envdata.db")

