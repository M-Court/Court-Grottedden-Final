import tkinter as Tk
from tkinter import ttk, font
import sqlite3

############################## #1 THE VIEW TAB ###################################

#Class that holds the data of a singular entry in table
class Entry:
    def __init__(self, name: str, date: str, book_of_bible: str, main_character_or_event: str, standingout_verse: str, time_spent_min: str, practical_action: str, id: int = -1) -> None:
        #create fields
        self.id: int = id # -1 means not determined
        self.name: str = name
        self.date: str = date
        self.book_of_bible: str = book_of_bible
        self.main_character_or_event: str = main_character_or_event
        self.standingout_verse: str = standingout_verse
        self.time_spent_min: str = time_spent_min
        self.practical_action: str = practical_action

    def get(self) -> tuple:
        return (self.name, self.date, self.book_of_bible, self.main_character_or_event, self.standingout_verse, self.time_spent_min, self.practical_action)

    def __str__(self) -> str: # split into multiple for easy reading
        out: str = f"Name: {self.name:<8} Date: {self.date:<15} Book: {self.book_of_bible:<8} Character or Event: {self.main_character_or_event:<15}"
        out += f"Verse: {self.standingout_verse:<50} Time spent: {self.time_spent_min} min\t Action: {self.practical_action:<30}"
        return out

#connect to database
class DatabaseConnection:
    def __init__(self) -> None:
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
        if not self.connection: 
            # raise an exception if not connected to the database, 
            # could easily have a failsafe but it is best that we know there are errors
            raise Exception("ADD entry error: Not connected to database") 
        self.cursor.execute("INSERT into DailyBibleReading (name_row, date_row, book_row, event_row, verse_row, time_row, action_row) VALUES (?, ?, ?, ?, ?, ?, ?)",
            entry.get()
        )
        self.connection.commit()

    def get_entries(self) -> list[Entry]:
        if not self.connection: 
            # raise an exception if not connected to the database
            raise Exception("GET entries error: Not connected to database") 
        self.cursor.execute('SELECT * FROM DailyBibleReading')
        rows = self.cursor.fetchall()
        table: list[Entry] = []
        for row in rows:
            table.append(Entry(row[1], row[2], row[3], row[4], row[5], row[6], row[7], id=row[0]))

        return table

    def reconnect(self) -> None:
        if self.connection: 
            # raise an exception if already connected to the database
            raise Exception("Reconnect error: Already connected to database") 
        self.connection = sqlite3.connect('Faith_Walk.db')

    def disconnect(self, commit: bool = False) -> None:
        if not self.connection: 
            # raise an exception if not connected to the database
            raise Exception("Disconnect error: Not connected to database") 
        if commit:
            self.connection.commit()
        self.connection.close()
        self.connection = None


    ################# for easy debugging, TODO: remove when done #######???

    def clear_table(self) -> None: 
        self.cursor.execute("DELETE FROM DailyBibleReading")
        self.connection.commit()

    ############################class for adding an entry######???


#create table 
class Table:
    def __init__(self, window: Tk.Tk, database: DatabaseConnection):

        # Create frame to hold the canvas and scrollbar
        self.canvas_frame = Tk.Frame(window)
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
        self.table_rows: list[Entry] = database.get_entries()
        self.text_boxes: dict[int, list[Tk.Text]] = {}

        # Code for creating the table
        for row_index, entry in enumerate(self.table_rows):
            for column_index in range(7):
                cell = Tk.Text(self.table_frame, width=11, height=2, wrap='word')
                cell.grid(row=row_index, column=column_index, padx=1, pady=1)
                cell.insert(Tk.END, entry.get()[column_index])
                cell.config(state=Tk.DISABLED)  # Make cells read-only if desired
                self.text_boxes.append(cell)


    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


##################################2 THE UPDATE TAB#######################################

class GUI:
    def __init__(self):
        #connect to database
        self.database = DatabaseConnection()

        # create the main window
        self.window = Tk.Tk()
        self.window.title("Faith Walk")
        self.window.config(bg='#1e2124')
        self.window.geometry('700x500')
        self.window.resizable(False, False)

        #create the Update tab
        self.tabController = ttk.Notebook(self.window)
        self.viewDatabaseTab = ttk.Frame(self.tabController)
        self.changeDatabaseTab = ttk.Frame(self.tabController)
        self.tabController.add(self.viewDatabaseTab, text ='View')
        self.tabController.add(self.changeDatabaseTab, text ='Update')
        self.tabController.pack(expand=1, fill="both")

#------------------CHANGE Database Tab---------------------

        #pack labels in top frame
        self.left_frame = ttk.Frame(self.changeDatabaseTab)
        self.right_frame = ttk.Frame(self.changeDatabaseTab)
        self.top_frame = ttk.Frame(self.changeDatabaseTab)
        self.bottom_frame = ttk.Frame(self.changeDatabaseTab)

#----------------grid------------------
#use grid to pack labels, textboxes, and edit buttons packed side-by-side
        self.left_frame.grid(row=1, column=0, sticky="nsew")
        self.right_frame.grid(row=1, column=1, sticky="nsew")
        self.top_frame.grid(row=0, column=1, sticky="nsew")
        self.bottom_frame.grid(row=2, column=1, sticky="nsew")
        
        #RAYMOND ---- add edit buttons to grid

#TOP FRAME----------------------------
        #create and pack title, subtitle
        self.title_label = Tk.Label(self.top_frame, text='FAITH WALK...', font=font.Font(size = 30))
        self.subtitle_label = Tk.Label(self.top_frame, text='keeping track of your daily discipleship', font=font.Font(size = 12))
        self.ID_button = Tk.Label(self.top_frame, text='the ID for this row is {table_ID}', font=font.Font(size = 12))

        self.title_label.pack()
        self.subtitle_label.pack()
        self.ID_button.pack(side='right')

        #variable to change font size
        self.label_size: font = font.Font(size=20)

#LEFT FRAME--------------------------
        self.name_label = ttk.Label(self.left_frame, text='Name: ', font=self.label_size, width=5)
        self.date_label = ttk.Label(self.left_frame, text='Date: ', font=self.label_size, width=5)
        self.book_label = ttk.Label(self.left_frame, text='Book: ', font=self.label_size, width=5)
        self.event_label = ttk.Label(self.left_frame, text='Event: ', font=self.label_size, width=5)
        self.verse_label = ttk.Label(self.left_frame, text='Verse: ', font=self.label_size, width=5)
        self.time_label = ttk.Label(self.left_frame, text='Time: ', font=self.label_size, width=5)
        self.action_label = ttk.Label(self.left_frame, text='Action: ', font=self.label_size, width=5)

        #pack the textbox widgets into the left frame
        self.name_box.pack()
        self.date_box.pack()
        self.book_box.pack()
        self.event_box.pack()
        self.verse_box.pack()
        self.time_box.pack()
        self.action_box.pack()

#RIGHT FRAME-----------------
        #create textbox widgets
        self.name_box = Tk.Text(self.right_frame, width=70, height=2)
        self.date_box = Tk.Text(self.right_frame, width=70, height=2)
        self.book_box = Tk.Text(self.right_frame, width=70, height=2)
        self.event_box = Tk.Text(self.right_frame, width=70, height=2)
        self.verse_box = Tk.Text(self.right_frame, width=70, height=2)
        self.time_box = Tk.Text(self.right_frame, width=70, height=2)
        self.action_box = Tk.Text(self.right_frame, width=70, height=2)

        #pack the labels into the right frame
        self.name_label.pack()
        self.date_label.pack()
        self.book_label.pack()
        self.event_label.pack()
        self.verse_label.pack()
        self.time_label.pack()
        self.action_label.pack()

#BOTTOM FRAME---------------
        #create the Submit and Cancel button
        self.submit_button = Tk.Button(self.bottom_frame, text='Submit', command=self.save_to_database, width=17, height=1, font=self.label_size)
        self.cancel_button = Tk.Button(self.buttom_frame, text='Cancel', command=self.cancel_entry, width=17, height=1, font=self.label_size)

        self.submit_button.pack(side='right')
        self.cancel_button.pack(side'right')

        #need comment here
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        #???
        self.view_table = Table(self.viewDatabaseTab, self.database)

#---------------MAINLOOP-----------------------
        #run mainloop
        self.window.mainloop()

#---------------METHODS------------------------

    #method for CANCEL button
    #to clear entry box and send you back to "View" tab
    def cancel_entry():
        #step 1 = clear textboxes

        #step 2 = send user back to the view tab
        
    #method for EDIT buttons
    def edit_entry():
        #step 1 = send user to Update tab

    #method for SUBMIT button
    #to save entry to database row
    def save_to_database(self) -> None:
        name_string: str = self.name_box.get("1.0", Tk.END)
        date_string: str = self.date_box.get("1.0", Tk.END)
        book_string: str = self.book_box.get("1.0", Tk.END)
        event_string: str = self.event_box.get("1.0", Tk.END)
        verse_string: str = self.verse_box.get("1.0", Tk.END)
        time_string: str = self.time_box.get("1.0", Tk.END)
        action_string: str = self.action_box.get("1.0", Tk.END)

     #method to disconnect from database
    def on_closing(self) -> None:
        self.database.disconnect()
        self.window.destroy()
   

#---------------------CREATE ENTRY-------------------

        #create an entry for database
        database_Entry = Entry(name_string, date_string, book_string, event_string, verse_string, time_string, action_string)
        #add entry to database
        self.database.add_entry(database_Entry)

        #??
        print(self.database.get_entries()[0])

        #update table with the information added to the database
        self.view_table.append(database_Entry)


#-----------------------INSTANCE----------------------------
#create an instance of the main class
if __name__ == "__main__":
    gui = GUI()

