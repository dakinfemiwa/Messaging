from tkinter import *
import tkinter.ttk
import json
import time
import socket
import _thread
import os
import Updater
import urllib.request
import random


class Client:
    @staticmethod
    def configure():
        global config, colourTheme, windowBackground, windowForeground
        global windowTitle, programVersion, programStage, windowResolution, windowFont

        with open('config.json') as jsonConfig:
            config = json.load(jsonConfig)

        # Config incorporation.
        colourTheme = config['window']['theme']
        windowResolution = config['window']['resolution']
        windowTitle = config['window']['title']
        windowForeground = config['window']['foreground']
        windowBackground = config['window']['background']
        windowFont = config['window']['font']

        programVersion = config['information']['version']
        programStage = config['information']['stage']

    @staticmethod
    def connect():

        global clientSocket, username, GameToken

        GameToken = 'NULL'

        print("WELCOME: Ready to connect.")
        print("INFO: Connecting to ", str(IP) + ":" + str(PORT))
        username = str(input("INPUT: Enter username: "))

        if ADMIN_LEVEL > 0:
            USER_PERMISSIONS.extend((ADMIN_COMMAND_SYNTAX, ADMIN_MESSAGE_JOIN, ADMIN_MESSAGE_LEAVE))

        join_message = username + ' has joined the server' + ' [' + str(programVersion) + ']'
        final_name = '$$$' + username

        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            clientSocket.connect((IP, PORT))
            print("INFO: Sending client information...")
            clientSocket.send(str.encode(final_name))
            print("INFO: Connected to ", str(IP) + ':' + str(PORT))
            clientSocket.send(str.encode(join_message))

            _thread.start_new_thread(Manager.search, ())

            _thread.start_new_thread(Client.receive, ())
            _thread.start_new_thread(MainWindow.mainloop(), ())

        except:
            print('ERROR: Unable to connect to the requested server.')
            print('INFO: Server is most likely offline, check with control panel.')
            exit(1)

        try:
            while True:
                continue
        except:
            print("INFO: The client was forced to close.")
            clientSocket.close()

    @staticmethod
    def external(address, connection_name, connection_pass=None):
        global username, clientSocket, GameToken
        Window.draw()
        GameToken = 'NULL'

        if ADMIN_LEVEL > 0:
            USER_PERMISSIONS.extend((ADMIN_COMMAND_SYNTAX, ADMIN_MESSAGE_JOIN, ADMIN_MESSAGE_LEAVE))

        username = connection_name
        join_message = connection_name.strip('$').strip('%!') + ' has joined the server'
        final_name = '$$$' + connection_name

        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            clientSocket.connect(('127.0.0.1', PORT))
            clientSocket.send(str.encode(final_name))

            time.sleep(.5)
            if connection_pass != None:
                final_pass = '#!-' + connection_pass
                clientSocket.send(str.encode(final_pass))
            else:
                time.sleep(.5)
                clientSocket.send(str.encode(join_message))

            _thread.start_new_thread(Manager.search, ())

            _thread.start_new_thread(Client.receive, ())
            _thread.start_new_thread(MainWindow.mainloop(), ())

        except:
            print('ERROR: Could not connect.')
            try:
                Window.show('You have been disconnected from the server.')
            except:
                pass

    @staticmethod
    def close(self):
        pass

    @staticmethod
    def send(message, inGame=False):
        global isTurn
        if inGame is False:
            try:
                if message[0] == '.':
                    Client.command(message)
                else:
                    entryBox.delete(0, END)
                    send_msg = username.strip('%!') + ': ' + message
                    clientSocket.send(str.encode(send_msg))
            except TypeError:
                pass
            except IndexError:
                pass
        else:
            isTurn = False
            clientSocket.send(str.encode(message))

    @staticmethod
    def receive():
        global isTurn, hasStarted, myTeam, theirTeam, boardSection, boardSlotsStatic, boardValues, boardSlots
        global A1_VAL, A2_VAL, A3_VAL, B1_VAL, B2_VAL, B3_VAL, C1_VAL, C2_VAL, C3_VAL

        while True:
            try:
                receive_data = clientSocket.recv(4096)
            except:
                # When the server goes down.
                print("INFO: Server closed connection")
                try:
                    Window.show('The server has shutdown or is not responding to requests.')
                except:
                    pass
                _thread.interrupt_main()
                break
            if not receive_data:
                print("INFO: Server closed connection")
                try:
                    Window.show('The server has shutdown or is not responding to requests.')
                except:
                    pass
                _thread.interrupt_main()
                break
            else:
                if receive_data.decode() == '$-$quit':
                    MainWindow.destroy()
                    clientSocket.close()
                    _thread.interrupt_main()
                elif receive_data.decode() == '$-$clear':
                    ChatLog.config(state=NORMAL)
                    ChatLog.delete(1.0, END)
                    Window.show(CLEAR_MESSAGE_ADMIN)
                elif '-##-' in receive_data.decode():
                    adminLvl = receive_data.decode().strip('-##-')
                    adminLvl = int(adminLvl)
                    ADMIN_LEVEL = adminLvl
                    print('ADMIN LEVEL:', adminLvl)
                    if ADMIN_LEVEL > 0:
                        USER_PERMISSIONS.extend((ADMIN_COMMAND_SYNTAX, ADMIN_MESSAGE_JOIN, ADMIN_MESSAGE_LEAVE))
                    if ADMIN_LEVEL > 1:
                        USER_PERMISSIONS.extend((ADMIN_COMMAND_KICK, ADMIN_COMMAND_CLEARALL, ADMIN_COMMAND_MESSAGE))
                    if ADMIN_LEVEL > 2:
                        USER_PERMISSIONS.extend((ADMIN_COMMAND_RESTART, ADMIN_COMMAND_SHUTDOWN, ADMIN_COMMAND_FORCEQUIT,
                                                 ADMIN_COMMAND_GHOST))
                elif '$-$play' in receive_data.decode():
                    urllib.request.urlretrieve(
                        'https://raw.githubusercontent.com/dakinfemiwa/MESSAGING/unstable/song.mp3', 'song.mp3')
                    os.startfile('song.mp3')
                elif '/!-:' in receive_data.decode():
                    if GameToken not in receive_data.decode() and GameToken != 'NULL':
                        moveRec = receive_data.decode().strip('/!-:')
                        moveRec = moveRec[:-12]
                        Window.drawpanel(moveRec, 2)
                    Window.refresh()
                elif 'YOUR_TURN_+' in receive_data.decode():
                    if GameToken not in receive_data.decode() and GameToken != 'NULL':
                        isTurn = True
                    Window.refresh()

                elif '+!+:)' in receive_data.decode():
                    if GameToken not in receive_data.decode() and GameToken != 'NULL':
                        GameStateWaiting.place_forget()
                        GameStateInGame.place(relx=.88, rely=.05)
                        hasStarted = True
                        myTeam = 'O'
                        theirTeam = 'X'
                elif '+-+-+!' in receive_data.decode():
                    if GameToken not in receive_data.decode() and GameToken != 'NULL':
                        winNotify = receive_data.decode().strip('+-+-+!')
                        winNotify = winNotify[:-12]
                        # This user lost:
                        if winNotify == 'W':
                            GameStateInGame.place_forget()
                            GameStateGameOver.place(relx=.83, rely=.05)
                            Window.displaywinner(False)
                            isTurn = False
                        else:
                            GameStateInGame.place_forget()
                            GameStateGameOver.place(relx=.83, rely=.05)
                            Window.displaywinner(True)
                            isTurn = False

                else:
                    if "$" in receive_data.decode():
                        pass
                    else:
                        new = receive_data.decode().strip("%")
                        Window.show(new)

    @staticmethod
    def command(command):
        global username, clientSocket

        entryBox.delete(0, END)

        colours = [
            'blue', 'green', 'purple', 'yellow', 'red', 'orange', 'white', 'gray'
        ]

        try:
            if command == '.help':
                Window.show(HELP_MESSAGE)

            elif command == '.clear':
                ChatLog.config(state=NORMAL)
                ChatLog.delete(1.0, END)
                Window.show(CLEAR_COMMAND)

            elif '.name' in command:
                if len(command) < 7:
                    Window.show(NAME_COMMAND)
                else:
                    new_name = command[6:]
                    updated_name = username + ' has changed their name to ' + new_name
                    clientSocket.send(str.encode(updated_name))
                    MainWindow.after(500)
                    second_name = '$$$' + new_name
                    username = new_name
                    clientSocket.send(str.encode(second_name))

            elif command == '.about':
                Window.show(VERSION_MESSAGE)

            elif '.colour' in command:
                if len(command) < 9:
                    Window.show('The correct usage is .colour <colour>')
                else:
                    colour = command[8:]
                    if colour in colours:
                        if colour == 'white':
                            config['window']['theme'] = '#FFFFFF'
                        elif colour == 'red':
                            config['window']['theme'] = '#FF0000'
                        elif colour == 'blue':
                            config['window']['theme'] = '#00BFFF'
                        elif colour == 'green':
                            config['window']['theme'] = '#7CFC00'
                        elif colour == 'yellow':
                            config['window']['theme'] = '#FFFF00'
                        elif colour == 'purple':
                            config['window']['theme'] = '#8A2BE2'
                        elif colour == 'orange':
                            config['window']['theme'] = '#FF8C00'
                        elif colour == 'gray':
                            config['window']['theme'] = '#CCCCCC'

                        with open('config.json', 'w') as config_file:
                            config_file.write(json.dumps(config, indent=8))

                        Window.show('Theme colour was changed; restart client')
                    else:
                        Window.show('You selected an invalid colour')

            elif len(command) > 150:
                Window.show(SPAM_MESSAGE)

            elif command == '.quit':
                MainWindow.destroy()
                clientSocket.close()

            elif command == '.online':
                clientSocket.send(str.encode('$-$online'))

            elif command == '.fq':
                if has('admin.commands.forcequit'):
                    clientSocket.send(str.encode('$-$quit'))
                else:
                    Window.show(INSUFFICIENT_PERMISSIONS)

            elif command == '.ca':
                if has('admin.commands.clearall'):
                    clientSocket.send(str.encode('$-$clear'))
                else:
                    Window.show(INSUFFICIENT_PERMISSIONS)

            elif command == '.admin':
                if has('admin.commands.show'):
                    Window.show(ADMIN_MESSAGE)
                else:
                    Window.show(INSUFFICIENT_PERMISSIONS)

            elif '.ghost' in command:
                if has('admin.commands.ghost'):
                    if len(command) < 8:
                        Window.show(GHOST_COMMAND)
                    else:
                        target_user = command[7:]
                        final_string = '_-$' + target_user
                        clientSocket.send(str.encode(final_string))
                else:
                    Window.show(INSUFFICIENT_PERMISSIONS)

            elif command == '.restart':
                clientSocket.send(str.encode('$-$restart'))

            elif command == '.shutdown':
                clientSocket.send(str.encode('$-$shutdown'))

            elif '.message' in command:
                if len(command) < 10:
                    Window.show(MESSAGE_COMMAND)
                else:
                    target_user = command[9:]
                    final_string = '£££ ' + target_user
                    clientSocket.send(str.encode(final_string))

            elif '.kick' in command:
                if len(command) < 7:
                    Window.show(KICK_COMMAND)
                else:
                    target_user = command[6:]
                    final_string = '$$-' + target_user
                    clientSocket.send(str.encode(final_string))

            elif command == '.update':
                MainWindow.destroy()
                # clientSocket.close()
                Manager.search('FORCED')

            elif command == '.game':
                MainWindow.destroy()
                Window.gamescreen()

            else:
                Window.show('That is an invalid command')

        except:
            pass

    def disconnect(self):
        pass


class Window:
    @staticmethod
    def draw():
        global ChatLog, MainWindow, entryBox

        def press(event):
            entryBox.config(state=NORMAL)
            Client.send(entryBox.get())

        def disable(event):
            entryBox.config(state=DISABLED)

        MainWindow = Tk()
        MainWindow.configure(bg=windowBackground)
        MainWindow.geometry(windowResolution)
        MainWindow.title(windowTitle)
        MainWindow.attributes('-topmost', True)

        titleText = StringVar()
        titleText.set('C H A T')

        lineText = StringVar()
        lineText.set('___________________________________________________________________________')

        enterMessageText = StringVar()
        enterMessageText.set('M E S S A G E: ')

        buttonText = StringVar()
        buttonText.set(' ➤ ')

        settingsText = StringVar()
        settingsText.set('⚙️')

        versionText = StringVar()
        versionText.set('V E R S I O N  ' + programVersion)

        lineLabel = Label(MainWindow, textvariable=lineText, font='Arial 15 bold', fg=colourTheme, bg=windowBackground)
        lineLabel.place(relx=.04, rely=.14)

        titleLabel = Label(MainWindow, textvariable=titleText, font='Arial 20 bold', bg=windowBackground,
                           fg=windowForeground)
        titleLabel.place(relx=.04, rely=.09)

        enterMessageLabel = Label(MainWindow, textvariable=enterMessageText, font='Arial 13 bold', bg=windowBackground,
                                  fg=windowForeground)
        enterMessageLabel.place(relx=.04, rely=.85)

        entryBox = Entry(MainWindow, width=100)
        entryBox.place(relx=.18, rely=.855)

        entryBox.bind("<Return>", disable)
        entryBox.bind("<KeyRelease-Return>", press)

        entryBox.insert(END, '.help')

        sendButton = Button(MainWindow, textvariable=buttonText, font='Arial 7 bold', width=7, height=1,
                            command=lambda: press("<Return>"))
        sendButton.place(relx=.86, rely=.855)

        settingsButton = Button(MainWindow, textvariable=settingsText, font='Arial 7 bold', width=3, height=1,
                                command=lambda: Window.settings())
        settingsButton.place(relx=.927, rely=.855)

        versionLabel = Label(MainWindow, textvariable=versionText, font='Arial 11 bold', bg=windowBackground,
                             fg=colourTheme)
        versionLabel.place(relx=.08, rely=.17)

        ChatLog = Text(MainWindow, bd=1, bg="#141414", height="13", width="91", font="Arial")
        ChatLog.place(relx=.043, rely=.23)

    @staticmethod
    def gamescreen(GAME=1, START=1):
        global boardSlots, boardSlotsStatic, boardValues, myTeam, theirTeam, isTurn, hasStarted, oneTimeSetup, GameToken, Game
        global GameInteract, GameInteract2, GameInteract3, GameInteract4, GameInteract5, GameInteract6, GameInteract7, GameInteract8, GameInteract9, GameButtons
        global A1_VAL, A2_VAL, A3_VAL, B1_VAL, B2_VAL, B3_VAL, C1_VAL, C2_VAL, C3_VAL
        global GameItem, GameItem2, GameItem3, GameItem4, GameItem5, GameItem6, GameItem7, GameItem8, GameItem9
        global GameWinner, GameLoser, GameStateGameOver, GameStateWaiting, GameStateInGame

        GameToken = str(random.randint(100000000000, 999999999999))

        Game = Tk()
        Game.configure(bg=windowBackground)
        Game.geometry('800x400')
        Game.title('GAME')

        titleText = StringVar()
        titleVert = StringVar()
        titleHorz = StringVar()
        titleWait = StringVar()
        titleGame = StringVar()
        titleOver = StringVar()

        endWin = StringVar()
        endLose = StringVar()

        boardSlotsStatic = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
        boardSlots = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']

        A1_VAL = StringVar()
        A2_VAL = StringVar()
        A3_VAL = StringVar()
        B1_VAL = StringVar()
        B2_VAL = StringVar()
        B3_VAL = StringVar()
        C1_VAL = StringVar()
        C2_VAL = StringVar()
        C3_VAL = StringVar()

        A1_VAL.set('-')
        A2_VAL.set('-')
        A3_VAL.set('-')
        B1_VAL.set('-')
        B2_VAL.set('-')
        B3_VAL.set('-')
        C1_VAL.set('-')
        C2_VAL.set('-')
        C3_VAL.set('-')

        boardValues = [A1_VAL, A2_VAL, A3_VAL, B1_VAL, B2_VAL, B3_VAL, C1_VAL, C2_VAL, C3_VAL]

        oneTimeSetup = False

        def sendMove(moveSlot):
            global isTurn, hasStarted, myTeam, theirTeam, oneTimeSetup, boardSection, boardSlotsStatic, boardValues
            global GameItem, GameItem2, GameItem3, GameItem4, GameItem5, GameItem6, GameItem7, GameItem8, GameItem9
            global GameWinner, GameLoser

            if oneTimeSetup == False:
                if hasStarted is False:
                    myTeam = 'X'
                    theirTeam = 'O'
                    hasStarted = True
                    GameStateWaiting.place_forget()
                    GameStateInGame.place(relx=.88, rely=.05)
                    startGame = '+!+:)' + GameToken
                    Client.send(startGame, True)
                    time.sleep(.1)
                else:
                    GameStateWaiting.place_forget()
                    GameStateInGame.place(relx=.88, rely=.05)
                    myTeam = 'O'
                    theirTeam = 'X'
                oneTimeSetup = True

            Window.drawpanel(moveSlot, 1)

            moveSlot = '/!-:' + moveSlot + GameToken
            TurnOver = 'YOUR_TURN_+' + GameToken
            Client.send(moveSlot, True)
            time.sleep(.1)
            Client.send(TurnOver, True)
            Window.checkwinner()
            refreshBoard()

        if GAME == 1:
            titleText.set('TIC TAC TOE')
            titleVert.set('|')
            titleHorz.set('__________________________________________')
            titleWait.set('WAITING FOR GAME')
            titleGame.set('IN-GAME')
            titleOver.set('GAME OVER')

            endWin.set('WINNER')
            endLose.set('LOSER')

        if START == 1:
            isTurn = True
            hasStarted = False
        else:
            isTurn = False

        GameTitle = Label(Game, textvariable=titleText, font='Arial 12 bold', bg=windowBackground, fg='white')
        GameTitle.place(relx=.03, rely=.05)

        GameStateWaiting = Label(Game, textvariable=titleWait, font='Arial 12 bold', bg=windowBackground, fg='#95a5a6')
        GameStateWaiting.place(relx=.76, rely=.05)

        GameStateInGame = Label(Game, textvariable=titleGame, font='Arial 12 bold', bg=windowBackground, fg='#2ecc71')
        # GameStateInGame.place(relx=.88, rely=.05)

        GameStateGameOver = Label(Game, textvariable=titleOver, font='Arial 12 bold', bg=windowBackground, fg='#e74c3c')
        # GameStateGameOver.place(relx=.83, rely=.05)

        GameTile = Label(Game, textvariable=titleVert, font='Arial 30 bold' , fg='white')
        GameTile.place(relx=.425, rely=.25)

        GameTile2 = Label(Game, textvariable=titleVert, font='Arial 30 bold' , fg='white')
        GameTile2.place(relx=.520, rely=.25)

        GameTile3 = Label(Game, textvariable=titleVert, font='Arial 30 bold' , fg='white')
        GameTile3.place(relx=.425, rely=.38)

        GameTile4 = Label(Game, textvariable=titleVert, font='Arial 30 bold' , fg='white')
        GameTile4.place(relx=.520, rely=.38)

        GameTile5 = Label(Game, textvariable=titleVert, font='Arial 30 bold', fg='white')
        GameTile5.place(relx=.425, rely=.51)

        GameTile6 = Label(Game, textvariable=titleVert, font='Arial 30 bold', fg='white')
        GameTile6.place(relx=.520, rely=.51)

        GameTile7 = Label(Game, textvariable=titleVert, font='Arial 30 bold', fg='white')
        GameTile7.place(relx=.425, rely=.64)

        GameTile8 = Label(Game, textvariable=titleVert, font='Arial 30 bold', fg='white')
        GameTile8.place(relx=.520, rely=.64)

        #

        GameTile9 = Label(Game, textvariable=titleHorz, font='Arial 7 bold', fg='white')
        GameTile9.place(relx=.35, rely=.4)

        GameTile10 = Label(Game, textvariable=titleHorz, font='Arial 7 bold', fg='white')
        GameTile10.place(relx=.35, rely=.6)

        #

        GameInteract = Button(Game, font='Arial 4 bold', fg='white', width=10, height=5, command=lambda: sendMove('A1'))

        GameInteract2 = Button(Game, font='Arial 4 bold', fg='white', width=10, height=5, command=lambda: sendMove('A2'))

        GameInteract3 = Button(Game, font='Arial 4 bold', fg='white', width=10, height=5, command=lambda: sendMove('A3'))

        GameInteract4 = Button(Game, font='Arial 4 bold', fg='white', width=10, height=5, command=lambda: sendMove('B1'))

        GameInteract5 = Button(Game, font='Arial 4 bold', fg='white', width=10, height=5, command=lambda: sendMove('B2'))

        GameInteract6 = Button(Game, font='Arial 4 bold', fg='white', width=10, height=5, command=lambda: sendMove('B3'))

        GameInteract7 = Button(Game, font='Arial 4 bold', fg='white', width=10, height=5, command=lambda: sendMove('C1'))

        GameInteract8 = Button(Game, font='Arial 4 bold', fg='white', width=10, height=5, command=lambda: sendMove('C2'))

        GameInteract9 = Button(Game, font='Arial 4 bold', fg='white', width=10, height=5, command=lambda: sendMove('C3'))

        #

        GameButtons = [GameInteract, GameInteract2, GameInteract3, GameInteract4, GameInteract5, GameInteract6, GameInteract7, GameInteract8, GameInteract9]

        GameItem = Label(Game, textvariable=A1_VAL, font='Arial 30 bold', fg='white', bg=windowBackground)

        GameItem2 = Label(Game, textvariable=A2_VAL, font='Arial 30 bold', fg='white', bg=windowBackground)

        GameItem3 = Label(Game, textvariable=A3_VAL, font='Arial 30 bold', fg='white', bg=windowBackground)

        GameItem4 = Label(Game, textvariable=B1_VAL, font='Arial 30 bold', fg='white', bg=windowBackground)

        GameItem5 = Label(Game, textvariable=B2_VAL, font='Arial 30 bold', fg='white', bg=windowBackground)

        GameItem6 = Label(Game, textvariable=B3_VAL, font='Arial 30 bold', fg='white', bg=windowBackground)

        GameItem7 = Label(Game, textvariable=C1_VAL, font='Arial 30 bold', fg='white', bg=windowBackground)

        GameItem8 = Label(Game, textvariable=C2_VAL, font='Arial 30 bold', fg='white', bg=windowBackground)

        GameItem9 = Label(Game, textvariable=C3_VAL, font='Arial 30 bold', fg='white', bg=windowBackground)

        BackButton = Button(Game, text='⇽ EXIT GAME', font='Arial 12 bold', bg=windowBackground, borderwidth=0, fg='#e74c3c', command=lambda: Window.exitgame())
        BackButton.place(relx=.03, rely=.885)

        GameInteract.place(relx=.36, rely=.28)
        GameInteract2.place(relx=.36, rely=.48)
        GameInteract3.place(relx=.36, rely=.68)
        GameInteract4.place(relx=.459, rely=.28)
        GameInteract5.place(relx=.459, rely=.48)
        GameInteract6.place(relx=.459, rely=.68)
        GameInteract7.place(relx=.56, rely=.28)
        GameInteract8.place(relx=.56, rely=.48)
        GameInteract9.place(relx=.56, rely=.68)

        def refreshBoard():
            global isTurn
            if 'A1' in boardSlots:
                GameInteract.place(relx=.36, rely=.28)
            else:
                GameItem.place(relx=.362, rely=.26)
                GameInteract.place_forget()
            if 'A2' in boardSlots:
                GameInteract2.place(relx=.36, rely=.48)
            else:
                GameItem2.place(relx=.362, rely=.46)
                GameInteract2.place_forget()
            if 'A3' in boardSlots:
                GameInteract3.place(relx=.36, rely=.68)
            else:
                GameItem3.place(relx=.362, rely=.66)
                GameInteract3.place_forget()
            if 'B1' in boardSlots:
                GameInteract4.place(relx=.459, rely=.28)
            else:
                GameItem4.place(relx=.462, rely=.26)
                GameInteract4.place_forget()
            if 'B2' in boardSlots:
                GameInteract5.place(relx=.459, rely=.48)
            else:
                GameItem5.place(relx=.462, rely=.46)
                GameInteract5.place_forget()
            if 'B3' in boardSlots:
                GameInteract6.place(relx=.459, rely=.68)
            else:
                GameItem6.place(relx=.462, rely=.66)
                GameInteract6.place_forget()
            if 'C1' in boardSlots:
                GameInteract7.place(relx=.56, rely=.28)
            else:
                GameItem7.place(relx=.562, rely=.26)
                GameInteract7.place_forget()
            if 'C2' in boardSlots:
                GameInteract8.place(relx=.56, rely=.48)
            else:
                GameItem8.place(relx=.562, rely=.46)
                GameInteract8.place_forget()
            if 'C3' in boardSlots:
                GameInteract9.place(relx=.56, rely=.68)
            else:
                GameItem9.place(relx=.562, rely=.66)
                GameInteract9.place_forget()
            if isTurn is False:
                print('is not turn')
                for GameButton in GameButtons:
                    GameButton.configure(state='disabled')
            else:
                print('is turn')
                for GameButton in GameButtons:
                    GameButton.configure(state='normal')

            Window.checkwinner()

        refreshBoard()

        GameWinner = Label(Game, textvariable=endWin, font='Arial 20 bold', fg='#2ecc71', bg=windowBackground)
        GameLoser = Label(Game, textvariable=endLose, font='Arial 20 bold', fg='#e74c3c', bg=windowBackground)

        # GameWinner.place(relx=.41, rely=.8)
        # GameLoser.place(relx=.42, rely=.8)

        Game.mainloop()

    @staticmethod
    def drawpanel(itemCord, team):
        global myTeam, theirTeam, boardSlots, boardValues
        global A1_VAL, A2_VAL, A3_VAL, B1_VAL, B2_VAL, B3_VAL, C1_VAL, C2_VAL, C3_VAL

        boardSlotsStatic2 = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']

        if team == 1:
            belongs = myTeam
        else:
            belongs = theirTeam

        boardSection2 = boardSlotsStatic2.index(itemCord)
        boardValues[boardSection2].set(belongs)
        boardSlots.remove(itemCord)

        Window.refresh()

    @staticmethod
    def refresh():
        global isTurn
        global GameInteract, GameInteract2, GameInteract3, GameInteract4, GameInteract5, GameInteract6, GameInteract7, GameInteract8, GameInteract9, GameButtons
        global boardSlots
        global GameItem, GameItem2, GameItem3, GameItem4, GameItem5, GameItem6, GameItem7, GameItem8, GameItem9

        if 'A1' in boardSlots:
            GameInteract.place(relx=.36, rely=.28)
        else:
            GameItem.place(relx=.362, rely=.26)
            GameInteract.place_forget()
        if 'A2' in boardSlots:
            GameInteract2.place(relx=.36, rely=.48)
        else:
            GameItem2.place(relx=.362, rely=.46)
            GameInteract2.place_forget()
        if 'A3' in boardSlots:
            GameInteract3.place(relx=.36, rely=.68)
        else:
            GameItem3.place(relx=.362, rely=.66)
            GameInteract3.place_forget()
        if 'B1' in boardSlots:
            GameInteract4.place(relx=.459, rely=.28)
        else:
            GameItem4.place(relx=.462, rely=.26)
            GameInteract4.place_forget()
        if 'B2' in boardSlots:
            GameInteract5.place(relx=.459, rely=.48)
        else:
            GameItem5.place(relx=.462, rely=.46)
            GameInteract5.place_forget()
        if 'B3' in boardSlots:
            GameInteract6.place(relx=.459, rely=.68)
        else:
            GameItem6.place(relx=.462, rely=.66)
            GameInteract6.place_forget()
        if 'C1' in boardSlots:
            GameInteract7.place(relx=.56, rely=.28)
        else:
            GameItem7.place(relx=.562, rely=.26)
            GameInteract7.place_forget()
        if 'C2' in boardSlots:
            GameInteract8.place(relx=.56, rely=.48)
        else:
            GameItem8.place(relx=.562, rely=.46)
            GameInteract8.place_forget()
        if 'C3' in boardSlots:
            GameInteract9.place(relx=.56, rely=.68)
        else:
            GameItem9.place(relx=.562, rely=.66)
            GameInteract9.place_forget()
        if isTurn is False:
            for GameButton in GameButtons:
                GameButton.configure(state='disabled')
        else:
            for GameButton in GameButtons:
                GameButton.configure(state='normal')

        Window.checkwinner()

    @staticmethod
    def checkwinner():
        global A1_VAL, A2_VAL, A3_VAL, B1_VAL, B2_VAL, B3_VAL, C1_VAL, C2_VAL, C3_VAL, myTeam, GameToken, isTurn

        def handleWinner(winBox):
            if winBox != '-':
                if winBox == myTeam:
                    GameStateInGame.place_forget()
                    GameStateGameOver.place(relx=.83, rely=.05)
                    winNotification = '+-+-+!' + 'W' + GameToken
                    Client.send(winNotification, True)
                    Window.displaywinner(True)
                    isTurn = False
                else:
                    GameStateInGame.place_forget()
                    GameStateGameOver.place(relx=.83, rely=.05)
                    winNotification = '+-+-+!' + 'L' + GameToken
                    Client.send(winNotification, True)
                    Window.displaywinner(False)
                    isTurn = False

        if A1_VAL.get() == A2_VAL.get() and A2_VAL.get() == A3_VAL.get():
            handleWinner(A1_VAL.get())

        if B1_VAL.get() == B2_VAL.get() and B2_VAL.get() == B3_VAL.get():
            handleWinner(B1_VAL.get())

        if C1_VAL.get() == C2_VAL.get() and C2_VAL.get() == C3_VAL.get():
            handleWinner(C1_VAL.get())

        if A1_VAL.get() == B1_VAL.get() and B1_VAL.get() == C1_VAL.get():
            handleWinner(A1_VAL.get())

        if A2_VAL.get() == B2_VAL.get() and B2_VAL.get() == C2_VAL.get():
            handleWinner(A2_VAL.get())

        if A3_VAL.get() == B3_VAL.get() and B3_VAL.get() == C3_VAL.get():
            handleWinner(A3_VAL.get())

        if A1_VAL.get() == B2_VAL.get() and B2_VAL.get() == C3_VAL.get():
            handleWinner(A1_VAL.get())

        if C1_VAL.get() == B2_VAL.get() and B2_VAL.get() == A3_VAL.get():
            handleWinner(C1_VAL.get())

    @staticmethod
    def exitgame():
        Game.destroy()
        Window.draw()

        Client.connect()

    @staticmethod
    def displaywinner(wonGame):
        if wonGame is True:
            GameWinner.place(relx=.41, rely=.8)
        else:
            GameLoser.place(relx=.42, rely=.8)
        pass

    @staticmethod
    def notif(title="Title Placeholder", subtext='Default text', colour='#e74c3c'):

        Notification2 = Tk()
        Notification2.configure(bg='#141414')
        Notification2.geometry('540x220+810+540')
        Notification2.title('Notification')

        Notification2.overrideredirect(1)

        titleText = StringVar()
        subText = StringVar()

        titleText.set(title)
        subText.set(subtext)

        barTop = Label(Notification2, text='                                            ', font='Arial 35 bold', fg=colour, bg=colour)
        barTop.place(relx=0, rely=0)

        title = Label(Notification2, textvariable=titleText, font=('Hurme Geometric Sans 4', 20, 'bold'),
                       fg='#141414', bg=colour)
        title.place(relx=.05, rely=.05)

        """text = Label(Notification2, textvariable=subText, font=('courier new', 10, 'bold'),
                      fg='white', bg='#141414')
        text.place(relx=.05, rely=.33)"""

        ChatLog = Text(Notification2, bg="#141414", height="4", width="54", font="Arial", borderwidth=0)
        ChatLog.place(relx=.05, rely=.33)

        ChatLog.config(state=NORMAL)

        ChatLog.insert(END, subtext)
        ChatLog.tag_add(subtext, 1.0, 99999999999999.0)
        ChatLog.tag_config(subtext, foreground='white', font=('Segoe UI Light', 10, "bold"))

        ChatLog.config(state=DISABLED)

        confirmButton = Button(Notification2, text='CONFIRM', font=('Hurme Geometric Sans 4', 20, 'bold'), fg=colour, bg='#141414', borderwidth=0, command=lambda: Notification2.destroy())
        confirmButton.place(relx=.695, rely=.71)


    @staticmethod
    def settings():
        global Settings

        def saveSettings():
            newColour = colour_drop.get().lower()
            if newColour == 'white':
                config['window']['theme'] = '#FFFFFF'
            elif newColour == 'red':
                config['window']['theme'] = '#FF0000'
            elif newColour == 'blue':
                config['window']['theme'] = '#00BFFF'
            elif newColour == 'green':
                config['window']['theme'] = '#7CFC00'
            elif newColour == 'yellow':
                config['window']['theme'] = '#FFFF00'
            elif newColour == 'purple':
                config['window']['theme'] = '#8A2BE2'
            elif newColour == 'orange':
                config['window']['theme'] = '#FF8C00'
            elif newColour == 'gray':
                config['window']['theme'] = '#CCCCCC'

            config['window']['font'] = font_drop.get()

            with open('config.json', 'w') as config_file:
                config_file.write(json.dumps(config, indent=8))

            sec3 = Label(Settings, text='Restarting in three seconds...', fg=colourTheme, bg=windowBackground, font=('courier new', '12'))
            sec2 = Label(Settings, text='Restarting in two seconds...', fg=colourTheme, bg=windowBackground, font=('courier new', '12'))
            sec1 = Label(Settings, text='Restarting in one second...', fg=colourTheme, bg=windowBackground, font=('courier new', '12'))

            Settings.after(0000, lambda: sec3.place(relx=0.6740, rely=0.83))
            Settings.after(1000, lambda: sec3.place_forget())
            Settings.after(1000, lambda: sec2.place(relx=0.6740, rely=0.83))
            Settings.after(2000, lambda: sec2.place_forget())
            Settings.after(2000, lambda: sec1.place(relx=0.6740, rely=0.83))



        MainWindow.destroy()

        Settings = Tk()
        Settings.configure(bg='#141414')
        Settings.geometry(windowResolution)
        Settings.title('Settings')

        # Settings.attributes('-topmost', True)

        title_type = StringVar()
        info_message = StringVar()
        lines = StringVar()
        subtitleset = StringVar()
        font_message = StringVar()
        user_message = StringVar()
        ip_text = StringVar()
        configuration_text = StringVar()
        connection_text = StringVar()

        info_message.set('CHANGE HOW THE GUI LOOKS [FONT / COLOUR / THEME]')
        subtitleset.set('W I N D O W  S E T T I N G S')
        font_message.set('F O N T')
        user_message.set('D E F A U L T  U S E R N A M E')
        ip_text.set('D E F A U L T  I P  A D D R E S S')
        configuration_text.set('C O N F I G U R A T I O N')
        connection_text.set('C O N N E C T I O N  S E T T I N G S')
        lines.set('_' * 75)

        title_colour = '#00FF00'
        title_type.set('S E T T I N G S')

        title_line = Label(Settings, textvariable=lines, font='Arial 15 bold', fg=colourTheme, bg='#141414')
        title_line.place(relx=.04, rely=.14)

        deep_line = Label(Settings, textvariable=lines, font='Arial 15 bold', fg=colourTheme, bg='#141414')
        deep_line.place(relx=.04, rely=.8)

        main_label = Label(Settings, textvariable=title_type, font='Arial 16 bold', fg='#141414', bg=colourTheme)
        main_label.place(relx=.046, rely=.09)

        subtitle = Label(Settings, textvariable=subtitleset, font='Arial 11 bold', fg=colourTheme, bg='#141414',
                      justify=LEFT)
        subtitle.place(relx=.046, rely=.26)

        font_label = Label(Settings, textvariable=font_message, font='Arial 9 bold', fg=colourTheme, bg='#141414',
                         justify=LEFT)
        font_label.place(relx=.046, rely=.34)

        current_default_username = 'NONE'
        current_default_ip = 'chatserver.hopto.org'

        user_label = Label(Settings, textvariable=user_message, font='Arial 9 bold', fg=colourTheme, bg='#141414',
                           justify=LEFT)
        user_label.place(relx=.046, rely=.48)

        ip_label = Label(Settings, textvariable=ip_text, font='Arial 9 bold', fg=colourTheme, bg='#141414',
                           justify=LEFT)
        ip_label.place(relx=.046, rely=.62)

        fonts = [
            'ARIAL',
            'SANS-SERIF',
            'COURIER NEW'
        ]

        current_default_username = 'NONE'

        current_font = 'ARIAL'

        font_drop = tkinter.ttk.Combobox(Settings, width=29, values=fonts, state='readonly')
        font_drop.set(current_font)
        font_drop.place(relx=.049, rely=.4)

        user_entry = Entry(Settings, width=32)
        user_entry.place(relx=.049, rely=.54)

        user_entry.setvar(current_default_username)

        ip_entry = Entry(Settings, width=32)
        ip_entry.place(relx=.049, rely=.68)

        ip_entry.setvar(current_default_username)

        ##################################################

        subtitle2 = Label(Settings, textvariable=configuration_text, font='Arial 11 bold', fg=colourTheme, bg='#141414',
                         justify=LEFT)
        subtitle2.place(relx=.37, rely=.26)

        colour_label = Label(Settings, text='C O L O U R', font='Arial 9 bold', fg=colourTheme, bg='#141414',
                           justify=LEFT)
        colour_label.place(relx=.37, rely=.34)

        colours = [
            'BLUE', 'GREEN', 'PURPLE', 'YELLOW', 'RED', 'ORANGE', 'WHITE', 'GRAY'
        ]

        current_colour = 'BLUE'

        current_font = 'ARIAL'

        colour_drop = tkinter.ttk.Combobox(Settings, width=26, values=colours, state='readonly')
        colour_drop.set(current_colour)
        colour_drop.place(relx=.372, rely=.4)

        ###############################################################

        subtitle3 = Label(Settings, textvariable=connection_text, font='Arial 11 bold', fg=colourTheme, bg='#141414',
                          justify=LEFT)
        subtitle3.place(relx=.675, rely=.26)

        time_label = Label(Settings, text='C O N N E C T I O N  T I M E O U T', font='Arial 9 bold', fg=colourTheme, bg='#141414',
                          justify=LEFT)
        time_label.place(relx=.675, rely=.34)

        time_entry = Entry(Settings, width=41)
        time_entry.place(relx=.679, rely=.4)

        port_label = Label(Settings, text='P O R T', font='Arial 9 bold', fg=colourTheme,
                           bg='#141414',
                           justify=LEFT)
        port_label.place(relx=.675, rely=.62)

        port_entry = Entry(Settings, width=23)
        port_entry.place(relx=.679, rely=.68)

        save_label = Label(Settings, text='S A V E', font='Arial 9 bold', fg=colourTheme,
                           bg='#141414',
                           justify=LEFT)
        save_label.place(relx=.86, rely=.62)

        save_button = Button(Settings, text='✓', width=11, height=1, command=lambda:saveSettings())
        save_button.place(relx=.86, rely=.68)

    def close(self):
        pass

    @staticmethod
    def alert(mode, message, frame=None):
        global Notification

        def execute():
            if frame is None:
                Notification.destroy()
            elif frame is 'UPDATE':
                Notification.destroy()
                Manager.search('FORCED')
            elif frame is 'UPDATE2':
                Notification.destroy()

        Notification = Tk()
        Notification.configure(bg='#141414')
        Notification.geometry('520x180+30+30')
        Notification.title('Notification')

        Notification.overrideredirect(1)
        Notification.attributes('-topmost', True)

        title_type = StringVar()
        error_message = StringVar()
        title_colour = StringVar()
        lines = StringVar()

        error_message.set(message)
        lines.set('_' * 43)

        if mode == 'ERROR':
            title_colour = '#F2473F'
            title_type.set('E R R O R')
        elif mode == 'WARNING':
            title_colour = '#FF8C00'
            title_type.set('W A R N I N G')
        elif mode == 'NORMAL':
            title_colour = '#CCCCCC'
            title_type.set('N O T I F I C A T I O N')

        title_line = Label(Notification, textvariable=lines, font='Arial 15 bold', fg=title_colour, bg='#141414')
        title_line.place(relx=.04, rely=.14)

        deep_line = Label(Notification, textvariable=lines, font='Arial 19 bold', fg=title_colour, bg='#141414')
        deep_line.place(relx=.0, rely=.8)

        main_label = Label(Notification, textvariable=title_type, font='Arial 16 bold', fg='#141414', bg=title_colour)
        main_label.place(relx=.046, rely=.09)

        error_label = Label(Notification, textvariable=error_message, font='system 11 bold', fg='#FFFFFF', bg='#141414',
                            justify=LEFT)
        error_label.place(relx=.045, rely=.4)

        button = tkinter.ttk.Button(Notification, text='OK', command=lambda: (execute()))
        button.place(relx=.81, rely=.79)

        if frame is 'UPDATE2':
            button.place_forget()
            execute()

        Notification.mainloop()

    @staticmethod
    def show(message):
        if 1:
            ChatLog.config(state=NORMAL)
            message = message.strip('%!')
            ChatLog.insert(END, '\n' + message)
            ChatLog.tag_add(message, float(ChatLog.index(END)) - 1.0, (float(ChatLog.index(END)) - 1.0) + len(message))
            ChatLog.tag_config(message, foreground=colourTheme, font=(windowFont, 11, "bold"))
            ChatLog.config(state=DISABLED)
            ChatLog.see(END)
        if 0:
            print('TT: ', message)


class Manager:
    @staticmethod
    def warn():
        Window.alert('WARNING', 'UPDATING IS CURRENTLY UNSTABLE DOING SO MAY PREVENT\n'
                                'THE PROGRAM FROM RUNNING OR CRASHING DURING RUNTIME', 'UPDATE')

    @staticmethod
    def search(frame='AUTO'):
        global Notification

        info_file = open('version.txt', 'r+')
        current_version = info_file.readlines()[0]
        info_file.close()
        try:
            if config['settings']['auth'] == 'true':
                # print('INFO: Permissions support ON')
                if ADMIN_LEVEL > 1:
                    USER_PERMISSIONS.extend((ADMIN_COMMAND_KICK, ADMIN_COMMAND_CLEARALL, ADMIN_COMMAND_MESSAGE))
                if ADMIN_LEVEL > 2:
                    USER_PERMISSIONS.extend((ADMIN_COMMAND_RESTART, ADMIN_COMMAND_SHUTDOWN, ADMIN_COMMAND_FORCEQUIT, ADMIN_COMMAND_GHOST))
        except:
            pass

        latest_version = External.Download()
        # Update is available
        if float(latest_version) > float(current_version):
            if frame is 'FORCED':
                Window.alert('NORMAL', 'AN UPDATE WAS FOUND - THE LATEST VERSION IS V ' + latest_version, 'UPDATE2')
                External.Switch()
            else:
                Window.show('An update was found, type .update to update the client.')

        # Update is not available
        else:
            if frame is 'FORCED':
                Window.alert('NORMAL', 'NO UPDATES WERE FOUND - CURRENT VERSION V ' + current_version)


Client.configure()

ADMIN_LEVEL = 0
HELP_MESSAGE = '''.help - prints the help menu
.quit - exit the server gracefully
.name - change current username
.clear - clear chat
.online - view online users
.colour - change theme colour
.update - update the client
.about - view information about client
'''

ADMIN_MESSAGE = '''.kick - kick a client off
.ca - clears messages for everyone
.fq - force quits all clients
.message - private message a user (unavailable)
.restart - restarts the server
.shutdown - shuts down the server
'''

CLEAR_MESSAGE_ADMIN = 'Chat was cleared by an administrator'
CLEAR_COMMAND = 'Chat was cleared successfully.'
NAME_COMMAND = 'The correct usage for this command is .name <username>'
GHOST_COMMAND = 'The correct usage for this command is .ghost <user>'
SPAM_MESSAGE = 'Your message was not sent due to potential spam.'
MESSAGE_COMMAND = 'This function is unavailable right now.'
KICK_COMMAND = 'The correct usage for this command is .kick <user>'
UPDATE_COMMAND = 'No updates are available right now.'
VERSION_MESSAGE = 'GUI CHAT / Auth support [VERSION: ' + str(programVersion) + ']'

# Admin permissions - to be handled in configuration file.
ADMIN_COMMAND_SYNTAX = 'admin.commands.show'
ADMIN_COMMAND_KICK = 'admin.commands.kick'
ADMIN_COMMAND_MESSAGE = 'admin.commands.message'
ADMIN_COMMAND_CLEARALL = 'admin.commands.clearall'
ADMIN_COMMAND_FORCEQUIT = 'admin.commands.forcequit'
ADMIN_COMMAND_NICKNAME = 'admin.commands.nickname'
ADMIN_COMMAND_RESTART = 'admin.commands.restart'
ADMIN_COMMAND_SHUTDOWN = 'admin.commands.shutdown'
ADMIN_COMMAND_GHOST = '.admin.commands.ghost'
ADMIN_MESSAGE_JOIN = 'admin.messages.join'
ADMIN_MESSAGE_LEAVE = 'admin.messages.leave'

INSUFFICIENT_PERMISSIONS = 'You do not have the permission to execute this command'
USER_PERMISSIONS = []
PORT = 6666

Window.notif('GAME START', 'There was an error when trying to start a game. No end user responded to the game start request, you will have to launch the game and start a new match using the online users list.')

Manager = Manager()
External = Updater.Update()


def has(permission):
    if permission in USER_PERMISSIONS:
        return True
    else:
        return False


IP = '127.0.0.1'

if __name__ == '__main__':
    Client.configure()
    Window.draw()

    IP = '127.0.0.1'
    Client.connect()
