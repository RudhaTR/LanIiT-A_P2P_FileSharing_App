from gui import open_main_window
import db_utils
import sender,receiver,utils

if __name__ == "__main__":
    db_utils.initialize_tables()
    open_main_window()
