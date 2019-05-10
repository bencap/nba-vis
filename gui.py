# Ben Capodanno
# CS251, gui.py
# This file builds a gui using tkinter
# 02/19/2019 updated 04/02/2019

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import math
import random
import numpy as np
from colour import Color
import view
import data
import analysis
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from matplotlib import cm
import matplotlib as mpl

# create a class to build and manage the display
class DisplayApp:

    def __init__(self, width, height):

        # create a tk object, which is the root window
        self.root = tk.Tk()

        # width and height of the window
        self.initDx = width
        self.initDy = height

        # set up the geometry for the window
        self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )

        # set the title of the window
        self.root.title("Viewing Axes")

        # set the maximum size of the window for resizing
        self.root.maxsize( 1024, 768 )

        # bring the window to the front
        self.root.lift()

        # setup the menus
        self.buildMenus()

        # build the controls
        self.buildControls()

        # build the objects on the Canvas
        self.buildCanvas()

        # set up the key bindings
        self.setBindings()

        # Create a View object and set up the default parameters
        self.view = view.View()
        self.view.extent = np.matrix( [.85,.85,.85])

        # Create the axes fields and build the axes
        #      x   y   z   homo
        # x1   0   0   0   1
        # x2   1   0   0   1
        # y1   0   0   0   1
        # y2   0   1   0   1
        # z1   0   0   0   1
        # z2   0   0   1   1

        self.axes_endpoints = np.matrix( [[0.2,-0.2,0,1],[1.4,-0.2,0,1],
                                          [0.2,-0.2,0,1],[0.2,.8,0,1],
                                          [0.2,0.8,0,1], [1.4,.8,0,1],
                                          [1.4,0.8,0,1], [1.4,-0.2,0,1]] )

        self.hoop_endpoints = np.matrix( [[0.77,-0.13,0,1],[0.83,-0.07,0,1]] )

        self.backboard_endpoints = np.matrix( [[0.73,-0.129,0,1],[0.87,-0.129,0,1]])

        self.outerpaint_endpoints = np.matrix( [[0.6,-0.2,0,1], [0.6, 0.25,0,1],
                                                [1.0,-0.2,0,1], [1.0, 0.25,0,1],
                                                [0.6,-0.2,0,1], [1.0,-0.2,0,1],
                                                [0.6, 0.25,0,1], [1.0, 0.25,0,1]] )

        self.innerpaint_endpoints = np.matrix( [[0.65,-0.2,0,1], [0.65, 0.25,0,1],
                                                [0.95,-0.2,0,1], [0.95, 0.25,0,1]])

        self.freethrow_endpoints = np.matrix( [[0.65,0.1,0,1], [0.95, 0.4,0,1],
                                               [0.65,0.1,0,1], [0.95, 0.4,0,1],
                                               [0.7,-0.2,0,1], [0.9, 0.0,0,1]])

        self.threecorner_endpoints = np.matrix( [[0.3,-0.2,0,1], [0.3, 0.1,0,1],
                                                 [1.3,-0.2,0,1], [1.3, 0.1,0,1]])

        self.threebreakpoint_endpoints = np.matrix( [[0.3,-0.3,0,1],[1.3,0.5,0,1]] )

        self.centercourt_endpoints = np.matrix( [[0.625,0.625,0,1], [0.975, 0.975,0,1],
                                               [0.725,0.725,0,1], [0.875, 0.875,0,1]])

        self.threevis_endpoints = np.matrix( [[0.2,-0.2,0,1], [0.3, 0.1,0,1],
                                              [1.3,-0.2,0,1], [1.4, 0.1,0,1]])

        self.ravis_endpoints = np.matrix( [[0.65,-0.2,0,1], [0.95,0.05,0,1],
                                           [0.65,0.05,0,1], [0.95,0.25,0,1]] )

        self.axes = []
        self.court = []
        self.heat = []
        self.buildAxes()
        self.buildCourt()

        # set up the application state
        self.pt_i = 4
        self.objects = []
        self.headers = []
        self.endpoints = []
        self.data = None
        self.players = data.Data( "players.csv" )

        self.color_col = None
        self.size_col = None

    def buildMenus(self):

        # create a new menu
        self.menu = tk.Menu(self.root)

        # set the root menu to our new menu
        self.root.config(menu = self.menu)

        # create a variable to hold the individual menus
        self.menulist = []

        # create a file menu
        filemenu = tk.Menu( self.menu )
        self.menu.add_cascade( label = "File", menu = filemenu )
        self.menulist.append(filemenu)


        # menu text for the elements
        menutext = [ [ 'Open...  \xE2\x8C\x98-O', 'Quit  \xE2\x8C\x98-Q' ] ]

        # menu callback functions
        menucmd = [ [self.handleOpen, self.handleQuit]  ]

        # build the menu elements and callbacks
        for i in range( len( self.menulist ) ):
            for j in range( len( menutext[i]) ):
                if menutext[i][j] != '-':
                    self.menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
                else:
                    self.menulist[i].add_separator()

    # create the canvas object
    def buildCanvas(self):
        self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy - 55 )
        self.canvas.pack( expand=tk.YES, fill=tk.BOTH )
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)

        # create a sepaarator line for the status area
        sep = tk.Frame( self.root, height=2, width=self.initDx, bd=1, relief=tk.SUNKEN )
        sep.pack( side=tk.TOP, padx = 2, pady = 2, fill=tk.X)

        # create a status area that is capable of displaying current point
        self.statusArea = tk.Frame( self.root, width = self.initDx, height = 20 )
        self.statusArea.pack( side=tk.TOP, padx=2, pady=2, fill=tk.X )
        return

	# build a frame and put controls in it
    def buildControls(self):
        # make a big control frame
        self.bigframe = tk.Frame(self.root)
        self.bigframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)
        sep = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
        sep.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)

        # make other cntl frames
        self.cntlframe = tk.Frame(self.bigframe)
        self.cntlframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)

        # make buttons for control frame, enabling user open, plot, and stat
        self.buttons = []
        self.buttons.append( ( 'open', tk.Button( self.cntlframe, text="Open File", command=self.handleOpen, width=12 ) ) )
        self.buttons.append( ( 'plot', tk.Button( self.cntlframe, text="Plot Data", command=self.handlePlotData, width=12 ) ) )
        self.buttons.append( ( 'stat', tk.Button( self.cntlframe, text="Shot Stats", command=self.handleStats, width=12 ) ) )

        # add these buttons to frame
        for bNum in range(len(self.buttons)):
            self.buttons[bNum][1].pack(side=tk.TOP)

        # create list boxes for teams and players
        xLabel = tk.Label( self.cntlframe, text="Teams" )
        self.tmBox = tk.Listbox( self.cntlframe, height = 16, width = 16, exportselection = 0 )
        self.tmBox.bind('<<ListboxSelect>>', self.playerBox )

        yLabel = tk.Label( self.cntlframe, text="Players" )
        self.plyrBox = tk.Listbox( self.cntlframe, height = 6, width = 16, exportselection = 0 )

        self.listboxes = [self.tmBox, self.plyrBox]
        labels = [xLabel, yLabel]
        for t in range(len(self.listboxes)):
            labels[t].pack( side = tk.TOP, pady=2 )
            self.listboxes[t].pack( side = tk.TOP, pady=0 )

        return

    # build team axis box
    def teamBox(self, headers):
        # get unique mappings of team names
        self.teams, self.map = np.unique( np.array( self.players.data_s[:,5] ).T, return_index = True )

        # create team name dictionary of IDs and add names to list boxes
        self.teams2id = {}
        for h in range(len(self.teams)):
            self.teams2id[self.teams[h]] = self.players.data[self.map[h],5]
            self.listboxes[0].insert(h, self.teams[h])
        for u in range(2): # automatically select first two columns for x and y
            self.listboxes[u].select_set(u)
        return

    # build player box
    def playerBox( self, event ):
        self.listboxes[1].delete(0, tk.END)

        # first index off cur select gives index of team, index that into to id for unique team id
        teamID = self.teams2id[self.teams[self.tmBox.curselection()[0]]]
        indices = np.where( self.data.data[:,1] == teamID )

        # these are all shots taken by a team in a given year
        self.teamShots = self.data.data[indices[0]]
        # IDs of the player that took those shots
        currTeamPlayerID = np.unique( np.array( self.teamShots[:,0] ) )
        # Indices of that player ID in the players matrix
        indices = np.where( self.players.data[:,1] == currTeamPlayerID )
        # The player names from x team in y year
        self.currTeamPlayerNames = self.players.data_s[indices[0],0]

        # add names to listbox
        for n in range( np.size( self.currTeamPlayerNames ) ):
            self.listboxes[1].insert(n, self.currTeamPlayerNames[n][0][0,0])

    # create the axis line objects in their default location
    def buildAxes(self):
        for obj in self.axes:
            self.canvas.delete( obj )
        vtm = self.view.build()
        pts = (vtm * self.axes_endpoints.T).T

        self.axes.append( self.canvas.create_line( pts[0,0], pts[0,1], pts[1,0], pts[1,1] ) )
        self.axes.append( self.canvas.create_line( pts[2,0], pts[2,1], pts[3,0], pts[3,1] ) )
        self.axes.append( self.canvas.create_line( pts[4,0], pts[4,1], pts[5,0], pts[5,1] ) )
        self.axes.append( self.canvas.create_line( pts[6,0], pts[6,1], pts[7,0], pts[7,1] ) )
        return

    def buildCourt(self):
        for obj in self.court:
            self.canvas.delete( obj )
        vtm = self.view.build()

        pts = ( vtm * self.hoop_endpoints.T ).T
        hoop = self.canvas.create_oval( pts[0,0], pts[0,1], pts[1,0], pts[1,1],width=2 )

        pts = ( vtm * self.backboard_endpoints.T ).T
        backboard = self.canvas.create_line( pts[0,0], pts[0,1], pts[1,0], pts[1,1],width=3 )

        pts = ( vtm * self.outerpaint_endpoints.T ).T
        outerpaint_left =   self.canvas.create_line( pts[0,0], pts[0,1], pts[1,0], pts[1,1],width=2 )
        outerpaint_right =  self.canvas.create_line( pts[2,0], pts[2,1], pts[3,0], pts[3,1],width=2 )
        outerpaint_bottom = self.canvas.create_line( pts[4,0], pts[4,1], pts[5,0], pts[5,1],width=2 )
        outerpaint_top =    self.canvas.create_line( pts[6,0], pts[6,1], pts[7,0], pts[7,1],width=2 )

        pts = ( vtm * self.innerpaint_endpoints.T ).T
        innerpaint_left =   self.canvas.create_line( pts[0,0], pts[0,1], pts[1,0], pts[1,1],width=2 )
        innerpaint_right =  self.canvas.create_line( pts[2,0], pts[2,1], pts[3,0], pts[3,1],width=2 )

        pts = ( vtm * self.freethrow_endpoints.T ).T
        freethrow_top =     self.canvas.create_arc( pts[0,0], pts[0,1], pts[1,0], pts[1,1], start=0, extent=180, style='arc',width=2 )
        freethrow_bot =     self.canvas.create_arc( pts[2,0], pts[2,1], pts[3,0], pts[3,1], start=0, extent=-180, style='arc',width=1 )
        restricted_area =   self.canvas.create_arc( pts[4,0], pts[4,1], pts[5,0], pts[5,1], start=0, extent=180, style='arc',width=2)

        pts = ( vtm * self.threecorner_endpoints.T ).T
        threecorner_left =   self.canvas.create_line( pts[0,0], pts[0,1], pts[1,0], pts[1,1],width=2 )
        threecorner_right =  self.canvas.create_line( pts[2,0], pts[2,1], pts[3,0], pts[3,1],width=2 )

        pts = ( vtm * self.threebreakpoint_endpoints.T ).T
        threebreakpoint = self.canvas.create_arc( pts[0,0], pts[0,1], pts[1,0], pts[1,1], start=0, extent=180, style='arc',width=2 )

        pts = ( vtm * self.centercourt_endpoints.T ).T
        centercourt_outer =     self.canvas.create_arc( pts[0,0], pts[0,1], pts[1,0], pts[1,1], start=0, extent=-180, style='arc',width=2 )
        centercourt_inner =     self.canvas.create_arc( pts[2,0], pts[2,1], pts[3,0], pts[3,1], start=0, extent=-180, style='arc',width=2 )

        self.court = [hoop,backboard,outerpaint_left,outerpaint_right,outerpaint_bottom,
                      outerpaint_top,innerpaint_left,innerpaint_right, freethrow_top,
                      freethrow_bot, restricted_area, threecorner_left,threecorner_right,
                      threebreakpoint, centercourt_outer, centercourt_inner]

        return

    # modify the endpoints of the axes to their new location
    def updateAxes(self):
        vtm = self.view.build()
        pts = ( vtm * self.axes_endpoints.T).T
        line_i = 0

        # go through and multiply each axis by the transition matrix
        for line in self.axes:
            line = self.canvas.coords( line, pts[line_i * 2,0], pts[line_i * 2,1],
                                             pts[(line_i * 2) + 1,0], pts[(line_i * 2) + 1,1] )
            line_i += 1

        return

    def updateCourt(self):
        vtm = self.view.build()

        pts = ( vtm * self.hoop_endpoints.T ).T
        self.canvas.coords( self.court[0], pts[0,0], pts[0,1], pts[1,0], pts[1,1] )

        pts = ( vtm * self.backboard_endpoints.T ).T
        self.canvas.coords( self.court[1], pts[0,0], pts[0,1], pts[1,0], pts[1,1] )

        pts = ( vtm * self.outerpaint_endpoints.T ).T
        self.canvas.coords( self.court[2], pts[0,0], pts[0,1], pts[1,0], pts[1,1] )
        self.canvas.coords( self.court[3], pts[2,0], pts[2,1], pts[3,0], pts[3,1] )
        self.canvas.coords( self.court[4], pts[4,0], pts[4,1], pts[5,0], pts[5,1] )
        self.canvas.coords( self.court[5], pts[6,0], pts[6,1], pts[7,0], pts[7,1] )

        pts = ( vtm * self.innerpaint_endpoints.T ).T
        self.canvas.coords( self.court[6], pts[0,0], pts[0,1], pts[1,0], pts[1,1] )
        self.canvas.coords( self.court[7], pts[2,0], pts[2,1], pts[3,0], pts[3,1] )

        pts = ( vtm * self.freethrow_endpoints.T ).T
        self.canvas.coords( self.court[8], pts[0,0], pts[0,1], pts[1,0], pts[1,1] )
        self.canvas.coords( self.court[9], pts[2,0], pts[2,1], pts[3,0], pts[3,1] )
        self.canvas.coords( self.court[10],  pts[4,0], pts[4,1], pts[5,0], pts[5,1] )

        pts = ( vtm * self.threecorner_endpoints.T ).T
        self.canvas.coords( self.court[11], pts[0,0], pts[0,1], pts[1,0], pts[1,1] )
        self.canvas.coords( self.court[12], pts[2,0], pts[2,1], pts[3,0], pts[3,1] )

        pts = ( vtm * self.threebreakpoint_endpoints.T ).T
        self.canvas.coords( self.court[13], pts[0,0], pts[0,1], pts[1,0], pts[1,1] )

        pts = ( vtm * self.centercourt_endpoints.T ).T
        self.canvas.coords( self.court[14], pts[0,0], pts[0,1], pts[1,0], pts[1,1] )
        self.canvas.coords( self.court[15], pts[2,0], pts[2,1], pts[3,0], pts[3,1] )

        return

    # clear the canvas of all points and models
    def clearAll( self ):
        # Clear Canvas of Normal Plot Points
        deleted = 0
        for pt in self.objects:
            self.canvas.delete( pt )
            deleted += 1
        self.pt_i = self.pt_i + deleted
        self.objects = []

    # update all plotted points
    def updatePoints( self ):
        if len( self.objects ) == 0:
            return
        vtm = self.view.build()
        pts = ( vtm * self.data.plotting.T).T
        pt_i = 0
        # multiply each point by the transition matrix
        for pt in self.objects:
            pt = self.canvas.coords( pt, pts[pt_i,0], pts[pt_i,1], pts[pt_i,0]-self.size_col[pt_i, 0], pts[pt_i,1]-self.size_col[pt_i, 0] )
            pt_i += 1

        return

    # set canvas bindings
    def setBindings(self):
        self.root.bind( '<Button-1>', self.handleButton1 )
        self.root.bind( '<Control-Button-1>', self.handleButton3 )
        self.root.bind( '<Button-2>', self.handleButton2 )
        self.root.bind( '<Button-3>', self.handleButton3 )
        self.canvas.bind( '<Motion>', self.handleMotion )
        self.root.bind( '<B1-Motion>', self.handleButton1Motion )
        self.root.bind( '<Control-B1-Motion>', self.handleButton3Motion )
        self.root.bind( '<B2-Motion>', self.handleButton2Motion )
        self.root.bind( '<B3-Motion>', self.handleButton3Motion )
        self.root.bind( '<Control-q>', self.handleQuit )
        self.root.bind( '<Control-o>', self.handleOpen )
        self.canvas.bind( '<Configure>', self.handleResize )
        return

    def handleResize(self, event=None):
        # You can handle resize events here
        pass

    # open a file
    def handleOpen(self, event=None ):
        print('handleOpen')
        fn = filedialog.askopenfilename( parent=self.root,
                                           title='Choose a data file', initialdir='.' )
        self.data = data.Data( fn )
        for t in range(len(self.listboxes)): # wipe prev headers from axes listboxes
            self.listboxes[t].delete(0, tk.END)
        self.teamBox( self.data.get_headers() )

        self.shot_types, idx = np.unique( np.array( self.data.data_s[:,1] ).T, return_index = True )
        self.shot_zone, idx = np.unique( np.array( self.data.data_s[:,2] ).T, return_index = True )
        self.shot_zone_len, idx = np.unique( np.array( self.data.data_s[:,3] ).T, return_index = True )

    # close the gui
    def handleQuit(self, event=None):
        print('Terminating')
        self.root.destroy()

    # Reset view to original x-y 2D
    def handleResetButton(self):
        self.view.reset_view()
        self.axes_endpoints = np.matrix( [[0,0,0,1],[1,0,0,1],
                                          [0,0,0,1],[0,1,0,1],
                                          [0,0,0,1],[0,0,1,1]] )
        self.updateAxes()
        self.updateCourt()
        self.updatePoints()
        print('handling reset button')

    def handlePlotData(self):
        # self.chosenData = self.dataO
        self.buildPoints( self.handleChooseAxes() )

    def handleChooseAxes( self ):
        player = self.plyrBox.curselection()[0]
        player_id = self.players.data[np.where( self.players.data_s == self.currTeamPlayerNames[player] )[0],1]
        return player_id[0][0]

    # plot all data user selected
    def buildPoints( self, playerID ):
        self.clearAll() # delete all objects from canvas and clear their lists
        self.view.reset() # reset view object
        self.updateAxes() # redraw axes
        self.updateCourt()

        # indices for player shots, and retrival of string and numerical data
        self.playerShots = np.where( self.data.data[:,0] == playerID )[0]
        self.playerShotStringData = self.data.data_s[self.playerShots,1:4]
        self.playerShotNumData = self.data.data[self.playerShots,2:4]

        makes, misses = self.buildPerc( self.playerShotStringData, self.playerShotNumData, playerID )

        for header in self.data.enum:
            if self.data.enum[header] == "Left Corner 3": left_three = int( header - 1 )
            if self.data.enum[header] == "Right Corner 3": right_three = int( header - 1 )
            if self.data.enum[header] == "Restricted Area": restricted_area = int( header - 1 )
            if self.data.enum[header] == "In The Paint (Non-RA)": paint = int( header - 1 )

        if misses[left_three] + makes[left_three] != 0:
            left_perc = round( ( makes[left_three] / ( misses[left_three] + makes[left_three] ) ) * 100 )
        else: left_perc = 0
        if misses[right_three] + makes[right_three] != 0:
            right_perc = round( ( makes[right_three] / ( misses[right_three] + makes[right_three] ) ) * 100 )
        else: right_perc = 0
        if misses[restricted_area] + makes[restricted_area] != 0:
            ra_perc = round( ( makes[restricted_area] / ( misses[restricted_area] + makes[restricted_area] ) ) * 100 )
        else: ra_perc = 0
        if misses[paint] + makes[paint] != 0:
            paint_perc = round( ( makes[paint] / ( misses[paint] + makes[paint] ) ) * 100 )
        else: ra_perc = 0

        colormap = cm.get_cmap('Reds')

        vtm = self.view.build()
        pts = ( vtm * self.threevis_endpoints.T ).T
        threecorner_left =   self.canvas.create_rectangle( pts[0,0], pts[0,1], pts[1,0], pts[1,1],fill=mpl.colors.to_hex( colormap(left_perc/100)[:-1] ) )
        threecorner_right =  self.canvas.create_rectangle( pts[2,0], pts[2,1], pts[3,0], pts[3,1],fill=mpl.colors.to_hex( colormap(right_perc/100)[:-1] ) )

        pts = ( vtm * self.ravis_endpoints.T ).T
        ravis_whole = self.canvas.create_rectangle( pts[0,0], pts[0,1], pts[1,0], pts[1,1],fill=mpl.colors.to_hex( colormap(ra_perc/100)[:-1] ) )
        paint_whole = self.canvas.create_rectangle( pts[2,0], pts[2,1], pts[3,0], pts[3,1],fill=mpl.colors.to_hex( colormap(paint_perc/100)[:-1] ) )

        self.buildCourt()

    def handleStats( self  ):
        player = self.plyrBox.curselection()[0]
        player_id = self.players.data[np.where( self.players.data_s == self.currTeamPlayerNames[player] )[0],1]
        name_idx = np.where( self.players.data[:,1] == player_id )[0]
        name = self.players.data_s[ name_idx, 0 ]

        # indices for player shots, and retrival of string and numerical data
        self.playerShots = np.where( self.data.data[:,0] == player_id )[0]
        self.playerShotStringData = self.data.data_s[self.playerShots,1:4]
        self.playerShotNumData = self.data.data[self.playerShots,2:4]

        makes, misses = self.buildPerc( self.playerShotStringData, self.playerShotNumData, player_id )

        title = "Numeric Shot Statistics for " + name[0][0,0]
        dialog = Dialog_PCA_Stats( self, self.data.enum, makes, misses, player_id, title )
        pass

    def buildPerc( self, playerString, playerNum, player_id ):
        indices = []
        for k in self.data.enum:
            indices.append( np.where( playerNum[:,0] == k )[0] )

        makes = []
        misses = []

        for idx in indices:
            if len( idx ) < 1:
                makes.append( 0 )
                misses.append( 0 )
                continue
            makes.append( len( np.where( playerNum[idx,1] == 1 )[0] ) )
            misses.append( len( np.where( playerNum[idx,1] == 0 )[0] ) )

        return (makes,misses)

    # translation
    def handleButton1(self, event):
        print('handle button 1: %d %d' % (event.x, event.y))
        self.baseClick = (event.x, event.y)

    # scaling
    def handleButton2(self, event):
        print('handle button 2: %d %d' % (event.x, event.y))
        self.baseClick = (event.x, event.y)
        self.exCopy = self.view.extent

    # rotation
    def handleButton3(self, event):
        print('handle button 3: %d %d' % (event.x, event.y))
        self.baseClick = (event.x, event.y)
        self.viewCopy = self.view.clone()

    # This method displays the point coordinates if the mouse moves over it
    def handleMotion( self, event ):
        event_coords = [ float( event.x ), float( event.y ) ] # format event coord as obj coords will be

        # get each objects coords and check if it is under mouse
        for object in self.objects:
            obj_coords = self.canvas.coords( object )[0:2]
            # print if under mouse
            if obj_coords[0] <= event_coords[0] < obj_coords[0] + 5 and obj_coords[1] <= event_coords[1] < obj_coords[1] + 5:
                text = tk.StringVar( self.root )
                pt = object + 3 - self.pt_i
                if len( self.headers ) == 2:
                    coord1 = "{0:.2f}".format( self.data.data[ object - self.pt_i, self.headers[0] ] )
                    coord2 = "{0:.2f}".format( self.data.data[ object - self.pt_i, self.headers[1] ] )

                    # add a label to the status area that gives a point ( x, y ) on mouse over
                    text.set( "point " + str(pt) + " at " + "( " + coord1 + ", " + coord2 + " )" )
                    self.label = tk.Label( self.statusArea, text=text.get(), width=30 )
                    self.label.pack( side=tk.RIGHT, pady=2 )

                else:
                    coord1 = "{0:.2f}".format( self.data.data[ object - self.pt_i, self.headers[0] ] )
                    coord2 = "{0:.2f}".format( self.data.data[ object - self.pt_i, self.headers[1] ] )
                    coord3 = "{0:.2f}".format( self.data.data[ object - self.pt_i, self.headers[2] ] )

                    # add a label to the status area that gives a point ( x, y ) on mouse over
                    text.set( "point " + str(pt) + " at " + "( " + coord1 + ", " + coord2 + ", " + coord3 + " )" )
                    self.label = tk.Label( self.statusArea, text=text.get(), width=30 )
                    self.label.pack( side=tk.RIGHT, pady=2 )

                return

            # if the mouse moves, delete the label
            else:
                try:
                    self.label.destroy()
                except AttributeError:
                    pass

    # translation
    def handleButton1Motion(self, event):
        print('handle button 1 motion: %d %d' % (event.x, event.y) )
        diff = ( event.x - self.baseClick[0], event.y - self.baseClick[1] )
        self.baseClick = (event.x, event.y)
        d0 = ( diff[0] / self.view.screen[0,0] ) * self.view.extent[0,0]
        d1 = ( diff[1] / self.view.screen[0,1] ) * self.view.extent[0,1]
        self.view.vrp += ( d0 * self.view.u ) + ( d1 * self.view.vup )
        self.updateAxes()
        self.updateCourt()
        self.updatePoints()

    # scaling
    def handleButton2Motion(self, event):
        print('handle button 2 motion: %d %d' % (event.x, event.y) )
        diff = ( event.y - self.baseClick[1] )
        s0 = (100 + diff) / 100
        if s0 > 3: s0 = 3
        if s0 <.1: s0 = .1
        self.view.extent = self.exCopy * s0
        self.updateAxes()
        self.updateCourt()
        self.updatePoints()

    # scaling
    def handleScrollWheel( self, event ):
        s0 = -1.1*(event.delta/120)
        if s0 < 0: s0 = .9
        self.view.extent = self.view.extent * s0
        self.updateAxes()
        self.updateCourt()
        self.updatePoints()

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self.handleScrollWheel )

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    # rotation
    def handleButton3Motion( self, event):
        print('handle button 3 motion: %d %d' % (event.x, event.y) )
        diff = ( event.x - self.baseClick[0], event.y - self.baseClick[1] )
        d0 = ( diff[0] / 150 ) * math.pi
        d1 = ( diff[1] / 150 ) * math.pi
        self.view = self.viewCopy.clone()
        self.view.rotateVRC( d0, -d1 )

        self.updateAxes()
        self.updateCourt()
        self.updatePoints()

    def generateSize( self, scalar ):
        self.size_col = np.multiply( self.size_col, scalar )

    def convertColor( self, x ):
        red = Color("red")
        colors = list(red.range_to(Color("blue"),100))
        return colors[ int( x[0]*99 ) ]

    def generateColor( self ):
        if isinstance( self.color_col[0], Color ):
            return
        rounded = self.color_col[:,0].round( 3 )
        self.color_col = np.apply_along_axis( self.convertColor, 1, rounded )

    def main(self):
        print('Entering main loop')
        self.root.mainloop()

class Dialog_PCA_Stats( tk.Toplevel ):
    def __init__(self, parent, headers, makes, misses, player_id, title = None):

        tk.Toplevel.__init__( self )
        #self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.headers = headers
        self.makes = makes
        self.misses = misses

        body = tk.Frame(self)
        self.result = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        self.geometry("+%d+%d" % (parent.root.winfo_rootx()+100,
                                  parent.root.winfo_rooty()+100))

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        lab = []

        idx = 1

        # place headers
        for header in self.headers:
            tk.Label( master, text = self.headers[header] + "  " ).grid( row = 0, column = idx)
            idx+=1

        tk.Label( master, text = "Makes" ).grid( row = 1, column = 0 )
        tk.Label( master, text = "Misses" ).grid( row = 2, column = 0 )
        tk.Label( master, text = "Percentage" ).grid( row = 3, column = 0 )
        tk.Label( master, text = "Fraction" ).grid( row = 4, column = 0 )

        both = [self.makes, self.misses]
        for i in range( len( self.headers ) ):
            for j in range( len( both ) ):
                tk.Label( master, text = str( both[j][i] ) ).grid( row = j + 1, column = i + 1 )
            if self.misses[i] == 0:
                tk.Label( master, text = "0.0%" ).grid( row = 3, column = i + 1 )
            else:
                tk.Label( master, text = str( round( ( self.makes[i] / ( self.misses[i] + self.makes[i] ) ) * 100 ) ) + "%" ).grid( row = 3, column = i + 1 )
            tk.Label( master, text = str( self.makes[i] ) + " / " + str( self.misses[i] + self.makes[i] ) ).grid( row = 4, column = i + 1)


        return True

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=15, command=self.ok, default="active")
        w.pack(side="left", padx=5, pady=5)

        self.bind("<Return>", self.ok)

        box.pack()

    # standard button semantics
    def ok(self, event=None):

        self.withdraw()
        self.update_idletasks()

        self.parent.root.focus_set()
        self.destroy()

if __name__ == "__main__":
    dapp = DisplayApp(840, 630)
    dapp.main()
