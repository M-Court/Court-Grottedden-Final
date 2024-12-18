import tkinter
from main import *

#create a table from the info in Faith Walk database
class Table:
    def __init__(self, window: tkinter.Tk, database: DatabaseConnection):

        #create frame to put table into
        self.canvas_frame = tkinter.Frame(window)
        #pack the frame
        self.canvas_frame.pack()

        #create and pack canvas for scrollbar
        self.canvas = tkinter.Canvas(self.canvas_frame)
        self.canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        
        #create and pack vertical scrollbar
        self.scrollbar = tkinter.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        #configure canvas to work with the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # place the table in the top left corner of the canvas
        self.canvas.create_window((0,0), window=self.canvas_frame, anchor="nw")

        #place the canvas in the frame
        self.table_frame = tkinter.Frame(self.canvas)
        

        self.table_rows: list[Entry] = database.get_entries()
        self.text_boxes: list[tkinter.Text] = []
        # code for creating table
        for row_in_table in range(len(self.table_rows)):
            for column_in_table in range(7):
                cell = tkinter.Text(self.table_frame, width=11, height=2, wrap='word')
                
                cell.grid(row=row_in_table, column=column_in_table)
                cell.insert(tkinter.END, self.table_rows[row_in_table].get()[column_in_table])

                self.text_boxes.append(cell)
        
        
        self.table_frame.pack(expand=True)
        
        # self.scrollbar = tkinter.Scrollbar(window, orient=tkinter.VERTICAL)
        # self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)


#create a tab for viewing table
class TestGUI:
    def __init__(self) -> None:
        #connect to the database
        self.database = DatabaseConnection()
        #test entry
        self.database.add_entry(Entry("bob", "23 dec", "hello", 'asd', "dfssdf", "123", "egrghrdehd hello world there buddy"))
        for entry in self.database.get_entries():
            print(entry)

        # create the main window
        self.window = tkinter.Tk()
        self.window.title("Faith Walk")
        self.window.config(bg='#ffffff')
        self.window.geometry('700x500')
        self.window.resizable(False, False)

        self.table = Table(self.window, self.database)

        self.window.mainloop()

if __name__ == "__main__":
    gui = TestGUI()