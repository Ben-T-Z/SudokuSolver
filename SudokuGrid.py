from PyQt5 import QtCore, QtGui, QtWidgets
import random


class Ui_SudokuGrid(object):
    def setupUi(self, SudokuGrid):
        SudokuGrid.setObjectName("SudokuGrid")
        SudokuGrid.resize(400, 450)
        self.gridLayout = QtWidgets.QGridLayout(SudokuGrid)
        self.gridLayout.setContentsMargins(20, 20, 20, 20)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")

        # Create a 9x9 grid of QLineEdit widgets
        self.cells = []
        self.initial_styles = []

        for row in range(9):
            row_cells = []
            row_styles = []

            for col in range(9):
                line_edit = QtWidgets.QLineEdit(SudokuGrid)
                line_edit.setMaximumSize(QtCore.QSize(40, 40))
                font = QtGui.QFont()
                font.setPointSize(12)
                line_edit.setFont(font)
                line_edit.setAlignment(QtCore.Qt.AlignCenter)
                line_edit.setObjectName(f"cell_{row}_{col}")

                # Set a validator to only allow integers between 1-9 (exclude 0)
                validator = QtGui.QRegExpValidator(QtCore.QRegExp("[1-9]"), line_edit)
                line_edit.setValidator(validator)

                # Limit input to 1 character
                line_edit.setMaxLength(1)

                # Style for thicker borders at specific rows and columns
                style = "border: 1px solid gray;"

                if row == 2 or row == 5:  # Bottom of 3rd and 6th rows (zero-indexed)
                    style += "border-bottom: 1.5px solid black;"
                if col == 2 or col == 5:  # Right of 3rd and 6th columns
                    style += "border-right: 1.5px solid black;"
                if row == 3 or row == 6:  # Top of 4th and 8th rows
                    style += "border-top: 1.5px solid black;"
                if col == 3 or col == 6:  # Left of 4th and 8th columns
                    style += "border-left: 1.5px solid black;"

                # Store the initial style
                row_styles.append(style)
                line_edit.setStyleSheet(style)

                self.gridLayout.addWidget(line_edit, row, col, 1, 1)
                row_cells.append(line_edit)
            
            self.cells.append(row_cells)
            self.initial_styles.append(row_styles)

        # Add a solve button below the grid
        self.solveButton = QtWidgets.QPushButton(SudokuGrid)
        self.solveButton.setText("Solve")
        self.solveButton.setObjectName("solveButton")
        self.gridLayout.addWidget(self.solveButton, 10, 0, 1, 9)  # Span across all columns
        self.solveButton.setStyleSheet("""margin-top: 5px;
                                       font-size: 16px;""")
        self.solveButton.setMinimumSize(200, 35)

        # Add a clear button below the grid
        self.clearButton = QtWidgets.QPushButton(SudokuGrid)
        self.clearButton.setText("Clear")
        self.gridLayout.addWidget(self.clearButton, 11, 0, 1, 9)  # Span across all columns
        self.clearButton.setStyleSheet("font-size: 16px;")
        self.clearButton.setMinimumSize(200, 30)


        self.retranslateUi(SudokuGrid)
        QtCore.QMetaObject.connectSlotsByName(SudokuGrid)

        # Initialize animation state
        self.animation_in_progress = False

    def retranslateUi(self, SudokuGrid):
        _translate = QtCore.QCoreApplication.translate
        SudokuGrid.setWindowTitle(_translate("SudokuGrid", "Sudoku Solver"))

    def solve_sudoku(self):
        """
        Solves the Sudoku puzzle by retrieving the grid values from the UI, checking for duplicates,
        and then using a backtracking algorithm to solve the puzzle. The solution process is animated.
        Once the puzzle is solved, the grid is updated with the solution and a message box is displayed.

        Steps:
        1. Retrieve the grid values from the UI.
        2. Check for duplicates in the grid. If duplicates are found, the solving process is aborted.
        3. Start an animation to show that the algorithm is working.
        4. Use a backtracking algorithm to solve the grid.
        5. If solved, stop the animation and update the UI with the solution. Show a success message.
        6. If unable to solve, display a warning message.
        """
        grid_values = []
        original_values = []

        # Step 1: Retrieve the grid values from the UI
        for row in range(9):
            row_values = []
            original_row = []
            for col in range(9):
                value = self.cells[row][col].text()
                if value == "":
                    value = "0"
                    original_row.append(0)
                else:
                    original_row.append(int(value))
                row_values.append(int(value))
            grid_values.append(row_values)
            original_values.append(original_row)

        self.original_values = original_values

        # Step 2: Check for duplicates before starting the solving process
        if self.find_duplicates():
            return  # If duplicates are found, stop the solving process

        # Step 3: Start animation to indicate the algorithm is working
        self.start_animation(grid_values, original_values)

        # Step 4: Run the solving algorithm in the background
        solved = self.solve(grid_values)

        # Step 5: Once solved, stop the animation and update the grid with the solution
        if solved:
            QtCore.QTimer.singleShot(1000, lambda: self.stop_animation_and_show_solution(grid_values))
        else:
            QtWidgets.QMessageBox.warning(None, "Error", "Unable to solve the Sudoku puzzle!")


    def stop_animation_and_show_solution(self, grid_values):
        """
        Stops the animation and updates the grid with the solved values.

        This method stops the solving animation and applies a ripple effect
        by changing the background color of the center subgrid before displaying the solution.
        """
        # Stop the animation timer
        self.timer.stop()

        # Update the grid with the solved values
        self.update_grid_with_solution(grid_values)

        # Start the ripple animation effect from the center subgrid
        self.start_ripple_effect()

    def start_ripple_effect(self):
        """
        Starts a ripple animation effect beginning at the center cell (the 41st square)
        and expanding outward in concentric rings. The effect is staggered by one phase:
        when the center cell is in a later phase, its neighbors are one phase behind.
        
        Each cell follows a 4-phase sequence:
        Phase 0: Light green (#a8f0a2) and font size 13
        Phase 1: Dark green (#4caf50) and font size 14
        Phase 2: Light green (#a8f0a2) and font size 13
        Phase 3: Reset to original style and font size 12
        """
        center = 4
        layers = {}
        for i in range(9):
            for j in range(9):
                d = max(abs(i - center), abs(j - center))
                layers.setdefault(d, []).append((i, j))
        
        # Create a sorted list of layers (layer 0 is the center, layer 1 its neighbors, etc.)
        ripple_layers = [layers[d] for d in sorted(layers.keys())]
        
        phase_delay = 100
        
        # Define the phase sequence as tuples: (phase offset, color, font size)
        # When color is None the cell resets.
        color_sequence = [
            (0, '#a8f0a2', 16),  # Phase 0: Light green, font size 13
            (1, '#4caf50', 20),  # Phase 1: Dark green, font size 14
            (2, '#a8f0a2', 16),  # Phase 2: Light green, font size 13
            (3, None, 12)       # Phase 3: Reset to original style and font size 12
        ]
        
        # Schedule the animation for each layer with an offset of one phase per layer.
        for layer_index, cells in enumerate(ripple_layers):
            for phase_offset, color, font_size in color_sequence:
                # Calculate the delay as the sum of the layer offset and the phase offset.
                delay = (layer_index + phase_offset) * phase_delay
                # Use lambda defaults to capture the current values of cells, color, and font_size.
                QtCore.QTimer.singleShot(
                    delay,
                    lambda cells=cells, color=color, font_size=font_size: self.apply_ripple(cells, color, font_size)
                )


    def apply_ripple(self, cells, color, font_size):
        """
        Applies a given background color and font size to a list of cells.
        If color is None, resets each cell to its original style and font size (12).
        
        Args:
        - cells (list of tuples): List of (row, col) pairs for the cells to update.
        - color (str or None): The background color to apply (e.g., '#a8f0a2'). If None, the cell style is reset.
        - font_size (int): The font size to set.
        """
        for i, j in cells:
            if color is None:
                # Reset to the original style stored during setup.
                self.cells[i][j].setStyleSheet(self.initial_styles[i][j])
                self.cells[i][j].setFont(QtGui.QFont("Arial", 12))
            else:
                # Apply the new background color and font size.
                # Append the original style for borders, etc.
                new_style = f"background-color: {color}; font-size: {font_size}pt;" + self.initial_styles[i][j]
                self.cells[i][j].setStyleSheet(new_style)
                
                # Also update the cell's font explicitly.
                font = self.cells[i][j].font()
                font.setPointSize(font_size)
                self.cells[i][j].setFont(font)



    def update_grid_with_solution(self, grid_values):
        """
        Updates the UI grid with the solved Sudoku values.

        This method sets the text of each grid cell to the corresponding solved value from the
        grid_values array. It is called once the puzzle is solved.

        Args:
        - grid_values: A 2D list representing the solved Sudoku grid.
        """
        # Update the grid cells with the solution after the algorithm completes
        for row in range(9):
            for col in range(9):
                self.cells[row][col].setText(str(grid_values[row][col]))  # Set the solved value

    def update_grid(self):
        """
        Updates the grid with the next set of values during the solving animation.

        This method is called periodically by the animation timer. It increments the current value
        of the empty cells in the grid and updates the UI with the new values. If all cells have been filled,
        the animation stops and the solution is displayed.
        """

        if not self.animation_in_progress:
            return  # Prevent any further updates if the solving process is complete

        all_filled = True

        # Loop through the grid and cycle the values
        for row in range(9):
            for col in range(9):
                if self.original_values[row][col] == 0:  # Only animate empty cells
                    current_value = self.animation_values[row][col]

                    # Increment the value and loop back to 1 after 9
                    new_value = current_value + 1 if current_value < 9 else 1
                    self.animation_values[row][col] = new_value  # Increment the value

                    # Update the QLineEdit widget with the new value
                    self.cells[row][col].setText(str(new_value))

                    # If this cell still needs to be updated, mark it as not filled
                    if new_value != 1:
                        all_filled = False



    def start_animation(self, grid_values, original_values):
        """
        Starts the animation that visually simulates the Sudoku solving process.

        This method initializes the grid with random values for animation and sets up a timer that periodically
        updates the grid. It also flags that the animation is in progress.

        Args:
        - grid_values: A 2D list representing the initial grid values.
        - original_values: A 2D list representing the original, unsolved grid values (before solving starts).
        """
        # Store the grid values so that we can modify them
        self.grid_values = grid_values
        self.original_values = original_values

        # Initialize the random values for animation (1-9)
        self.animation_values = [[random.randint(1, 9) if self.original_values[row][col] == 0 else self.original_values[row][col]
                                for col in range(9)] for row in range(9)]

        # Create a QTimer to update the grid every 0.2 seconds
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_grid)  # Connect the timeout to the update_grid method
        self.timer.start(20)  # 200ms = 0.2 seconds

        # Set animation in progress flag
        self.animation_in_progress = True


    def solve(self, grid):
        """
        Solves the Sudoku puzzle using the backtracking algorithm.

        This method recursively attempts to fill the grid using a backtracking approach, where it places a valid number
        in each empty cell and backtracks if it encounters an invalid state.

        Args:
        - grid: A 2D list representing the current state of the Sudoku grid.

        Returns:
        - True if the puzzle is successfully solved, False otherwise.
        """
        def is_valid(num, row, col):
            # Check row
            if num in grid[row]:
                return False

            # Check column
            for r in range(9):
                if grid[r][col] == num:
                    return False

            # Check 3x3 subgrid
            start_row, start_col = 3 * (row // 3), 3 * (col // 3)
            for r in range(start_row, start_row + 3):
                for c in range(start_col, start_col + 3):
                    if grid[r][c] == num:
                        return False
            return True

        def backtrack():
            for row in range(9):
                for col in range(9):
                    if grid[row][col] == 0:  # Find an empty cell
                        for num in range(1, 10):
                            if is_valid(num, row, col):
                                grid[row][col] = num  # Try placing the number

                                if backtrack():  # Recursively attempt to solve
                                    return True
                                grid[row][col] = 0  # Undo if not valid
                        return False  # No valid number found, backtrack
            return True  # Solved

        return backtrack()


    def find_duplicates(self):
        """
        Checks the Sudoku grid for duplicate values in rows, columns, or subgrids.

        This method scans the grid for any duplicates and flashes the corresponding row, column, or subgrid
        if a duplicate is found. If any duplicates are detected, the method stops the solving process and
        returns True. Otherwise, it returns False.

        Returns:
        - True if duplicates are found, False if no duplicates are detected.
        """
        # Check rows for duplicates
        for row in range(9):
            row_values = set()
            for col in range(9):
                value = self.original_values[row][col]
                if value != 0:
                    if value in row_values:
                        self.flash_row(row)  # Flash the row
                        return True  # Duplicate found, return True
                    row_values.add(value)

        # Check columns for duplicates
        for col in range(9):
            col_values = set()
            for row in range(9):
                value = self.original_values[row][col]
                if value != 0:
                    if value in col_values:
                        self.flash_column(col)  # Flash the column
                        return True  # Duplicate found, return True
                    col_values.add(value)

        # Check 3x3 subgrids for duplicates
        for row in range(0, 9, 3):
            for col in range(0, 9, 3):
                subgrid_values = set()
                for i in range(3):
                    for j in range(3):
                        value = self.original_values[row + i][col + j]
                        if value != 0:
                            if value in subgrid_values:
                                self.flash_subgrid(row, col)  # Flash the subgrid
                                return True  # Duplicate found, return True
                            subgrid_values.add(value)

        return False  # No duplicates found


    def clear_sudoku(self):
        for row in self.cells:
            for cell in row:
                cell.clear()

    def flash_row(self, row):
        # Flash the row 3 times
        for i in range(3):  # Flash 3 times
            QtCore.QTimer.singleShot(i * 500, lambda i=i: self.set_row_background(row, 'salmon' if i % 2 == 0 else 'white'))
        QtCore.QTimer.singleShot(3 * 500, lambda: self.reset_row_background(row))  # Reset after the third flash

    def flash_column(self, col):
        # Flash the column 3 times
        for i in range(3):
            QtCore.QTimer.singleShot(i * 500, lambda i=i: self.set_column_background(col, 'salmon' if i % 2 == 0 else 'white'))
        QtCore.QTimer.singleShot(3 * 500, lambda: self.reset_column_background(col))  # Reset after the third flash

    def flash_subgrid(self, row, col):
        # Flash the subgrid 3 times
        for i in range(3):
            QtCore.QTimer.singleShot(i * 500, lambda i=i: self.set_subgrid_background(row, col, 'salmon' if i % 2 == 0 else 'white'))
        QtCore.QTimer.singleShot(3 * 500, lambda: self.reset_subgrid_background(row, col))  # Reset after the third flash

    def set_row_background(self, row, color):
        # Set the row background to the error colour (salmon)
        for col in range(9):
            self.cells[row][col].setStyleSheet(f"background-color: {color};")

    def set_column_background(self, col, color):
        # Set the column background to the error colour (salmon)
        for row in range(9):
            self.cells[row][col].setStyleSheet(f"background-color: {color};")

    def set_subgrid_background(self, row, col, color):
        # Set the subgrid background to the error colour (salmon)
        for i in range(3):
            for j in range(3):
                self.cells[row + i][col + j].setStyleSheet(f"background-color: {color};")

    def reset_row_background(self, row):
        # Reset the row background to the initial style
        for col in range(9):
            self.cells[row][col].setStyleSheet(self.initial_styles[row][col])

    def reset_column_background(self, col):
        # Reset the column background to the initial style
        for row in range(9):
            self.cells[row][col].setStyleSheet(self.initial_styles[row][col])

    def reset_subgrid_background(self, row, col):
        # Reset the subgrid background to the initial style
        for i in range(3):
            for j in range(3):
                self.cells[row + i][col + j].setStyleSheet(self.initial_styles[row + i][col + j])



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    SudokuGrid = QtWidgets.QWidget()
    ui = Ui_SudokuGrid()
    ui.setupUi(SudokuGrid)
    SudokuGrid.show()
    sys.exit(app.exec_())
