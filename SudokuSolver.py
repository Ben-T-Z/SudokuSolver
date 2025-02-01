import sys
from PyQt5 import QtWidgets
from SudokuGrid import Ui_SudokuGrid

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Create the Sudoku window and set up the UI
    window = QtWidgets.QWidget()
    ui = Ui_SudokuGrid()
    ui.setupUi(window)  # Setup the UI for the window

    window.show()  # Show the window
    window.setFixedSize(window.size()) # Fix the window size

    ui.solveButton.clicked.connect(ui.solve_sudoku)
    ui.clearButton.clicked.connect(ui.clear_sudoku)

    sys.exit(app.exec_())  # Start the event loop

if __name__ == "__main__":
    main()
