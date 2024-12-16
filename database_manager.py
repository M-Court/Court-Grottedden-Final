import sqlite3

"""

Sorry, I find it easier to create the idea than the pseudocode, so I kinda swapped it around
I created this then the pseudo code, I can create comments and make it easier to understand soon

Its pretty simple 👍
no problem! :) -mc

"""




class Entry:
    """
    Class that holds the data of a singular entry in a table 
    """
    def __init__(self, name: str, date: str, book_of_bible: str, main_character_or_event: str, standingout_verse: str, time_spent_min: int, practical_action: str, id: int = -1) -> None:
        self.id: int = id # -1 means not determined
        self.name: str = name
        self.date: str = date
        self.book_of_bible: str = book_of_bible
        self.main_character_or_event: str = main_character_or_event
        self.standingout_verse: str = standingout_verse
        self.time_spent_min: int = time_spent_min
        self.practical_action: str = practical_action

    def get(self) -> tuple:
        return (self.name, self.date, self.book_of_bible, self.main_character_or_event, self.standingout_verse, self.time_spent_min, self.practical_action)

    def __str__(self) -> str: # split into multiple for easy reading
        out: str = f"Name: {self.name:<8} Date: {self.date:<15} Book: {self.book_of_bible:<8} Character or Event: {self.main_character_or_event:<15}"
        out += f"Verse: {self.standingout_verse:<50} Time spent: {self.time_spent_min} min\t Action: {self.practical_action:<30}"
        return out

class DatabaseConnection:
    def __init__(self) -> None:
        self.connection: sqlite3.Connection | None = sqlite3.connect('Faith_Walk.db')
        self.cursor: sqlite3.Cursor = self.connection.cursor()
        # create the table if it does not currently exist
        # can change structure later if needing more than one table
        self.cursor.execute("""CREATE table if not exists DailyBibleReading (
            id INTEGER primary key autoincrement, 
            name TEXT, 
            date TEXT, 
            book_of_bible TEXT,
            main_character_or_event TEXT,
            standingout_verse TEXT,
            time_spent INTEGER,
            practical_action TEXT
        )""")

    def add_entry(self, entry: Entry) -> None:
        if not self.connection: 
            # raise an exception if not connected to the database, 
            # could easily have a failsafe but it is best that we know there are errors
            raise Exception("ADD entry error: Not connected to database") 
        self.cursor.execute("INSERT into DailyBibleReading (name, date, book_of_bible, main_character_or_event, standingout_verse, time_spent, practical_action) VALUES (?, ?, ?, ?, ?, ?, ?)",
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


################# for easy debugging, TODO: remove when done ##############

    test_entry: Entry = Entry("Ray","November 12","Genesis","Creation","Genesis 1:1: \"In the beginning when God created the heavens and the earth\"",22,"An action")

    def clear_table(self) -> None: 
        self.cursor.execute("DELETE FROM DailyBibleReading")
        self.connection.commit()

#cool! i'll make i a test entry too...

    test_entry_2: Entry = Entry("Mackenzie", "December 1, "Luke", "Christmas", "Luke 2:11", "Unto us a Savior is born!", 15, "sing 'Hark the Harold'")



# test code
if __name__ == "__main__":
    connection: DatabaseConnection = DatabaseConnection()

    connection.clear_table()
    connection.add_entry(DatabaseConnection.test_entry)

    # print the first entry
    print(connection.get_entries()[0])
