#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  dicts.py
#


USER_DATA_MASTER = {}
TEXT_FIELD = 'Text Field'

USER_DATA_MASTER["usertype"] = ["admin", "root", "std"]
USER_DATA_MASTER["dateofreg"] = ""
USER_DATA_MASTER["lastlogin"] = ""
USER_DATA_MASTER["emailaddr_valid"] = ["false", "true"]


def get_master_user_dict():
    return USER_DATA_MASTER
