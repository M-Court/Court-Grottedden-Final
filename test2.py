import tkinter
from main import *

# Create a table from the info in Faith Walk database
class Table:
    def __init__(self, window: tkinter.Tk, database: DatabaseConnection):

        # Create frame to hold the canvas and scrollbar
        self.canvas_frame = tkinter.Frame(window)
        self.canvas_frame.pack(fill=tkinter.BOTH, expand=True)

        # Create and pack the canvas
        self.canvas = tkinter.Canvas(self.canvas_frame)
        self.canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        # Create and pack the vertical scrollbar
        self.scrollbar = tkinter.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # Configure the canvas to work with the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas to hold the table
        self.table_frame = tkinter.Frame(self.canvas)
        
        # Add the table_frame to the canvas
        self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        # Bind the <Configure> event to update the scrollregion
        self.table_frame.bind("<Configure>", self.on_frame_configure)

        # Fetch table rows from the database
        self.table_rows: list[Entry] = database.get_entries()
        self.text_boxes: list[tkinter.Text] = []

        # Code for creating the table
        for row_index, entry in enumerate(self.table_rows):
            for column_index in range(7):
                cell = tkinter.Text(self.table_frame, width=11, height=2, wrap='word')
                cell.grid(row=row_index, column=column_index, padx=1, pady=1)
                cell.insert(tkinter.END, entry.get()[column_index])
                cell.config(state=tkinter.DISABLED)  # Make cells read-only if desired
                self.text_boxes.append(cell)

    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

# Create a tab for viewing the table
class TestGUI:
    def __init__(self) -> None:
        # Connect to the database
        self.database = DatabaseConnection()
        # Test entry
        self.database.add_entry(Entry("bob", "23 dec", "hello", 'asd', "dfssdf", "123", "egrghrdehd hello world there buddy"))
        for entry in self.database.get_entries():
            print(entry)

        # Create the main window
        self.window = tkinter.Tk()
        self.window.title("Faith Walk")
        self.window.config(bg='#ffffff')
        self.window.geometry('700x500')
        self.window.resizable(True, True)  # Allow resizing to better test scrollbars

        # Create the table
        self.table = Table(self.window, self.database)

        self.window.mainloop()

if __name__ == "__main__":
    gui = TestGUI()
