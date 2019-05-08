# CS 251 Project 5 Display - Max Perrello

import tkinter as tk
from tkinter import filedialog as fd
import math
import random
import numpy as np
import view
import analysis as anal
import data as dat
import PCAData
import PCADialog
from ClusterData import ClusterData

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
		# pca objects (need to be above where controls are built)
		self.PCAObjects = []
		self.pcaResultBox = tk.Listbox()
		# k clustering objects
		self.KObjects = []
		self.kResultBox = tk.Listbox()
		# build the controls
		self.buildControls()
		# build the objects on the Canvas
		self.buildCanvas()
		# set up the key bindings
		self.setBindings()
		# Create a View object and set up the default parameters
		self.vw = view.View()
		# Create the axes fields and build the axes
		self.axes = np.matrix([
			[ 0., 1., 0., 0., 0., 0.],
			[ 0., 0., 0., 1., 0., 0.],
			[ 0., 0., 0., 0., 0., 1.],
			[ 1., 1., 1., 1., 1., 1.]
			])
		# Create field for line objects
		self.lines = []
		self.buildAxes()
		# Initialize list and endpoints for linear regression
		self.linRegObjects = []
		self.linRegEndpts = None
		# set up the application state
		self.objects = []
		self.dataO = None
		# other stuff
		self.scaleF = 1 # scale factor
		self.startPts = None # built points for later

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
		# create another file menu
		function_menu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "Functions", menu = function_menu )
		self.menulist.append(function_menu)
		# menu text for the elements
		menutext = [ [ 'Open...  (Ctrl-O)', '-', 'Quit  (Ctrl-Q)' ], [ 'Linear Regression', '-', 'PCA Analysis' ] ]
		# menu callback functions
		menucmd = [ [self.handleOpen, None, self.handleQuit], [ self.handleLinearRegression, None, self.handlePCAanalysis ]  ]
		# build the menu elements and callbacks
		for i in range( len( self.menulist ) ):
			for j in range( len( menutext[i]) ):
				if menutext[i][j] != '-':
					self.menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
				else:
					self.menulist[i].add_separator()

	# create the canvas object
	def buildCanvas(self):
		self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy )
		self.canvas.pack( expand=tk.YES, fill=tk.BOTH )
		return

	# build a frame and put controls in it
	def buildControls(self):
		self.PCAStatus = False
		self.KStatus = False
		# make a big control frame
		self.bigframe = tk.Frame(self.root)
		self.bigframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)
		sep = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
		sep.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)
		# make other cntl frames
		self.cntlframe = tk.Frame(self.bigframe)
		self.cntlframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)
		# make a cmd 1 button in the frame
		self.buttons = []
		self.buttons.append( ( 'open', tk.Button( self.cntlframe, text="Open File", command=self.handleModO, width=12 ) ) )
		self.buttons.append( ( 'plot', tk.Button( self.cntlframe, text="Plot Data", command=self.handlePlotData, width=12 ) ) )
		self.buttons.append( ( 'linreg', tk.Button( self.cntlframe, text="Plot LinReg", command=self.handleLinearRegression, width=12 ) ) )
		self.buttons.append( ( 'pcawin', tk.Button( self.cntlframe, text="PCA", command=self.togglePCAFrame, width=12 ) ) )
		self.buttons.append( ( 'kwin', tk.Button( self.cntlframe, text="K Means", command=self.toggleKFrame, width=12 ) ) )
		# self.buttons.append( ( 'draw', tk.Button( self.cntlframe, text="Draw Data", command=self.displayPoints, width=8 ) ) )
		for bNum in range(len(self.buttons)): # plot all buttons in list
			self.buttons[bNum][1].pack(side=tk.TOP)  # default side is top
		# self.axesBoxes()
		xLabel = tk.Label( self.cntlframe, text="x-Axis" )
		self.xBox = tk.Listbox( self.cntlframe, height = 3, width = 16, exportselection = 0 )
		yLabel = tk.Label( self.cntlframe, text="y-Axis" )
		self.yBox = tk.Listbox( self.cntlframe, height = 3, width = 16, exportselection = 0 )
		zLabel = tk.Label( self.cntlframe, text="z-Axis" )
		self.zBox = tk.Listbox( self.cntlframe, height = 3, width = 16, exportselection = 0 )
		cLabel = tk.Label( self.cntlframe, text="Colors" )
		self.cBox = tk.Listbox( self.cntlframe, height = 3, width = 16, exportselection = 0 )
		sLabel = tk.Label( self.cntlframe, text="Size" )
		self.sBox = tk.Listbox( self.cntlframe, height = 3, width = 16, exportselection = 0 )
		self.listboxes = [self.xBox, self.yBox, self.zBox, self.cBox, self.sBox]
		labels = [xLabel, yLabel, zLabel, cLabel, sLabel]
		for t in range(len(self.listboxes)):
			labels[t].pack( side = tk.TOP, pady=2 )
			self.listboxes[t].pack( side = tk.TOP, pady=0 )
		self.buildMoreControls()
		self.buildKControls()
		# self.togglePCAFrame()
		return

	def buildMoreControls(self): # builds second control frame
		self.cntlframe2 = tk.Frame(self.bigframe)
		# self.cntlframe2.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)
		self.sep2 = tk.Frame( self.bigframe, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
		# self.sep2.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)
		headLabel = tk.Label(self.cntlframe2, text="PCA Analysis")
		headLabel.pack( side = tk.TOP, pady=4 )
		headSep = tk.Frame( self.cntlframe2, height=2, bd=1, relief=tk.RAISED ) # separator
		headSep.pack(  fill=tk.X, padx=2, pady=4  )
		# PCA Buttons
		runPCA = tk.Button( self.cntlframe2, text="Run Analysis", command=self.runPCA, width=12 )
		plotPCA = tk.Button( self.cntlframe2, text="Plot Results", command=self.handlePlotPCA, width=12 )
		viewPCA = tk.Button( self.cntlframe2, text="View Results", command=self.handleViewPCA, width=12 )
		buttons = [runPCA, plotPCA, viewPCA]
		for n in range(len(buttons)):
			buttons[n].pack( side = tk.TOP, pady = 2 )
		# Button Separator
		buttSep = tk.Frame( self.cntlframe2, height=2, bd=1, relief=tk.RAISED ) # separator
		buttSep.pack(  fill=tk.X, padx=2, pady=4  )
		# PCA Listboxes
		pcaChoiceLabel = tk.Label( self.cntlframe2, text="Chosen Columns" )
		self.pcaChoiceBox = tk.Listbox( self.cntlframe2, height = 10, width = 16, selectmode = 'multiple', exportselection = 0 )
		self.listboxes.append(self.pcaChoiceBox)
		self.pcaResultBox = tk.Listbox( self.cntlframe2, height = 10, width = 16, exportselection = 0 )
		pcaResultLabel = tk.Label( self.cntlframe2, text="PCA Results" )
		listBoxes = [self.pcaChoiceBox, self.pcaResultBox]
		boxLabels = [pcaChoiceLabel, pcaResultLabel]
		# populate the listboxes with axes choices
		for t in range(len(listBoxes)):
			boxLabels[t].pack( side = tk.TOP, pady=2 )
			listBoxes[t].pack( side = tk.TOP, pady=0 )
		return

	def togglePCAFrame(self, force = False):
		if (self.PCAStatus == False) or (force == True):
			self.PCAStatus = True
			self.sep2.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)
			self.cntlframe2.pack( side=tk.RIGHT, padx=2, pady=2, fill=tk.Y )
		else:
			self.PCAStatus = False
			self.cntlframe2.pack_forget()
			self.sep2.pack_forget()

	def runPCA(self): # run pca analysis on selected columns
		pca_targets = []
		for e in range(len( self.pcaChoiceBox.curselection() )):
			pca_targets.append(self.dataO.get_headers()
				[self.pcaChoiceBox.curselection()[e]])
		self.PCAObjects.append( anal.pca(self.dataO, pca_targets) )
		cur_len = len(self.PCAObjects)
		nam = "PCA " + "{:02d}".format(cur_len)
		self.pcaResultBox.insert(cur_len, nam) # maybe END instead of len()
		# print("PCAObjects: ", self.PCAObjects)

	def handleViewPCA(self): # view PCA numerical results in table
		self.createPCADialog()
		# pass

	def createPCADialog(self): # create the dialog box for setting up linear regression
		dialog = PCADialog.PCADialog(self.root, self.PCAObjects[
			self.pcaResultBox.curselection()[0]])
		# dialog = PCADialog.PCADialog(self.root)
		# if ( dialog.getCancelled() == False ):
		# 	# dialog.getLinReg()
		# 	print("successful dialog!")

	def buildKControls(self): # builds second control frame
		self.cntlframe3 = tk.Frame(self.bigframe)
		# self.cntlframe2.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)
		self.sep3 = tk.Frame( self.bigframe, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
		# self.sep2.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)
		headLabel = tk.Label(self.cntlframe3, text="K Clustering")
		headLabel.pack( side = tk.TOP, pady=4 )
		headSep = tk.Frame( self.cntlframe3, height=2, bd=1, relief=tk.RAISED ) # separator
		headSep.pack(  fill=tk.X, padx=2, pady=4  )
		# K Spinbox
		def_var = tk.IntVar(value=2)
		self.k_spin = tk.Spinbox(self.cntlframe3, from_=0, to=10, width=13, textvariable=def_var, justify='center') # FIX UPPER LIMIT LATER
		self.k_spin.pack()
		# K Buttons
		runK = tk.Button( self.cntlframe3, text="Run Analysis", command=self.runK, width=12 )
		plotK = tk.Button( self.cntlframe3, text="Plot Results", command=self.handlePlotK, width=12 )
		viewK = tk.Button( self.cntlframe3, text="View Results", command=self.handleViewK, width=12 )
		buttons = [runK, plotK, viewK]
		for n in range(len(buttons)):
			buttons[n].pack( side = tk.TOP, pady = 2 )
		# Button Separator
		buttSep = tk.Frame( self.cntlframe3, height=2, bd=1, relief=tk.RAISED ) # separator
		buttSep.pack(  fill=tk.X, padx=2, pady=4  )
		# K Listboxes
		kChoiceLabel = tk.Label( self.cntlframe3, text="Chosen Columns" )
		self.kChoiceBox = tk.Listbox( self.cntlframe3, height = 10, width = 16, selectmode = 'multiple', exportselection = 0 )
		self.listboxes.append(self.kChoiceBox)
		self.kResultBox = tk.Listbox( self.cntlframe3, height = 10, width = 16, exportselection = 0 )
		kResultLabel = tk.Label( self.cntlframe3, text="K Results" )
		listBoxes = [self.kChoiceBox, self.kResultBox]
		boxLabels = [kChoiceLabel, kResultLabel]
		# populate the listboxes with axes choices
		for t in range(len(listBoxes)):
			boxLabels[t].pack( side = tk.TOP, pady=2 )
			listBoxes[t].pack( side = tk.TOP, pady=0 )
		return

	def toggleKFrame(self, force = False):
		if (self.KStatus == False) or (force == True):
			self.KStatus = True
			self.sep3.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)
			self.cntlframe3.pack( side=tk.RIGHT, padx=2, pady=2, fill=tk.Y )
		else:
			self.KStatus = False
			self.cntlframe3.pack_forget()
			self.sep3.pack_forget()

	def runK(self): # run pca analysis on selected columns
		k_targets = []
		for e in range(len( self.kChoiceBox.curselection() )):
			k_targets.append(self.dataO.get_headers()
				[self.kChoiceBox.curselection()[e]])
		self.KObjects.append( anal.kmeans( self.dataO, k_targets, int(self.k_spin.get()) ) )
		cur_len = len(self.KObjects)
		nam = "K " + "{:02d}".format(cur_len)
		self.kResultBox.insert(cur_len, nam) # maybe END instead of len()
		pass

	def handleViewK(self): # view PCA numerical results in table
		# self.createKDialog()
		pass

	def createKDialog(self): # create the dialog box for setting up linear regression
		# dialog = PCADialog.PCADialog(self.root, self.PCAObjects[
		# 	self.pcaResultBox.curselection()[0]])
		pass

	def axesBoxes(self, headers): # builds axes boxes
		for t in range(len(self.listboxes)):
			for h in range(len(headers)):
				self.listboxes[t].insert(h, headers[h])
		for u in range(2): # automatically select first two columns for x and y
			self.listboxes[u].select_set(u)
		return

	# create the axis line objects in their default location
	def buildAxes(self):
		vtm = self.vw.build()
		pts = vtm * self.axes
		xLine = self.canvas.create_line( pts[0,0], pts[1,0], pts[0,1], pts[1,1], fill='red' )
		yLine = self.canvas.create_line( pts[0,2], pts[1,2], pts[0,3], pts[1,3], fill='green' )
		zLine = self.canvas.create_line( pts[0,4], pts[1,4], pts[0,5], pts[1,5], fill='yellow' )
		self.lines.append(xLine)
		self.lines.append(yLine)
		self.lines.append(zLine)

	# modify the endpoints of the axes to their new locations
	def updateAxes(self):
		vtm = self.vw.build()
		pts = vtm * self.axes
		self.canvas.coords( self.lines[0], pts[0,0], pts[1,0], pts[0,1], pts[1,1] ) # xLine
		self.canvas.coords( self.lines[1], pts[0,2], pts[1,2], pts[0,3], pts[1,3] ) # yLine
		self.canvas.coords( self.lines[2], pts[0,4], pts[1,4], pts[0,5], pts[1,5] ) # zLine

	# modify the endpoints of the lin reg line to their new locations
	def updateFits(self):
		vtm = self.vw.build()
		pts = vtm * self.linRegEndpts
		self.canvas.coords( self.linRegObjects[0], pts[0,0],
			pts[1,0], pts[0,1], pts[1,1] )

	def setBindings(self):
		self.root.bind( '<Button-1>', self.handleButton1 )
		self.root.bind( '<Button-2>', self.handleButton2 )
		self.root.bind( '<Button-3>', self.handleButton3 )
		self.root.bind( '<B1-Motion>', self.handleButton1Motion )
		self.root.bind( '<B2-Motion>', self.handleButton2Motion )
		self.root.bind( '<B3-Motion>', self.handleButton3Motion )
		self.root.bind( '<Control-q>', self.handleQuit )
		self.root.bind( '<Control-o>', self.handleModO )
		self.root.bind( '<Control-Button-1>', self.handleButton2 )
		self.root.bind( '<Control-B1-Motion>', self.handleButton2Motion )
		self.canvas.bind( '<Configure>', self.handleResize )
		return

	def handleResize(self, event=None):
		# You can handle resize events here
		pass

	def handleModO(self, event=None):
		self.handleOpen()

	def handleQuit(self, event=None):
		print('Terminating')
		self.root.destroy()

	def handleButton1(self, event):
		self.baseClick1 = (event.x, event.y)
		self.baseVRP = self.vw.clone().vrp
		# print('handle button 1: %d %d' % (event.x, event.y))

	# rotation
	def handleButton2(self, event):
		self.baseClick2 = (event.x, event.y)
		self.baseView = self.vw.clone()
		# print('handle button 2: %d %d' % (event.x, event.y))

	# scaling
	def handleButton3(self, event):
		self.baseClick3 = (event.x, event.y)
		self.baseExtent = self.vw.clone().extent
		# print('handle button 3: %d %d' % (event.x, event.y))

	# translation
	def handleButton1Motion(self, event):
		(dx, dy) = ( (event.x - self.baseClick1[0]), (event.y - self.baseClick1[1]) )
		delta0 = ( dx / self.vw.screen[0,0] ) * self.vw.extent[0,0]
		delta1 = ( dy / self.vw.screen[0,1] ) * self.vw.extent[0,1]
		self.vw.vrp = self.baseVRP + (delta0 * self.vw.u) + (delta1 * self.vw.vup)
		self.updateAxes()
		# print("\n\n\n\nlinRegObjects: ", self.linRegObjects, "\n\n\n\n")
		if ( len(self.linRegObjects) != 0 ):
			self.updateFits()
		self.updatePoints()
		# print('handle button 1 motion: %d %d' % (event.x, event.y) )
		# print('diff: (%d, %d)' % (dx, dy) )
	
	def handleButton2Motion(self, event):
		(dx, dy) = ( (event.x - self.baseClick2[0]), (event.y - self.baseClick2[1]) )
		delta0 = (dx / 200) * math.pi
		delta1 = (dy / 200) * math.pi
		self.vw = self.baseView.clone()
		self.vw.rotateVRC(delta0, delta1)
		self.updateAxes()
		if ( len(self.linRegObjects) != 0 ):
			self.updateFits()
		self.updatePoints()
		# print('handle button 2 motion: %d %d' % (event.x, event.y) )

	def handleButton3Motion( self, event):
		dy = -(event.y - self.baseClick3[1])
		# Starts at 1, so it begins scaling immediately. 
		# Also ensures that the distance traveled down for minimum
		# scale is the same as distance traveled up for maximum scale.
		if (dy < 0.0):
			self.scaleF = 1 + (dy / 555)
			if (self.scaleF < 0.1):
				self.scaleF = 0.1
		elif (dy > 0.0):
			self.scaleF = 1 + (dy / 250)
			if (self.scaleF > 3.0):
				self.scaleF = 3.0
		self.vw.extent = self.baseExtent / self.scaleF
		self.updateAxes()
		if ( len(self.linRegObjects) != 0 ):
			self.updateFits()
		self.updatePoints()
		# print('dy: %f' % dy )
		# print('scaleF: %f' % self.scaleF)

	def handleOpen(self):
		fn = fd.askopenfilename( parent=self.root,
		title='Choose a data file', initialdir='.' )
		self.dataO = dat.Data(fn)
		for t in range(len(self.listboxes)): # wipe prev headers from axes listboxes
			self.listboxes[t].delete(0, tk.END)
		self.axesBoxes( self.dataO.get_headers() )

	def handlePlotPCA(self):
		print("handlePlotPCA is running, that sneaky bastard")
		self.handlePlotData(True)

	def handlePlotK(self):
		print("handlePlotK is running, that sneaky bastard")
		self.handlePlotData(False, True)

	def handlePlotData(self, pca = False, k = False):
		if pca == False and k == False:
			print("PCA == False")
			# self.chosenData = self.dataO
			self.buildPoints( self.handleChooseAxes() )
		elif pca == True and self.pcaResultBox.curselection() and k == False:
			# accounting for undispalyed axes
			data = self.PCAObjects[self.pcaResultBox.curselection()[0]]
			self.colorAxis = 255 *np.matrix(np.ones(data.get_data().shape[0] )).T
			self.sizeAxis = 5 *np.matrix(np.ones(data.get_data().shape[0] )).T
			# end unused axes stuff
			print("PCA == True\n", self.pcaResultBox.curselection())
			# self.chosenData = self.PCAObjects[self.pcaResultBox.curselection()[0]]
			self.buildPoints( self.PCAObjects[
				self.pcaResultBox.curselection()[0]].get_headers()[0:3], True )
			# cutting off all but first 3
		elif k == True and self.kResultBox.curselection() and pca == False:
			# accounting for undisplayed axes
			data = self.KObjects[self.kResultBox.curselection()[0]]
			# self.colorAxis = 255 *np.matrix(np.ones(data.get_data().shape[0] )).T
			temp_colors = []
			# Color Axis Setup
			# color bank
			color_list = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8',
				'#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c',
				'#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8',
				'#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075',
				'#808080', '#ffffff', '#000000']
			# build color column using codes
			for i in range(data.get_codes().shape[0]):
				temp_colors.append(color_list[np.squeeze(data.get_codes().T)[i]])
			self.colorAxis = np.matrix([temp_colors]).T
			# Finish Color Axis Setup
			self.sizeAxis = 5 *np.matrix(np.ones(data.get_data().shape[0] )).T
			# end unused axes stuff
			print("K == True\n", self.kResultBox.curselection())
			# self.chosenData = self.PCAObjects[self.pcaResultBox.curselection()[0]]
			self.buildPoints( self.KObjects[
				self.kResultBox.curselection()[0]].get_headers(), False, True )
			# to cut off all but first 3, use [0:3]
		else:
			print("PCA == Skipping\n", self.pcaResultBox.curselection())
			return

	def handleChooseAxes(self, pca = False, k = False):
		if pca == False:
			data = self.dataO
		else:
			data = self.PCAObjects[self.pcaResultBox.curselection()[0]]
		if self.zBox.curselection(): # checks to see if a z column is selected
			# populates list with header selections for each axis
			chosenHeaders = [data.get_headers()[self.xBox.curselection()[0]],
				data.get_headers()[self.yBox.curselection()[0]],
				data.get_headers()[self.zBox.curselection()[0]]]
		else: # if not, just creates a list with x and y selections
			chosenHeaders = [data.get_headers()[self.xBox.curselection()[0]],
				data.get_headers()[self.yBox.curselection()[0]]]
		if self.cBox.curselection(): # checks to see if a color column is selected
			# grabs, normalizes (and scales to 1-255) axis chosen to be represented by color
			self.colorAxis = 255 * anal.normalize_columns_separately([
				data.get_headers()[self.cBox.curselection()[0]]], self.dataO)
		else: # if not, creates a matrix of 255 (uniform blue color)
			self.colorAxis = 255 *np.matrix(np.ones(data.get_data().shape[0] )).T
		if self.sBox.curselection(): # checks to see if a size column is selected
			# grabs, normalizes (and scales to 1-30) axis chosen to be represented by size
			self.sizeAxis = 10 * anal.normalize_columns_separately([
				data.get_headers()[self.sBox.curselection()[0]]], data)
		else: # if nothing is selected, it creates a matrix of 5 (desired uniform size)
			self.sizeAxis = 5 *np.matrix(np.ones(data.get_data().shape[0] )).T
		return chosenHeaders

	def buildPoints(self, headers, pca = False, k = False): # builds and prepares the points for plotting
		self.wipeAllObjects() # delete all objects from canvas and clear their lists
		self.vw.reset() # reset view object
		self.updateAxes() # redraw axes
		if pca == False and k == False:
			self.chosenData = anal.normalize_columns_separately(headers, self.dataO)
		elif pca == True and k == False:
			self.chosenData = anal.normalize_columns_separately(headers,
				self.PCAObjects[self.pcaResultBox.curselection()[0]])
		elif pca == False and k == True:
			self.chosenData = anal.normalize_columns_separately(headers,
				self.KObjects[self.kResultBox.curselection()[0]])
		# print("Chosen Data After Normalization:\n", self.chosenData)
		if len(headers) == 2:
			# vert matrix w ones and proper rows is concatenated onto the right side
			self.chosenData = np.concatenate( ( self.chosenData, (np.matrix(np.zeros(
				self.chosenData.shape[0] )).T) ), axis=1)
			# print("\n\nChosen Data: ", self.chosenData, "\n\n")
		elif len(headers) == 3:
			pass
		else:
			print("\nToo Many Columns!\n")
		# vert matrix w zeros and proper rows is concatenated onto the right side
		self.chosenData = np.concatenate( ( self.chosenData, (np.matrix(np.ones(
			self.chosenData.shape[0] )).T) ), axis=1) # vert matrix w proper rows
		# print("\n\nChosen Data:\n", self.chosenData, "\n\n")
		vtm = self.vw.build()
		# print("built")
		pts = (vtm * self.chosenData.T).T
		self.displayPoints(pts, k) # k == True doesn't call colorMaker

	def displayPoints(self, pts, k = False): # actually draws the new points on the screen
		for n in range(len(pts)):
			# print("n: ", pts[n])
			color = None
			if k == False:
				color = self.colorMaker(self.colorAxis[n,0])
			else:
				color = self.colorAxis[n,0]
			dx = self.sizeAxis[n,0]
			oval = self.canvas.create_oval(pts[n,0] - dx,
				pts[n,1] - dx, pts[n,0] + dx, pts[n,1] + dx,
				fill = color)
			self.objects.append(oval)

	def wipeAllObjects(self): # deletes all objects from canvas and clears lists
		for i in range(len(self.objects)): # delete items in objects list from canvas
			self.canvas.delete(self.objects[i])
		self.objects = [] # clear objects list
		for u in range(len(self.linRegObjects)): # delete lin reg objects
			if u == 0:
				# for n in range(len(self.linRegObjects[u])): # delete multiple lin reg lines
				# 	self.canvas.delete(self.linRegObjects[u][n]) # delete multiple lin reg lines
				self.canvas.delete(self.linRegObjects[u])
			else:
				self.linRegObjects[u].destroy()
		self.linRegObjects = [] # clear lin reg objects list

	# modify the datapoints to their new location
	def updatePoints(self):
		if len(self.objects) == 0:
			return
		vtm = self.vw.build()
		pts = (vtm * self.chosenData.T).T
		for dp in range(len(self.objects)):
			newPt = pts[dp]
			dx = self.sizeAxis[dp,0]
			self.canvas.coords( self.objects[dp], newPt[0,0] - dx,
				newPt[0,1] - dx, newPt[0,0] + dx, newPt[0,1] + dx )

	def colorMaker(self, val): # creates the properly formatted tkinter color code
		r = (255 - val)
		g = r
		b = val
		letters = (int(r),int(g),int(b)) # string/int-ed nums
		color = ('#%02x%02x%02x' % letters)
		return color

	def handleLinearRegression(self): # set up linear regression
		if len(self.linRegObjects) != 0: # if a lin reg line already exists, delete it
			self.canvas.delete(self.linRegObjects[0])
		self.linRegObjects = []
		indVar = self.handleChooseAxes()[0] # set x-axis selection to ind var
		depVar = self.handleChooseAxes()[1] # set y-axis selection to dep var
		curLinReg = anal.single_linear_regression(self.dataO,
			indVar, depVar) # do single linear regression on x and y cols
		self.buildLinearRegression(curLinReg) # build regression line

	def handlePCAanalysis(self): # set up linear regression
		self.togglePCAFrame(True) # force ON

	def buildLinearRegression(self, curLinReg): # given linReg info, builds the reg line
		(slope, intercept, r_value, p_value, std_err, xMin,
		xMax, yMin, yMax) = curLinReg # assign appropriate vars to results of lin reg
		yStart = ((xMin * slope + intercept) - yMin)/(yMax - yMin)
		yEnd = ((xMax * slope + intercept) - yMin)/(yMax - yMin)
		self.linRegEndpts = np.matrix([
			[ 0., 1.],
			[ yStart, yEnd],
			[ 0., 0.],
			[ 1., 1.]
			])
		vtm = self.vw.build()
		pts = vtm * self.linRegEndpts
		linRegLine = self.canvas.create_line( pts[0,0],
			pts[1,0], pts[0,1], pts[1,1], fill='black' )
		self.linRegObjects.append(linRegLine)
		linResLabels = self.buildLinearResults(slope, intercept, r_value)
		for p in range(5):
			self.linRegObjects.append(linResLabels[p])

	def buildLinearResults(self, slope, intercept, rVal): # Displays results of linear regression
		linResults = tk.Label( self.cntlframe, text="LinReg Results" ) # title label
		linSep = tk.Frame( self.cntlframe, height=2, bd=1, relief=tk.RAISED ) # separator
		linSlope = tk.Label( self.cntlframe, text="Slope: %f" % slope ) # slope
		linInt = tk.Label( self.cntlframe, text="Intercept: %f" % intercept ) # intercept
		linRVal = tk.Label( self.cntlframe, text="R-value: %f" % rVal ) # r-value
		linResLabels = [linResults, linSep, linSlope, linInt, linRVal]
		for k in range(len(linResLabels)):
			if k != 1: # pack labels
				linResLabels[k].pack( side = tk.TOP, pady=3 )
			else: # pack separator
				linResLabels[k].pack( fill=tk.X, padx=2, pady=1 )
		return linResLabels

	def main(self):
		print('Entering main loop')
		self.root.mainloop()

if __name__ == "__main__":
	dapp = DisplayApp(840, 630)
	dapp.main()