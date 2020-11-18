from tkinter import *
from tkinter import messagebox
from threading import Thread
import time

# time until next resin in seconds (8 minutes)
NEXT_RESIN = 5

# max resin number (currently 160)
MAX_RESIN = 160

class Window(Frame):
    def __init__(self, master):
        self.master = master
        self.master.title('Resin Checker')

        # Variables
        self.resinString = StringVar()
        self.nextResinString = StringVar()
        self.fullResinString = StringVar()

        # Set default values to variables
        self.resinString.set('150')
        self.nextResinString.set('00')
        self.fullResinString.set('00')

        # Resin entry
        # self.resinEntry = Entry(master, textvariable=self.resinString)
        # self.resinEntry.grid(row=0, column=0)

        self.resinSpinbox = Spinbox(master, from_=0, to=MAX_RESIN, state='readonly',
            repeatdelay=500, repeatinterval=50, textvariable=self.resinString)
        self.resinSpinbox.grid(row=0, column=0)

        # Resin label (right of entry)
        self.resinLabel = Label(master, text='/160')
        self.resinLabel.grid(row=0, column=1)

        # -20 resin button
        self.useTwentyButton = Button(master, text='-20', command=lambda: self.useResin(20))
        self.useTwentyButton.grid(row=0, column=2)

        # -40 resin button
        self.useFortyButton = Button(master, text='-40', command=lambda: self.useResin(40))
        self.useFortyButton.grid(row=0, column=3)

        # -60 resin button
        self.useSixtyButton = Button(master, text='-60', command=lambda: self.useResin(60))
        self.useSixtyButton.grid(row=0, column=4)

        # +60 resin button
        self.getSixtyButton = Button(master, text='+60', command=lambda: self.useResin(-60))
        self.getSixtyButton.grid(row=0, column=5)

        # 'Next resin' label
        self.nextResinLabel = Label(master, text='Next resin in: ')
        self.nextResinLabel.grid(row=1, column=0)

        # Next resin entry
        self.nextResinEntry = Entry(master, textvariable=self.nextResinString)
        self.nextResinEntry.grid(row=2, column=0)

        # 'Full resin' label
        self.fullResinLabel = Label(master, text='Full resin in: ')
        self.fullResinLabel.grid(row=3, column=0)

        # Full resin entry
        self.fullResinEntry = Entry(master, textvariable=self.fullResinString)
        self.fullResinEntry.grid(row=4, column=0)

        # self.nextResinCountdown()
        # daemon=True means, when the main thread (window) dies, also terminate the thread
        self.nextResin_thread = Thread(target=self.nextResinCountdown, daemon=True)
        self.nextResin_thread.start()

        self.fullResin_thread = Thread(target=self.fullResinCountdown, daemon=True)
        self.fullResin_thread.start()


        # self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def useResin(self, resin):
        currentResin = int(self.resinSpinbox.get())
        newResin = currentResin - resin
        if newResin < 0:
            newResin = 0

        if newResin >= MAX_RESIN:
            newResin = MAX_RESIN
        self.resinString.set(str(newResin))

    def startCountdown(self):
        # while True:
        #     currentResin = int(self.resinSpinbox.get())
        #     resinUntilFull = MAX_RESIN - currentResin
        #
        #     timeUntilNext = NEXT_RESIN
        #     timeUntilFull = (MAX_RESIN - currentResin) * NEXT_RESIN
        #
        #     if currentResin >= MAX_RESIN:
        #         break
        #
        #     while timeUntilFull > -1:
        return 0

    def fullResinCountdown(self):
        while True:
            currentResin = int(self.resinSpinbox.get())
            timeUntilFull = (MAX_RESIN - currentResin) * NEXT_RESIN

            if currentResin >= MAX_RESIN:
                break

            while timeUntilFull > -1:
                newResin = int(self.resinSpinbox.get()) - currentResin
                if newResin != 0:
                    break

                mins, secs = divmod(timeUntilFull, 60)

                hours = 0
                if mins > 60:
                    hours, mins = divmod(mins, 60)

                timeString = ''
                timeString += "{0:2d}".format(hours)
                timeString += ':'
                timeString += "{0:2d}".format(mins)
                timeString += ':'
                timeString += "{0:2d}".format(secs)
                self.fullResinString.set(timeString)

                self.master.update()
                time.sleep(1)

                if (timeUntilFull == 0) or int(self.resinSpinbox.get()) == MAX_RESIN:
                    messagebox.showinfo('Resin Checker', 'Resin is full!')

                timeUntilFull -= 1

    def nextResinCountdown(self):
        while True:
            timeRemaining = NEXT_RESIN
            # currentResin = int(self.resinString.get())
            currentResin = int(self.resinSpinbox.get())

            if currentResin >= MAX_RESIN:
                break

            while timeRemaining > -1:
                mins, secs = divmod(timeRemaining, 60)

                hours = 0
                if mins > 60:
                    hours, mins = divmod(mins, 60)

                timeString = ''
                timeString += "{0:2d}".format(hours)
                timeString += ':'
                timeString += "{0:2d}".format(mins)
                timeString += ':'
                timeString += "{0:2d}".format(secs)
                self.nextResinString.set(timeString)

                print(timeString)
                # currentResin = int(self.resinString.get())

                self.master.update()
                time.sleep(1)


                if int(self.resinSpinbox.get()) == MAX_RESIN:
                    break

                if (timeRemaining == 0):
                    currentResin += 1
                    # self.resinString.set(str(currentResin))
                    self.resinSpinbox.invoke('buttonup')
                    break

                timeRemaining -= 1


if __name__ == '__main__':
    window = Tk()

    windowWidth = 800
    windowHeight = 600

    # display window in center of screen
    # -------------
    screenWidth = window.winfo_screenwidth()
    screenHeight = window.winfo_screenheight()

    positionRight = int(screenWidth/2 - windowWidth/2)
    positionDown = int(screenHeight/2 - windowHeight/2)

    window.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, positionRight, positionDown))
    # -------------

    app = Window(window)
    window.mainloop()
