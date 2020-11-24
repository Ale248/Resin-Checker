from tkinter import *
from tkinter import messagebox
from tkinter.font import Font
from threading import Thread
import os
import shelve
import time
import datetime

# Time until next resin in seconds (8 minutes)
NEXT_RESIN_TIME = 5

# Max resin number (currently 160)
MAX_RESIN = 160

# Max resin time (max resin is 160, and each resin takes 8 minutes)
MAX_RESIN_TIME = MAX_RESIN * NEXT_RESIN_TIME

class Window(Frame):
    def __init__(self, master):
        """Class constructor.
        """
        # Change working directory to this directory
        os.chdir(os.path.dirname(sys.argv[0]))

        # Open file with shelve to retrieve data (if exists)
        self.dataFile = shelve.open('Resin_Data')

        self.BIG_FONT = Font(family='Helvetica', size=24)

        self.master = master
        self.master.title('Resin Checker')

        # Resin times
        self.nextResinTime = 0
        self.fullResinTime = 0

        # Variables
        self.resinString = StringVar()              # string for resin text
        self.nextResinString = StringVar()          # string for countdown to next resin
        self.fullResinString = StringVar()          # string for countdown to full resin
        self.resinNum = 0                           # initialize resin number
        self.secondsPassed = 0                      # initialize seconds passed

        # Update resin with according to time passed
        self.updateData()

        # Set default values to the respective strings
        self.resinString.set(str(self.resinNum))
        self.nextResinString.set(str(self.nextResinTime))
        self.fullResinString.set(str(self.fullResinTime))

        # Resin Spinbox
        self.up_or_down_func = self.master.register(self.up_or_down)
        self.resinSpinbox = Spinbox(master, from_=0, to=MAX_RESIN, state='readonly',
            repeatdelay=500, repeatinterval=50, textvariable=self.resinString, command=(self.up_or_down_func, '%d'),
            font=self.BIG_FONT)
        self.resinSpinbox.grid(row=0, column=0)

        # Resin label (right of entry)
        self.resinLabel = Label(master, text='/160', font=self.BIG_FONT)
        self.resinLabel.grid(row=0, column=1)

        # -20 resin button
        self.useTwentyButton = Button(master, text='-20', command=lambda: self.useResin(20), font=self.BIG_FONT)
        self.useTwentyButton.grid(row=0, column=2)

        # -40 resin button
        self.useFortyButton = Button(master, text='-40', command=lambda: self.useResin(40), font=self.BIG_FONT)
        self.useFortyButton.grid(row=0, column=3)

        # -60 resin button
        self.useSixtyButton = Button(master, text='-60', command=lambda: self.useResin(60), font=self.BIG_FONT)
        self.useSixtyButton.grid(row=0, column=4)

        # +60 resin button
        self.getSixtyButton = Button(master, text='+60', command=lambda: self.useResin(-60), font=self.BIG_FONT)
        self.getSixtyButton.grid(row=0, column=5)

        # 'Next resin' label
        self.nextResinLabel = Label(master, text='Next resin in: ', font=self.BIG_FONT)
        self.nextResinLabel.grid(row=1, column=0, columnspan=6)

        # Next resin entry
        self.nextResinEntry = Entry(master, textvariable=self.nextResinString, font=self.BIG_FONT)
        self.nextResinEntry.grid(row=2, column=0, columnspan=6)

        # 'Full resin' label
        self.fullResinLabel = Label(master, text='Full resin in: ', font=self.BIG_FONT)
        self.fullResinLabel.grid(row=3, column=0, columnspan=6)

        # Full resin entry
        self.fullResinEntry = Entry(master, textvariable=self.fullResinString, font=self.BIG_FONT)
        self.fullResinEntry.grid(row=4, column=0, columnspan=6)

        # Start a thread for next resin countdown
        # daemon=True means, when the main thread (window) dies, also terminate the thread
        self.nextResin_thread = Thread(target=self.nextResinCountdown, daemon=True)
        self.nextResin_thread.start()

        # Start a thread for full resin countdown
        self.fullResin_thread = Thread(target=self.fullResinCountdown, daemon=True)
        self.fullResin_thread.start()

        # Run self.onclosing() when application is closed
        self.master.protocol('WM_DELETE_WINDOW', self.on_closing)


    def updateData(self):
        """Updates resin and how much time has passed in seconds using Resin_Data files.
        """
        if all(key in list(self.dataFile.keys()) for key in ['lastResin', 'lastTime']):
            currentTime = datetime.datetime.now().replace(microsecond=0)
            lastTime = self.dataFile['lastTime']
            lastResin = self.dataFile['lastResin']

            # Calculates how much time has passed
            timeDelta = currentTime - lastTime

            # Converts timeDelta to seconds
            secondsPassed = 0
            secondsPassed += timeDelta.days * 86400
            secondsPassed += timeDelta.seconds

            # Calculates how much resin gained and how many seconds need to be deducted
            # from current countdown
            resinGain, self.secondsPassed = divmod(secondsPassed, NEXT_RESIN_TIME)

            # Update resin
            self.resinNum = lastResin + resinGain


    def on_closing(self):
        """Updates Resin_Data files upon closing.
        """
        self.dataFile['lastResin'] = self.resinNum

        # Ignore microseconds
        self.dataFile['lastTime'] = datetime.datetime.now().replace(microsecond=0)
        self.dataFile['lastNextRemaining'] = self.nextResinTime
        self.dataFile['lastFullRemaining'] = self.fullResinTime

        self.dataFile.close()
        self.master.destroy()


    def up_or_down(self, direction):
        """Updates current variables according to which button is pressed on the Spinbox.

        Keyword arguments:
        direction -- the direction of Spinbox button pushed ('up' or 'down')
        """
        oldResin = self.resinNum
        newResin = 0

        if (direction == 'up'):
            self.fullResinTime -= NEXT_RESIN_TIME
            newResin = oldResin + 1
        else:
            self.fullResinTime += NEXT_RESIN_TIME
            newResin = oldResin - 1

        self.resinNum = newResin


    def useResin(self, resin):
        """Update the resin and countdown according to how much resin is used.

        Keyword arguments:
        resin -- the amount of resin used
        """
        currentResin = self.resinNum
        newResin = currentResin - resin
        if newResin < 0:
            newResin = 0
        if newResin >= MAX_RESIN:
            newResin = MAX_RESIN

        self.fullResinTime += NEXT_RESIN_TIME * resin

        # Set the upper bound for full resin countdown
        if self.fullResinTime >= MAX_RESIN_TIME:
            self.fullResinTime = (MAX_RESIN_TIME - NEXT_RESIN_TIME) + self.nextResinTime

        self.resinNum = newResin
        self.resinString.set(str(self.resinNum))


    def fullResinCountdown(self):
        """Starts the countdown for full resin.
        """
        firstRun = True
        while True:
            currentResin = int(self.resinString.get())
            self.fullResinTime = (MAX_RESIN - currentResin) * NEXT_RESIN_TIME
            if 'lastFullRemaining' in list(self.dataFile.keys()) and firstRun:
                self.fullResinTime = self.dataFile['lastFullRemaining']
            self.fullResinTime -= self.secondsPassed

            if currentResin >= MAX_RESIN:
                continue

            while self.fullResinTime > -1:
                mins, secs = divmod(self.fullResinTime, 60)

                hours = 0
                if mins > 60:
                    hours, mins = divmod(mins, 60)

                timeString = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)
                self.fullResinString.set(timeString)

                self.master.update()
                time.sleep(1)

                if (self.fullResinTime == 0) or (int(self.resinString.get()) == MAX_RESIN):
                    messagebox.showinfo('Resin Checker', 'Resin is full!')
                    firstRun = False
                    break

                self.fullResinTime -= 1


    def nextResinCountdown(self):
        """Starts the countdown for next resin.
        """
        firstRun = True
        while True:
            self.nextResinTime = NEXT_RESIN_TIME
            if firstRun:
                self.nextResinTime = NEXT_RESIN_TIME - self.secondsPassed
                if 'lastNextRemaining' in list(self.dataFile.keys()):
                    self.nextResinTime = self.dataFile['lastNextRemaining'] - self.secondsPassed

            if self.resinNum >= MAX_RESIN:
                continue

            while self.nextResinTime > -1:
                mins, secs = divmod(self.nextResinTime, 60)

                hours = 0
                if mins > 60:
                    hours, mins = divmod(mins, 60)

                timeString = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)
                self.nextResinString.set(timeString)

                self.master.update()
                time.sleep(1)

                if self.resinNum == MAX_RESIN:
                    break

                if (self.nextResinTime == 0):
                    self.resinNum += 1
                    self.resinString.set(str(self.resinNum))
                    break

                self.nextResinTime -= 1

            firstRun = False

if __name__ == '__main__':
    window = Tk()

    windowWidth = 800
    windowHeight = 600

    # Display window in center of screen
    # -------------
    screenWidth = window.winfo_screenwidth()
    screenHeight = window.winfo_screenheight()

    positionRight = int(screenWidth/2 - windowWidth/2)
    positionDown = int(screenHeight/2 - windowHeight/2)

    window.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, positionRight, positionDown))
    # -------------

    app = Window(window)
    window.mainloop()
