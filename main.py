import sys
from PyQt6.QtWidgets import QApplication
from src.game import RPGGame

def main():
    app = QApplication(sys.argv)
    game = RPGGame()
    game.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()