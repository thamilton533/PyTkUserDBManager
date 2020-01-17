#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  gui.py
#

from tkinter import *
import webapp_db
from dicts import get_master_user_dict

data = "User Data will appear here"

# Connect to database and get usernames
c, conn = webapp_db.db_connect()

# Global vars
master_user_dict = get_master_user_dict()


class ScrollBox(Listbox):

    def __init__(self, window, **kwargs):
        super().__init__(window, **kwargs)

        self.scrollbar = Scrollbar(window, orient=VERTICAL, command=self.yview)

    def grid(self, row, column, sticky='nsw', rowspan=1, columnspan=1, **kwargs):
        # tkinter.Listbox.grid(self, row=row, column=column, sticky=sticky, rowspan=rowspan,
        #  **kwargs)  # Python 2
        super().grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan, **kwargs)
        self.scrollbar.grid(row=row, column=column, sticky='nse', rowspan=rowspan)
        self['yscrollcommand'] = self.scrollbar.set


class MyDialog:

    def __init__(self, parent, dict):

        top = self.top = Toplevel(parent)

        top.title("Alert!")
        geom = '+' + str(parent.winfo_x()+100) + '-' + str(parent.winfo_y() + parent.winfo_height())
        top.geometry(geom)

        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=4)
        top.columnconfigure(2, weight=1)

        top.rowconfigure(0, weight=1)
        top.rowconfigure(1, weight=1)
        top.rowconfigure(2, weight=1)
        top.rowconfigure(3, weight=1)

        prompt = Label(top, text="Update Dictionary?")
        prompt.grid(row=0, column=1, sticky="ew", padx=(10,0))

        d = Label(top, text=dict)
        d.grid(row=1, column=1, sticky="ew", padx=(10,0))

        yes_b = Button(top, text="Yes", command=self.yes)
        yes_b.grid(row=2, column=1, sticky="ew", padx=(10,0))

        no_b = Button(top, text="No", command=self.no)
        no_b.grid(row=3, column=1, sticky="ew", padx=(10,0))

    def yes(self):

        print("Dictionary Updated")

        self.top.destroy()

    def no(self):

        print("Update Cancelled")

        self.top.destroy()


class DictEditor(Frame):

    def __init__(self, window, connection, table, field, sort_order=(), **kwargs):
        super().__init__(window, **kwargs)

        self.linked_box = None
        self.link_field = None
        self.link_value = None

        self.cursor = connection.cursor()
        self.table = table
        self.field = field

        self.framerow = 0

        self.newdict = []

        self.sql_select = "SELECT " + "uid," + self.field + " FROM " + self.table
        if sort_order:
            self.sql_sort = " ORDER BY " + ','.join(sort_order)
        else:
            self.sql_sort = " ORDER BY " + self.field

        print(self.sql_select)

        self.scrollbar = Scrollbar(window, orient=VERTICAL)

    def grid(self, row, column, sticky='nsw', rowspan=1, columnspan=1, **kwargs):
        # tkinter.Listbox.grid(self, row=row, column=column, sticky=sticky, rowspan=rowspan,
        #  **kwargs)  # Python 2
        super().grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan, **kwargs)
        self.scrollbar.grid(row=row, column=column, sticky='nse', rowspan=rowspan)

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def link(self, widget, link_field):
        self.linked_box = widget
        widget.link_field = link_field

    def load(self, link_value=None):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)

        if link_value and self.link_field:
            sql = self.sql_select + " WHERE " + self.link_field + "=?" + self.sql_sort
            self.cursor.execute(sql, (link_value,))
        else:
            self.cursor.execute(self.sql_select + self.sql_sort)

        # Clear dictionary edit box
        self.clear()
        
        # Get dictionary from data base per username
        userstr = self.cursor.fetchone()
        userdict = eval(userstr[1])

        # Populate GUI Frame with user dictionary
        self.framerow = 0
        for key, value in master_user_dict.items():

            label = Label(self, text=key)
            label.grid(column=0, row=self.framerow, sticky='w')

            if type(value) == str:
                textvalue = userdict.get(key)
                #if dictionary key is found
                if textvalue:
                    val_edit = Entry(self)
                    val_edit.insert(INSERT, textvalue)
                    val_edit.grid(column=1, row=self.framerow, sticky='w')
            elif type(value) == list:
                listVar = StringVar(self)
                listVar.set(userdict[key])
                dropdown = OptionMenu(self, listVar, *value)
                dropdown.grid(column=1, row=self.framerow, sticky='w')

            self.framerow = self.framerow+1

    def get_current_dict(self):
        edit_dict = {}
        c_key = ""
        _list = self.winfo_children()

        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())

            if type(item) == Label:
                c_key = item.cget("text")
                edit_dict[c_key] = None

            elif type(item) == OptionMenu:
                edit_dict[c_key] = item.cget("text")

            elif type(item) == Entry:
                edit_dict[c_key] = item.get()

        print(edit_dict)

        d = MyDialog(window, edit_dict)
        window.wait_window(d.top)
        self.update_database(edit_dict)

        return edit_dict

    def update_database(self, dict):
        print(self.link_field)
        self.sql_update = "UPDATE " + self.table + " SET " + self.field + " = " + str(dict) + " WHERE " + self.link_field + "=TimHamilton"
        print(self.sql_update)
        #self.cursor.execute(self.sql_update)

class DataListBox(ScrollBox):

    def __init__(self, window, connection, table, field, sort_order=(), **kwargs):
        super().__init__(window, **kwargs)

        self.linked_box = None
        self.link_field = None
        self.link_value = None

        self.cursor = connection.cursor()
        self.table = table
        self.field = field

        self.bind('<<ListboxSelect>>', self.on_select)

        self.sql_select = "SELECT " + "uid," + self.field + " FROM " + self.table
        if sort_order:
            self.sql_sort = " ORDER BY " + ','.join(sort_order)
        else:
            self.sql_sort = " ORDER BY " + self.field

        print(self.sql_select)

    def clear(self):
        self.delete(0, END)

    def link(self, widget, link_field):
        self.linked_box = widget
        widget.link_field = link_field

    def requery(self, link_value=None):
        if link_value and self.link_field:
            sql = self.sql_select + " WHERE " + self.link_field + "=?" + self.sql_sort
            self.cursor.execute(sql, (link_value,))
        else:
            self.cursor.execute(self.sql_select + self.sql_sort)

        # clear the listbox contents before re-loading
        self.clear()
        for value in self.cursor:
            self.insert(END, value[1])

        if self.linked_box:
            self.linked_box.clear()

    def on_select(self, event):
        if self.linked_box:
            index = self.curselection()[0]
            value = self.get(index),

            # get the ID from the database row
            # Make sure we're getting the correct one, by including the link_value if appropriate
            if self.link_value:
                value = value[0], self.link_value
                sql_where = " WHERE " + self.field + "=? AND " + self.link_field + "=?"
            else:
                sql_where = " WHERE " + self.field + "=?"

            link_id = self.cursor.execute(self.sql_select + sql_where, value).fetchone()[1]
            self.linked_box.load(link_id)

    def get_email(self, event):
        lb = event.widget
        index = lb.curselection()[0]
        username = lb.get(index)
        print(index, username)

        # the the email from the database
        email = c.execute("SELECT email FROM users WHERE username=?", (username,)).fetchone()
        keysList.insert(END, email)

    def get_value(self, event):
        lb = event.widget
        index = lb.curselection()
        key = lb.get(index)
        print(index)
        print(key)


# === Window Object ===
window = Tk()
window.title("Env App User Database Manager")
window.geometry('800x600-10+10')

window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)

window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=4)
window.rowconfigure(2, weight=1)
window.rowconfigure(3, weight=1)
window.rowconfigure(4, weight=1)
Label(window, text="Username").grid(column=0, row=0)
Label(window, text="User Data").grid(column=1, row=0)

# === User List Box ===
userList = DataListBox(window, conn, "users", "username", sort_order=("uid",))
userList.grid(column=0, row=1, sticky='nsew', padx=(30, 0))
userList.config(border=2, relief='sunken')

userList.requery()

# === Dictionary Editor Frame ===
dataFrame = DictEditor(window, conn, "users", "data", sort_order=("uid",))
dataFrame.grid(column=1, row=1, sticky='nsew', padx=(30, 0))
dataFrame.grid(column=1, row=1, sticky='nsew', padx=(30, 0))
dataFrame.config(border=1, relief='sunken')

userList.link(dataFrame, "username")

# === Buttons ===
submitButton = Button(window, text="Submit Database Changes", command=dataFrame.get_current_dict)
submitButton.grid(column=1, row=2, sticky="ew", padx=(30, 0))

clearButton = Button(window, text="Clear", command=dataFrame.clear)
clearButton.grid(column=1, row=3, sticky="ew", padx=(30, 0))

exitButton = Button(window, text="Exit", command=exit)
exitButton.grid(column=1, row=4, sticky="ew", padx=(30, 0))


# === Execute UI ===
window.mainloop()
webapp_db.db_disconnect(conn)