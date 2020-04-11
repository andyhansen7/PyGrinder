#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
            PyGrinder by Andy Hansen
                Version 1.0.0

A simulated mouse clicker with a clean interface and added features to help avoid server AFK plugins

"""

# packages
import pynput.mouse as pymouse
import pynput.keyboard as pykeyboard
import wx

# libraries
import os
import time
import math
import random
import datetime
import threading

class WindowController():
    def __init__(self, title, defWidth, defHeight):
        self.width = defWidth
        self.height = defHeight
        self.title = title
        
        self.app = wx.App() 
        
        self.window = MainWindow(self, self.title, self.width, self.height)
        
        self.app.MainLoop()
        
    def Resize(self, w, h):
        self.width = w 
        self.height = h 
        
        self.window.Destroy()
        self.window = MainWindow(self, self.title, self.width, self.height)
        

class MainWindow(wx.Frame):
    def __init__(self, parent, title, width, height):
        super().__init__(parent=None, title=title, size=(width,height))
        
        self.parent = parent
        
        self.width = width
        self.height = height

        self.panel = MainPanel(self, width, height)

        self.CreateStatusBar()

        # file menu items
        self.filemenu = wx.Menu()
        self.menuSaveConfig = self.filemenu.Append(wx.ID_SAVE, "&Save configuration", "Save the current settings as a loadable configuration")
        self.menuLoadConfig = self.filemenu.Append(wx.ID_OPEN, "Load configuration", "Load settings from a configuration file")
        self.menuAbout = self.filemenu.Append(wx.ID_ABOUT, "&About","Information about this program")
        self.menuReport = self.filemenu.Append(wx.ID_SETUP, "&Report Bug", "Report a bug or problem")
        self.menuExit = self.filemenu.Append(wx.ID_EXIT,"&Exit","Terminate the program")

        # file menu bar
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.filemenu, "&File")
        self.SetMenuBar(self.menuBar)

        # menu events
        self.Bind(wx.EVT_MENU, self.OnSave, self.menuSaveConfig)
        self.Bind(wx.EVT_MENU, self.OnLoad, self.menuLoadConfig)
        self.Bind(wx.EVT_MENU, self.OnAbout, self.menuAbout)
        self.Bind(wx.EVT_MENU, self.OnReport, self.menuReport)
        self.Bind(wx.EVT_MENU, self.OnExit, self.menuExit)
        
        self.Bind(wx.EVT_SIZE, self.OnResize);

        self.Center()
        self.Show(True)

    def loadConfig(self, file):
        self.panel.setData(file.read())
        file.close()

    def saveConfig(self, file):
        file.write(self.panel.getData())
        file.close()

    def OnSave(self, e):
        with wx.FileDialog(self, "Save config file", wildcard="PyGrinder files (*.pygrinder)|*.pygrinder", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as file:
                    self.saveConfig(file)
            except IOError:
                dlg = wx.MessageDialog( self, "The file could not be saved.", "IOError", wx.OK)
                dlg.ShowModal()
                dlg.Destroy()      

    def OnLoad(self, e):
        with wx.FileDialog(self, "Open config file", wildcard="PyGrinder files (*.pygrinder)|*.pygrinder",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return   

            pathname = fileDialog.GetPath()
        try:
            with open(pathname, 'r') as file:
                self.loadConfig(file)
        except IOError:
            dlg = wx.MessageDialog( self, "The file could not be opened.", "IOError", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()

    def OnAbout(self, e):
        dlg = wx.MessageDialog( self, "A simple autoclicker for avoiding server AFK filters", "About PyClick", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnReport(self, e):
        self.reportWindow = ReportWindow(parent=self, mainPanel=self.panel)

    def OnExit(self, e):
        self.Close(True)
        
    def OnResize(self, e):
        w,h = e.GetSize()
        if w != self.width and h != self.height:
            self.parent.Resize(w, h)

class ReportWindow(wx.Frame):
    def __init__(self, parent, mainPanel):
        super(ReportWindow, self).__init__(parent=parent, title="Report Issue", size=(600,400), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        
        self.panel = wx.Panel()
        self.panel.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.Center()
        self.Show(True)

class MainPanel(wx.Panel):
    def __init__(self, parent, width, height):
        super().__init__(parent)

        # members
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        #self.grid = wx.GridBagSizer(hgap=5, vgap=5)

        self.mouse = pymouse.Controller()
        self.keyboard = pykeyboard.Controller()

        self.logger = open("PyGrinder.log", "w")

        # vars
        self.width = width
        self.height = height
        
        self.running = False
        self.cancelled = False
        
        self.executeHop = False
        self.executeStrafe = False
        self.executeCommand = False

        self.command_list_text = ''

        self.countdown_delay = 15.0
        self.hop_delay = 60.0
        self.strafe_delay = 60.0
        self.command_delay = 120.0
        
        self.clickloop_delay = 0.01
        self.start_pause = 0.25
        
        self.hop_time_1 = 0.25
        self.hop_time_2 = 0.1
        self.hop_time_3 = 0.25
        
        self.strafe_time_1 = 0.05
        self.strafe_time_2 = 0.05
        self.strafe_time_3 = 0.08
        self.strafe_time_4 = 0.10
        
        self.keypress_time_1 = 0.05
        self.keypress_time_2 = 0.05
        self.enter_time_1 = 0.05
        self.enter_time_2 = 0.45

        self.SetBackgroundColour("steel blue")

        # center title
        titleFont = wx.Font(wx.FontInfo(int(.025 * self.height)).Bold())

        self.progTitle = wx.StaticText(self, label="PyGrinder 1.0.0", style=wx.ALIGN_CENTER_HORIZONTAL)
        #self.progTitle.Center()
        self.progTitle.SetFont(titleFont)
        self.progTitle.SetPosition((int(.375 * self.width), int(.416 * self.height)))
        self.mainSizer.Add(self.progTitle, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

        # timer
        timerFont = wx.Font(wx.FontInfo(36).Bold())

        self.timer = wx.TextCtrl(self, name="Timer", style=wx.TE_READONLY)
        self.timer.SetFont(timerFont)
        self.timer.SetSize(int(.675 * self.width), int(.666 * self.height), int(.2875 * self.width), int(.1 * self.height))
        self.timer.SetForegroundColour('black')
        self.timer.SetValue('00:00.00')
        self.mainSizer.Add(self.timer, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

        # timer label
        timerLabelFont = wx.Font(wx.FontInfo(16).Bold())

        self.timerLabel = wx.StaticText(self, name="Timer Label")
        self.timerLabel.SetFont(timerLabelFont)
        self.timerLabel.SetSize(int(.675 * self.width), int(.616 * self.height), int(0.25 * self.width), int(0.1 * self.height))
        self.timerLabel.SetLabel('')
        self.mainSizer.Add(self.timerLabel, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

        # start control
        self.startButton = wx.Button(self, label="START")
        self.startButton.SetSize(int(.0125 * self.width), int(.033 * self.height), int(.4625 * self.width), int(0.333 * self.height), wx.SIZE_FORCE)
        self.startButton.SetBackgroundColour('pale green')
        self.startButton.SetForegroundColour('white')
        self.startButton.SetFont(timerFont)
        self.mainSizer.Add(self.startButton, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

        # stop control
        self.stopButton = wx.Button(self, label="STOP")
        self.stopButton.SetSize(int(.5 * self.width), int(.033 * self.height), int(.4625 * self.width), int(0.333 * self.height), wx.SIZE_FORCE)
        self.stopButton.SetBackgroundColour('red')
        self.stopButton.SetForegroundColour('white')
        self.stopButton.SetFont(timerFont)
        self.mainSizer.Add(self.stopButton, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

        # hopper
        self.hopCheckBox = wx.CheckBox(self, label="Add periodic hop")
        self.hopCheckBox.SetPosition((int(.025 * self.width), int(0.5 * self.height)))
        self.mainSizer.Add(self.hopCheckBox, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

        # strafer
        self.strafeCheckBox = wx.CheckBox(self, label="Add periodic strafe")
        self.strafeCheckBox.SetPosition((int(.025 * self.width), int(0.55 * self.height)))
        self.mainSizer.Add(self.strafeCheckBox, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

        # command sender
        self.commandCheckBox = wx.CheckBox(self, label="Add periodic commands")
        self.commandCheckBox.SetPosition((int(.025 * self.width), int(0.6 * self.height)))
        self.mainSizer.Add(self.commandCheckBox, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

        # events 
        self.Bind(wx.EVT_BUTTON, self.OnStartClick, self.startButton)
        self.Bind(wx.EVT_BUTTON, self.OnStopClick, self.stopButton)

        self.Bind(wx.EVT_CHECKBOX, self.OnHopCheck, self.hopCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnStrafeCheck, self.strafeCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCommandCheck, self.commandCheckBox)

        self.logger.write(str(datetime.datetime.now()) + '[INIT] Panel created\n')

    def setData(self, contents):
        elements = contents.split(' ', 5)
        commands = elements[5].split('\n', 1)

        self.hopCheckBox.SetValue(bool(elements[0]))
        if self.hopCheckBox.GetValue(): 
            self.hopCheckBox.SetValue(True)
            self.OnHopCheck(None)
            self.hopTextBox.SetValue(elements[1])

        self.strafeCheckBox.SetValue(bool(elements[2]))
        if self.strafeCheckBox.GetValue():
            self.strafeCheckBox.SetValue(True)
            self.OnStrafeCheck(None)
            self.strafeTextBox.SetValue(elements[3])

        self.commandCheckBox.SetValue(bool(elements[4]))
        if self.commandCheckBox.GetValue():
            self.commandCheckBox.SetValue(True)
            self.OnCommandCheck(None)
            self.commandTextBox.SetValue(commands[0])
            self.commandList.SetValue(commands[1])
    
    def getData(self):
        return ( str(self.hopCheckBox.GetValue()) + ' ' + str(self.hop_delay) + ' ' + str(self.strafeCheckBox.GetValue()) + ' ' + str(self.strafe_delay) + ' ' + str(self.commandCheckBox.GetValue()) + ' ' + str(self.command_delay) + '\n' + self.command_list_text)

    def timerSleep(self, delay):
        for i in range(0, int(100 * delay)):
            time.sleep(0.01)
            self.loop += 1
            
            if self.loop % (self.hop_delay * 100) == 0:
                self.executeHop = True
            if self.loop % (self.strafe_delay * 100) == 0:
                self.executeStrafe = True
            if self.loop % (self.command_delay * 100) == 0:
                self.executeCommand = True
            
            self.timer.SetValue((str((math.trunc(self.loop / 6000) % 60)) if (math.trunc(self.loop / 6000) % 60) > 10 else ('0' + str(math.trunc(self.loop / 6000) % 60))) + ':' + (str((self.loop % 6000) / 100) if (self.loop % 6000) / 100 > 10 else '0' + str((self.loop % 6000) / 100)))
            
    def clickLoop(self):
        self.logger.write(str(datetime.datetime.now()) + '[INFO] Click loop began execution\n')

        # log vars from inputs
        if self.hopCheckBox.GetValue(): 
            self.logger.write(str(datetime.datetime.now()) + '[INFO] Hop delay set to ' + str(self.hop_delay) + '\n')

        if self.strafeCheckBox.GetValue(): 
            self.logger.write(str(datetime.datetime.now()) + '[INFO] Strafe delay set to ' + str(self.strafe_delay) + '\n')

        if self.commandCheckBox.GetValue(): 
            self.logger.write(str(datetime.datetime.now()) + '[INFO] Command delay set to ' + str(self.command_delay) + '\n')
            self.logger.write(str(datetime.datetime.now()) + '[INFO] Commands being run:\n')
            for c in self.command_list_text.split('\n'):
                self.logger.write(c + '\n')

        # countdown to execution
        self.timer.SetForegroundColour('red')
        self.timerLabel.SetLabel('Countdown:')

        for i in range(0, int(100 * self.countdown_delay)):
            if self.cancelled: break
            self.timer.SetLabel('00:' + (str(round(self.countdown_delay - ((i + 1) / 100), 2) if self.countdown_delay - (i + 1) / 100 > 10 else '0' + str(round(self.countdown_delay - ((i + 1) / 100), 2)))))
            time.sleep(0.01)
        
        self.logger.write(str(datetime.datetime.now()) + '[INFO] Click loop finished countdown, beginning execution\n')

        if not self.cancelled:

            self.timerLabel.SetLabel('Elapsed Time:')
            self.timer.SetForegroundColour('lime green')

            self.mouse.press(pymouse.Button.left)

            self.loop = 0

            # main loop
            while True:
                # check whether operation has been cancelled
                if self.cancelled: break

                # hop implementation
                if self.hopCheckBox.GetValue() and self.executeHop:
                    self.logger.write(str(datetime.datetime.now()) + '[INFO] Performed hop\n')
                    self.mouse.release(pymouse.Button.left)
                    self.timerSleep(self.hop_time_1)
                    self.keyboard.press(pykeyboard.Key.space)
                    self.timerSleep(self.hop_time_2)
                    self.keyboard.release(pykeyboard.Key.space)
                    self.timerSleep(self.hop_time_3)
                    
                    self.mouse.press(pymouse.Button.left)          
                    self.executeHop = False

                # strafe implementation
                if self.strafeCheckBox.GetValue() and self.executeStrafe:
                    self.logger.write(str(datetime.datetime.now()) + '[INFO] Performed strafe\n')
                    self.mouse.release(pymouse.Button.left)
                    self.timerSleep(self.start_pause)
                    
                    self.keyboard.press('s')
                    self.timerSleep(self.strafe_time_1)
                    self.keyboard.release('s')
                    self.timerSleep(self.strafe_time_2)
                    self.keyboard.press('w')
                    self.timerSleep(self.strafe_time_3)
                    self.keyboard.release('w')
                    self.timerSleep(self.strafe_time_4)

                    self.mouse.press(pymouse.Button.left)
                    self.executeStrafe = False

                # command implementation
                if self.commandCheckBox.GetValue() and self.executeCommand:
                    self.logger.write(str(datetime.datetime.now()) + '[INFO] Ran following commands:\n')

                    self.mouse.release(pymouse.Button.left)
                    self.timerSleep(self.start_pause)
                    
                    commands = self.commandList.GetValue()
                    if commands[-1] != '\n': commands += '\n' 

                    for character in commands:
                        if character == '\n':
                            self.keyboard.press(pykeyboard.Key.enter)
                            self.timerSleep(self.enter_time_1)
                            self.keyboard.release(pykeyboard.Key.enter)
                            self.timerSleep(self.enter_time_2) 
                            
                        else:
                            self.keyboard.press(character)
                            self.timerSleep(self.keypress_time_1)
                            self.keyboard.release(character)
                            self.timerSleep(self.keypress_time_2)

                    self.timerSleep(self.start_pause)

                    self.mouse.press(pymouse.Button.left)
                    self.executeCommand = False

                self.timerSleep(self.clickloop_delay)
        
        self.mouse.release(pymouse.Button.left)

        self.running = False
        self.cancelled = False

    def OnStartClick(self, e):
        if not self.running:
            self.running = True 
            self.cancelled = False

            clickThread = threading.Thread(target=self.clickLoop, daemon=True)
            clickThread.start()

        self.logger.write(str(datetime.datetime.now()) + '[INFO] Start button pressed\n')

    def OnStopClick(self, e):
        self.cancelled = True

        self.logger.write(str(datetime.datetime.now()) + '[INFO] Stop button pressed\n')

    def OnHopCheck(self, e):
        if self.hopCheckBox.GetValue():
            self.hopTextBox = wx.TextCtrl(self, name="Hop Delay")
            self.hopTextBox.SetSize(int(.4375 * self.width), int(.5 * self.height), int(.125 * self.width), int(.033 * self.height))
            self.mainSizer.Add(self.hopTextBox, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

            self.hopLabel = wx.StaticText(self, label="Hop interval (seconds):", style=wx.ALIGN_RIGHT)
            self.hopLabel.SetPosition((int(.28125 * self.width), int(.5 * self.height)))
            self.mainSizer.Add(self.hopLabel, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)
        
            self.Bind(wx.EVT_TEXT, self.OnHopTextBoxText, self.hopTextBox)

        else:
            self.hopTextBox.Destroy()
            self.hopLabel.Destroy()

        self.logger.write(str(datetime.datetime.now()) + '[INFO] Hop button checked\n')

    def OnStrafeCheck(self, e):
        if self.strafeCheckBox.GetValue():
            self.strafeTextBox = wx.TextCtrl(self, name="Strafe Delay")
            self.strafeTextBox.SetSize(int(.4375 * self.width), int(0.55 * self.height), int(.125 * self.width), int(.033 * self.height))
            self.mainSizer.Add(self.strafeTextBox, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

            self.strafeLabel = wx.StaticText(self, label="Strafe interval (seconds):", style=wx.ALIGN_RIGHT)
            self.strafeLabel.SetPosition((int(.2725 * self.width), int(0.55 * self.height)))
            self.mainSizer.Add(self.strafeLabel, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

            self.Bind(wx.EVT_TEXT, self.OnStrafeTextBoxText, self.strafeTextBox)

        else:
            self.strafeTextBox.Destroy()
            self.strafeLabel.Destroy()

        self.logger.write(str(datetime.datetime.now()) + '[INFO] Strafe button checked\n')

    def OnCommandCheck(self, e):
        if self.commandCheckBox.GetValue():
            self.commandList = wx.TextCtrl(self, name="Command List", style=wx.TE_MULTILINE)
            self.commandList.SetSize(int(.025 * self.width), int(.683 * self.height), int(.25 * self.width), int(.166 * self.height))
            self.mainSizer.Add(self.commandList, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

            self.commandListLabel = wx.StaticText(self, label="Command list (enter on seperate lines):", style=wx.ALIGN_RIGHT)
            self.commandListLabel.SetPosition((int(.025 * self.width), int(.65 * self.height)))
            self.mainSizer.Add(self.commandListLabel, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

            self.commandTextBox = wx.TextCtrl(self, name="Command Delay")
            self.commandTextBox.SetSize(int(.4375 * self.width), int(.6 * self.height), int(.125 * self.width), int(0.033 * self.height))
            self.mainSizer.Add(self.commandTextBox, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

            self.commandLabel = wx.StaticText(self, label="Command interval (seconds):", style=wx.ALIGN_RIGHT)
            self.commandLabel.SetPosition((int(.2375 * self.width), int(.6 * self.height)))
            self.mainSizer.Add(self.commandLabel, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 20)

            self.Bind(wx.EVT_TEXT, self.OnCommandListText, self.commandList)
            self.Bind(wx.EVT_TEXT, self.OnCommandTextBoxText, self.commandTextBox)
            
        else:
            self.commandList.Destroy()
            self.commandListLabel.Destroy()
            self.commandTextBox.Destroy()
            self.commandLabel.Destroy()

        self.logger.write(str(datetime.datetime.now()) + '[INFO] Command button checked\n')

    # text change monitors
    def OnHopTextBoxText(self, e):
        self.hop_delay = float(self.hopTextBox.GetValue())
    def OnStrafeTextBoxText(self, e):
        self.strafe_delay = float(self.strafeTextBox.GetValue())
    def OnCommandListText(self, e): 
        self.command_list_text = self.commandList.GetValue()
    def OnCommandTextBoxText(self, e):
        self.command_delay = float(self.commandTextBox.GetValue())

run = WindowController("PyGrinder by Andy Hansen", 800, 600)
