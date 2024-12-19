import tkinter as Tk
from tkinter import ttk, font, messagebox
import sqlite3
import enum

# make reference of GUI class so other classes depending on it can access
class GUI:...

############################ UPDATE TAB ############################

class Entry:
    """
    Class that holds the data of a singular entry in a table 
    """
    def __init__(self, name: str, date: str, book_of_bible: str, main_character_or_event: str, standingout_verse: str, time_spent_min: str, practical_action: str, id: int = -1) -> None:
        self.id: int = id # -1 means not determined
        self.name: str = name
        self.date: str = date
        self.book_of_bible: str = book_of_bible
        self.main_character_or_event: str = main_character_or_event
        self.standingout_verse: str = standingout_verse
        self.time_spent_min: str = time_spent_min
        self.practical_action: str = practical_action

    #
    def get(self) -> list[str]:
        """
        Get the row in the form of a list
        """
        return [self.name, self.date, self.book_of_bible, self.main_character_or_event, self.standingout_verse, self.time_spent_min, self.practical_action, self.id]

class DatabaseConnection:
    def __init__(self) -> None:
        """
        Open a database connection and manage it
        """
        self.connection: sqlite3.Connection | None = sqlite3.connect('Faith_Walk.db')
        self.cursor: sqlite3.Cursor = self.connection.cursor()
        # create the table if it does not currently exist
        # can change structure later if needing more than one table
        self.cursor.execute("""CREATE table if not exists DailyBibleReading (
            id INTEGER primary key autoincrement, 
            name_row TEXT, 
            date_row TEXT, 
            book_row TEXT,
            event_row TEXT,
            verse_row TEXT,
            time_row TEXT,
            action_row TEXT
        )""")
        self.connection.commit()

    def add_entry(self, entry: Entry) -> None:
        """
        Add an entry to the database
        """
        if not self.connection:
            #raise an exception if not connected to the database, 
            #could easily have a failsafe but it is best that we know there are errors
            raise Exception("ADD entry error: Not connected to database") 
        formatted_entry: list[str] = entry.get()
        formatted_entry.pop(-1)
        self.cursor.execute("INSERT into DailyBibleReading (name_row, date_row, book_row, event_row, verse_row, time_row, action_row) VALUES (?, ?, ?, ?, ?, ?, ?)",
            tuple(formatted_entry)
        )

        entry.id = self.cursor.lastrowid
        
        self.connection.commit()

    def edit_entry(self, entry: Entry) -> None:
        """
        Edit an entry in a database
        """
        if entry.id == -1:
            raise Exception("When editing database Entry, ID = -1")
        
        self.cursor.execute("""
        UPDATE DailyBibleReading
        SET name_row = ?, date_row = ?, book_row = ?, event_row = ?, verse_row = ?, time_row = ?, action_row = ?
        WHERE id = ?
        """, tuple(entry.get())) 

        self.connection.commit()

    def delete_entry(self, entry_id: int):
        """
        Delete a row in the database using an ID
        """
        self.cursor.execute("DELETE FROM DailyBibleReading WHERE id = ?", (entry_id,))
        self.connection.commit()

    def get_entries(self) -> list[Entry]:
        """
        Get all rows in the database in the form of Entries
        """
        if not self.connection: 
            # raise an exception if not connected to the database
            raise Exception("GET entries error: Not connected to database") 
        self.cursor.execute('SELECT * FROM DailyBibleReading')
        rows = self.cursor.fetchall()
        table: list[Entry] = []
        for row in rows:
            table.append(Entry(row[1], row[2], row[3], row[4], row[5], row[6], row[7], id=row[0]))

        return table

    def disconnect(self, commit: bool = False) -> None:
        """
        Disconnect from the database
        """
        if not self.connection: 
            # raise an exception if not connected to the database
            raise Exception("Disconnect error: Not connected to database") 
        if commit:
            self.connection.commit()
        self.connection.close()
        self.connection = None

class DataType(enum.Enum):
    NAME = 0
    DATE = 1
    BOOK = 2
    EVENT = 3
    VERSE = 4
    TIME = 5
    ACTION = 6

class Table_Row:
    def __init__(self, parent: Tk.Frame, row_index: int, row: Entry, parentGUIinstance: GUI) -> None:
        """
        Used for storing rows in the database viewing table.
        """
        self.row: Entry = row
        self.row_index: int = row_index
        self.text_boxes: dict[DataType, Tk.Text] = {}
        self.parentGUIinstance: GUI = parentGUIinstance

        #
        for column_index in range(7):
            cell = Tk.Text(parent, width=12, height=3, wrap='word')
            cell.grid(row=row_index, column=column_index, padx=1, pady=1)
            cell.insert(Tk.END, row.get()[column_index])
            cell.config(state=Tk.DISABLED)  # Make cells read-only if desired
            self.text_boxes.update({DataType(column_index): cell})

        #create edit and delete button
        self.edit_button = Tk.Button(parent, text="Edit", width=9, height=2, command=self.edit_press)
        self.delete_button = Tk.Button(parent, text="Delete", width=9, height=2, command=self.delete_press)

        #set edit and delete buttons into the View Tab grid
        self.edit_button.grid(row=row_index, column=7, padx=1, pady=1)
        self.delete_button.grid(row=row_index, column=8, padx=1, pady=1)

    #edit button sends user to Update tab
    def edit_press(self, *args) -> None:
        """
        Calls upon edit button being pressed.
        """
        self.parentGUIinstance.row_being_edited = self.row_index
        #sends user to Update Tab
        self.parentGUIinstance.tabController.select(self.parentGUIinstance.changeDatabaseTab)
        #edits the row
        self.parentGUIinstance.edit_row(self.row)

    #messagebox confirming deleting a row
    def delete_press(self, *args) -> None:
        """
        Calls upon d button being pressed.
        """
        response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this entry?")
    
        if response:  # if clicks Yes
            self.parentGUIinstance.view_table.delete_row(self.row_index)
        # nothing happens if pressed No

    #put text in each row
    def set_text(self, new_text: str, database_value: DataType) -> None:
        """
        Sets the text of a textbox in a row
        """
        match (database_value):
            case DataType.NAME:
                self.row.name = new_text
            case DataType.DATE:
                self.row.date = new_text
            case DataType.BOOK:
                self.row.book_of_bible = new_text
            case DataType.EVENT:
                self.row.main_character_or_event = new_text
            case DataType.VERSE:
                self.row.standingout_verse = new_text
            case DataType.TIME:
                self.row.time_spent_min = new_text
            case DataType.ACTION:
                self.row.practical_action = new_text
        # using the database Type as the key, get the textbox and 
        box = self.text_boxes[database_value]
        box.config(state=Tk.NORMAL)
        box.delete("1.0", Tk.END)
        box.insert(Tk.END, new_text)
        box.config(state=Tk.DISABLED)

#############################VIEW TAB#########################################

#create the table in the view tab
class Table:
    def __init__(self, parentGUIinstance: GUI):
        """
        Creates a table which is used in the view database tab
        """
        # Create frame to hold the canvas and scrollbar
        self.parentGUIinstance = parentGUIinstance
        self.canvas_frame = Tk.Frame(self.parentGUIinstance.viewDatabaseTab)
        self.canvas_frame.pack(fill=Tk.BOTH, expand=True)

        # Create and pack the canvas
        self.canvas = Tk.Canvas(self.canvas_frame)
        self.canvas.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)

        # Create and pack the vertical scrollbar
        self.scrollbar = Tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)

        # Configure the canvas to work with the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas to hold the table
        self.table_frame = Tk.Frame(self.canvas)
        
        # Add the table_frame to the canvas
        self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        # Bind the <Configure> event to update the scrollregion
        self.table_frame.bind("<Configure>", self.on_frame_configure)

        # Fetch table rows from the database
        database_entries: list[Entry] = parentGUIinstance.database.get_entries()
        self.table_rows: list[Table_Row] = []

        # Code for creating the table
        for index in range(len(database_entries)):
            self.table_rows.append(Table_Row(self.table_frame, index, database_entries[index], parentGUIinstance))

    def delete_row(self, index: int):
        """
        Delete a row from the table
        """
        row_being_deleted = self.table_rows[index]
        # delete from data base
        self.parentGUIinstance.database.delete_entry(row_being_deleted.row.id)
        print(row_being_deleted.row.id)

        # delete all textboxes in the row
        for textbox in row_being_deleted.text_boxes.values():
            textbox.destroy()
        row_being_deleted.edit_button.destroy()
        row_being_deleted.delete_button.destroy()

        self.table_rows.pop(index)
        # shift all textboxes accordingly
        for new_index, table_row in enumerate(self.table_rows):
            table_row.row_index = new_index
            for textbox in table_row.text_boxes.values():
                textbox.grid(row=new_index)

            table_row.edit_button.grid(row=new_index, column=7)
            table_row.delete_button.grid(row=new_index, column=8)
    
    #create scrollbar
    def on_frame_configure(self, event):
        #Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

class CreateEntryGUI:
    def __init__(self, parentGUIinstance: GUI) -> None:
        """
        GUI for updating the 
        """
        self.parentGUIinstance: GUI = parentGUIinstance
        self.left_frame = ttk.Frame(self.parentGUIinstance.changeDatabaseTab)
        self.right_frame = ttk.Frame(self.parentGUIinstance.changeDatabaseTab)
        self.top_frame = ttk.Frame(self.parentGUIinstance.changeDatabaseTab)
        self.bottom_frame = ttk.Frame(self.parentGUIinstance.changeDatabaseTab)

# use grid so the labels and textboxes can be packed side-by-side
#----------------create a grid------------------
        self.left_frame.grid(row=1, column=0, sticky="nsew")
        self.right_frame.grid(row=1, column=1, sticky="nsew")
        self.top_frame.grid(row=0, column=1, sticky="nsew")
        self.bottom_frame.grid(row=2, column=1, sticky="nsew")

#---------------TOP FRAME----------------------------
        self.title_label = Tk.Label(self.top_frame, text='FAITH WALK', font=font.Font(size = 36))
        self.subtitle_label = Tk.Label(self.top_frame, text='keeping track of your daily discipleship', font=font.Font(size = 13))

        self.title_label.pack()
        self.subtitle_label.pack()

        #create variable for font size in order to change easily
        self.label_size: font = font.Font(size=17)

#-----------------RIGHT FRAME--------------------------
        self.name_label = ttk.Label(self.left_frame, text='NAME ', font=self.label_size, width=7)
        self.date_label = ttk.Label(self.left_frame, text='DATE ', font=self.label_size, width=7)
        self.book_label = ttk.Label(self.left_frame, text='BOOK ', font=self.label_size, width=7)
        self.event_label = ttk.Label(self.left_frame, text='EVENT ', font=self.label_size, width=7)
        self.verse_label = ttk.Label(self.left_frame, text='VERSE ', font=self.label_size, width=7)
        self.time_label = ttk.Label(self.left_frame, text='MINUTE ', font=self.label_size, width=7)
        self.action_label = ttk.Label(self.left_frame, text='ACTION ', font=self.label_size, width=7)

        #pack the labels into the right frame
        self.name_label.pack(padx=10)
        self.date_label.pack(padx=10, pady=4)
        self.book_label.pack(padx=10, pady=4)
        self.event_label.pack(padx=10, pady=4)
        self.verse_label.pack(padx=10, pady=4)
        self.time_label.pack(padx=10, pady=4)
        self.action_label.pack(padx=10, pady=4)

#-------------------LEFT FRAME-----------------
        #create textbox widgets
        self.name_box = Tk.Text(self.right_frame, width=90, height=2)
        self.date_box = Tk.Text(self.right_frame, width=90, height=2)
        self.book_box = Tk.Text(self.right_frame, width=90, height=2)
        self.event_box = Tk.Text(self.right_frame, width=90, height=2)
        self.verse_box = Tk.Text(self.right_frame, width=90, height=2)
        self.time_box = Tk.Text(self.right_frame, width=90, height=2)
        self.action_box = Tk.Text(self.right_frame, width=90, height=2)

        #packing the textbox widgets into the left frame
        self.name_box.pack(padx=10)
        self.date_box.pack(padx=10)
        self.book_box.pack(padx=10)
        self.event_box.pack(padx=10)
        self.verse_box.pack(padx=10)
        self.time_box.pack(padx=10)
        self.action_box.pack(padx=10)
        
#--------------BOTTOM FRAME---------------
        #create and pack the cancel button
        self.cancel_button = Tk.Button(self.bottom_frame, text='Cancel', command=self.parentGUIinstance.cancel_action, width=17, height=1, font=self.label_size)
        self.cancel_button.grid(row=0, column=1, padx=50)

        #create and pack the submit button
        self.submit_button = Tk.Button(self.bottom_frame, text='Submit', command=self.parentGUIinstance.submit_pressed, width=17, height=1, font=self.label_size)
        self.submit_button.grid(row=0, column=0, padx=50)

class GUI:
    def __init__(self):
        """
        Main window and GUI
        """
        # open a connection to the database
        self.database = DatabaseConnection()
        
        #generate_filler_entries(self.database)
        # create the main window
        self.window = Tk.Tk()
        self.window.title("Faith Walk")
        self.window.config(bg='#1e2124')
        self.window.geometry('900x500')
        self.window.resizable(False, False)

        #creating both Update and View tab
        self.tabController = ttk.Notebook(self.window)
        self.viewDatabaseTab = ttk.Frame(self.tabController)
        self.changeDatabaseTab = ttk.Frame(self.tabController)
        self.tabController.add(self.viewDatabaseTab, text ='View')
        self.tabController.add(self.changeDatabaseTab, text ='Update')
        self.tabController.pack(expand=1, fill="both")
        self.tabController.bind("<<NotebookTabChanged>>", self.on_tab_change)

#------------------UPDATE Tab---------------------#

        #create interface for the Update tab
        self.change_tab = CreateEntryGUI(self)

        # the index of the row that is being edited
        # if it == -1, then there is no row being edited
        self.row_being_edited: int = -1
        
        #detects when window is closed and calls 'on_closing' method
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

#------------------VIEW Tab---------------------#
        #view table
        self.view_table = Table(self)

        #run mainloop
        self.window.mainloop()

    def on_closing(self) -> None:
        """
        Fires when 'X' button is clicked 
        """
        self.database.disconnect()
        self.window.destroy()

    def clear_textboxes(self):
        """
        Delete contents of textboxes, resets textbox widgets
        """
        # clear textboxes
        self.change_tab.name_box.delete("1.0", Tk.END)
        self.change_tab.date_box.delete("1.0", Tk.END)
        self.change_tab.book_box.delete("1.0", Tk.END)
        self.change_tab.event_box.delete("1.0", Tk.END)
        self.change_tab.verse_box.delete("1.0", Tk.END)
        self.change_tab.time_box.delete("1.0", Tk.END)
        self.change_tab.action_box.delete("1.0", Tk.END)

    def get_textboxes(self) -> Entry:
        """
        Change data from textbox widgets into string
        """
        name_string: str = self.change_tab.name_box.get("1.0", Tk.END)
        date_string: str = self.change_tab.date_box.get("1.0", Tk.END)
        book_string: str = self.change_tab.book_box.get("1.0", Tk.END)
        event_string: str = self.change_tab.event_box.get("1.0", Tk.END)
        verse_string: str = self.change_tab.verse_box.get("1.0", Tk.END)
        time_string: str = self.change_tab.time_box.get("1.0", Tk.END)
        action_string: str = self.change_tab.action_box.get("1.0", Tk.END)

        datarow_id = self.view_table.table_rows[self.row_being_edited].row.id
        return Entry(name_string, date_string, book_string, event_string, verse_string, time_string, action_string, id = datarow_id)

    def edit_row(self, entry: Entry) -> None:
        """
        Edit a specific row in the view table
        """
        # set textboxes to correct values, make cancel button visible and lock tab view on "Change Tab" until finished

        self.clear_textboxes()
        # set change tab textboxes to be correct
        self.change_tab.name_box.insert(Tk.END, entry.name)
        self.change_tab.date_box.insert(Tk.END, entry.date)
        self.change_tab.book_box.insert(Tk.END, entry.book_of_bible)
        self.change_tab.event_box.insert(Tk.END, entry.main_character_or_event)
        self.change_tab.verse_box.insert(Tk.END, entry.standingout_verse)
        self.change_tab.time_box.insert(Tk.END, entry.time_spent_min)
        self.change_tab.action_box.insert(Tk.END, entry.practical_action)

    def on_tab_change(self, *args):
        """
        Calls when the user changes tabs 
        """
        # if a row is being edited, it will automatically switch back to the Update tab
        if self.row_being_edited != -1:
            self.tabController.select(self.changeDatabaseTab)
 
    def submit_pressed(self, *args):
        """
        Create submit button that
        """
        if self.row_being_edited == -1:
            self.save_to_database()
        else:
            editing_entry: Entry = self.get_textboxes()
            # edit in the database
            self.database.edit_entry(editing_entry)
            # set the string in the textboxes inside the row
            self.view_table.table_rows[self.row_being_edited].set_text(editing_entry.name, DataType.NAME)
            self.view_table.table_rows[self.row_being_edited].set_text(editing_entry.date, DataType.DATE)
            self.view_table.table_rows[self.row_being_edited].set_text(editing_entry.book_of_bible, DataType.BOOK)
            self.view_table.table_rows[self.row_being_edited].set_text(editing_entry.main_character_or_event, DataType.EVENT)
            self.view_table.table_rows[self.row_being_edited].set_text(editing_entry.standingout_verse, DataType.VERSE)
            self.view_table.table_rows[self.row_being_edited].set_text(editing_entry.time_spent_min, DataType.TIME)
            self.view_table.table_rows[self.row_being_edited].set_text(editing_entry.practical_action, DataType.ACTION)

            self.row_being_edited = -1
        # focus on the view data tab
        self.tabController.select(self.viewDatabaseTab)

        #hide cancel button
        self.clear_textboxes()
    
    def cancel_action(self, *args):
        """
        Method to switch to view tab when cancel is clicked
        """
        self.row_being_edited = -1
        # hide cancel button
        self.clear_textboxes()
        self.tabController.select(self.viewDatabaseTab)

    def save_to_database(self) -> None:
        """
        Method to save entry to database row
        """
        #use the text from the textbox to create an entry for the database
        database_Entry: Entry = self.get_textboxes()

        #add the entry to the database
        self.database.add_entry(database_Entry)

        #update table row with the info from the inbox
        self.view_table.table_rows.append(Table_Row(self.view_table.table_frame, len(self.view_table.table_rows), database_Entry, self))

#instance of the main class
if __name__ == "__main__":
    gui = GUI()