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
                                          [0.2,0.8,0,1],[1.4,.8,0,1],
                                          [1.4,0.8,0,1],[1.4,-0.2,0,1]] )

        self.axes = []
        self.court = []
        self.buildAxes()

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
        # x - blue
        # y - red
        # z - green
        self.axes.append( self.canvas.create_line( pts[0,0], pts[0,1], pts[1,0], pts[1,1] ) )
        self.axes.append( self.canvas.create_line( pts[2,0], pts[2,1], pts[3,0], pts[3,1] ) )
        self.axes.append( self.canvas.create_line( pts[4,0], pts[4,1], pts[5,0], pts[5,1] ) )
        self.axes.append( self.canvas.create_line( pts[6,0], pts[6,1], pts[7,0], pts[7,1] ) )
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
        self.updateFits()
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

        # indices for player shots, and retrival of string and numerical data
        self.playerShots = np.where( self.data.data[:,0] == playerID )[0]
        self.playerShotStringData = self.data.data_s[self.playerShots,1:4]
        self.playerShotNumData = self.data.data[self.playerShots,2:4]



    def handleStats( self ):
        pass

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
        self.updatePoints()

    # scaling
    def handleScrollWheel( self, event ):
        s0 = -1.1*(event.delta/120)
        if s0 < 0: s0 = .9
        self.view.extent = self.view.extent * s0
        self.updateAxes()
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

class Dialog_Plot( tk.Toplevel ):

    def __init__(self, parent, headers, title = None):

        tk.Toplevel.__init__( self )
        #self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.headers = headers
        self.cancelled = None

        body = tk.Frame(self)
        self.result = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.root.winfo_rootx()+100,
                                  parent.root.winfo_rooty()+100))

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):

        labx = tk.Label( self, text = "       X-Axis         Y-Axis       Z-Axis   Color Axis Size Axis" )
        x = tk.StringVar(master)
        x.set( self.headers[0] ) # default value
        s = tk.OptionMenu( master, x, *self.headers )
        labx.pack( side = "top" )
        s.pack( side = "left" )

        y = tk.StringVar(master)
        y.set( self.headers[1] ) # default value
        t = tk.OptionMenu( master, y, *self.headers )
        t.pack( side = "left" )

        z = tk.StringVar(master)
        u = tk.OptionMenu( master, z, *self.headers )
        u.pack( side = "left" )

        col = tk.StringVar(master)
        v = tk.OptionMenu( master, col, *self.headers )
        v.pack( side = "left" )

        size = tk.StringVar(master)
        w = tk.OptionMenu( master, size, *self.headers )
        w.pack( side = "left" )

        return (x,y,z,col,size)

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default="active")
        w.pack(side="left", padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side="left", padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    # standard button semantics
    def ok(self, event=None):
        if not self.validate():
            messagebox.showerror("Error", "Please enter a valid integer between 1-1000")
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()
        self.cancel( cancelled = False )

    def cancel( self, event=None, cancelled = True ):
        self.cancelled = cancelled

        self.parent.root.focus_set()
        self.destroy()

    # command hooks
    def validate(self):
        results = []
        for val in self.result:
            results.append( val.get() )
        try:
            for string in results:
                string = str( string )
        except ValueError:
            return 0

        return 1 # override

    def apply(self):
        pass

    def getResult( self ):
        print( self.result[4] )
        return self.result

    def userCancelled( self ):
        return self.cancelled

if __name__ == "__main__":
    dapp = DisplayApp(840, 630)
    dapp.main()
