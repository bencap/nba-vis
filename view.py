# CS251 - Project 3 - view.py - Max Perrello - 3/9/19

import numpy as np
import math
import sys

class View:

	def __init__(self, vrp = np.matrix([0.5, 0.5, 1]), vpn = np.matrix([0, 0, -1]),
		vup = np.matrix([0, 1, 0]), u = np.matrix([-1, 0, 0]),
		extent = np.matrix([1., 1., 1.]), screen = np.matrix([400., 400.]),
		offset = np.matrix([20., 20.])):
		# not calling reset method to accommdate for init calls without value args
		self.vrp = vrp
		self.vpn = vpn
		self.vup = vup
		self.u = u
		self.extent = extent
		self.screen = screen
		self.offset = offset

	def reset(self): # resets all values to defaults
		self.vrp = np.matrix([0.5, 0.5, 1])
		self.vpn = np.matrix([0, 0, -1])
		self.vup = np.matrix([0, 1, 0])
		self.u = np.matrix([-1, 0, 0])
		self.extent = np.matrix([1., 1., 1.])
		self.screen = np.matrix([400., 400.])
		self.offset = np.matrix([20., 20.])

	def build(self): # uses the current viewing parameters to return a view matrix
		vtm = np.identity( 4, float )
		t1 = np.matrix( [
			[1, 0, 0, -self.vrp[0, 0]],
			[0, 1, 0, -self.vrp[0, 1]],
			[0, 0, 1, -self.vrp[0, 2]],
			[0, 0, 0, 1]
			] )
		vtm = t1 * vtm
		tu = np.cross(self.vup, self.vpn)
		tvup = np.cross(self.vpn, tu)
		tvpn = np.copy(self.vpn)
		self.u = self.normalize(tu)
		self.vup = self.normalize(tvup)
		self.vpn = self.normalize(tvpn)
		r1 = np.matrix( [
			[ tu[0, 0], tu[0, 1], tu[0, 2], 0.0 ],
			[ tvup[0, 0], tvup[0, 1], tvup[0, 2], 0.0 ],
			[ tvpn[0, 0], tvpn[0, 1], tvpn[0, 2], 0.0 ],
			[ 0.0, 0.0, 0.0, 1.0 ] 
			] )
		vtm = r1 * vtm
		vtm = self.translate( 0.5*self.extent[0,0], 0.5*self.extent[0,1], 0 ) * vtm
		vtm = self.scale( -self.screen[0,0] / self.extent[0,0], -self.screen[0,1] /
			self.extent[0,1], 1.0 / self.extent[0,2] ) * vtm
		vtm = self.translate( self.screen[0,0] + self.offset[0,0], self.screen[0,1] +
			self.offset[0,1], 0 ) * vtm
		return vtm
		
	def normalize(self, vector): # normalizes and returns the given vector
		vNorm = np.matrix([0., 0., 0.])
		length = math.sqrt( vector[0,0]**2 + vector[0,1]**2 + vector[0,2]**2 )
		vNorm[0,0] = vector[0,0] / length
		vNorm[0,1] = vector[0,1] / length
		vNorm[0,2] = vector[0,2] / length
		return vNorm

	def translate(self, tx, ty, tz): # returns a translation matrix given dimensions
		tMatrix = np.matrix( [
			[1, 0, 0, tx],
			[0, 1, 0, ty],
			[0, 0, 1, tz],
			[0, 0, 0, 1]
			] )
		return tMatrix

	def translateMatrix(self, matrix): # returns translation matrix given hor dim matrix
		tMatrix = np.matrix( [
			[1, 0, 0, matrix[0,0]],
			[0, 1, 0, matrix[0,1]],
			[0, 0, 1, matrix[0,2]],
			[0, 0, 0, 1]
			] )
		return tMatrix

	def alignMatrix(self): # Creates the matrix necessary to re-align an object
		aMatrix = np.matrix( [
			[self.u[0,0], self.u[0,1], self.u[0,2], 0],
			[self.vup.T[0,0], self.vup.T[1,0], self.vup.T[2,0], 0],
			[self.vpn[0,0], self.vpn[0,1], self.vpn[0,2], 0],
			[0, 0, 0, 1]
			] )
		return aMatrix

	def scale(self, tx, ty, tz): # returns a scale matrix given dimensions
		sMatrix = np.matrix( [
			[tx, 0, 0, 0],
			[0, ty, 0, 0],
			[0, 0, tz, 0],
			[0, 0, 0, 1]
			] )
		return sMatrix

	def yRotate(self, vupAngle): # returns a rotation matrix for the y-axis
		# p = np.angle(self.vup) # angle of vup
		rMatrix = np.matrix( [
			[np.cos(vupAngle), 0, np.sin(vupAngle), 0],
			[0, 1, 0, 0],
			[-np.sin(vupAngle), 0, np.cos(vupAngle), 0],
			[0, 0, 0, 1]
			] )
		return rMatrix

	def xRotate(self, uAngle): # returns a rotation matrix for the x-axis
		# p = np.angle(self.u) # angle of u
		rMatrix = np.matrix( [
			[1, 0, 0, 0],
			[0, np.cos(uAngle), -np.sin(uAngle), 0],
			[0, np.sin(uAngle), np.cos(uAngle), 0],
			[0, 0, 0, 1]
			] )
		return rMatrix

	def clone(self): # clones the current view object and returns it
		cloned = View(self.vrp.copy(), self.vpn.copy(), self.vup.copy(), self.u.copy(), self.extent.copy(),
			self.screen.copy(), self.offset.copy())
		return cloned

	def rotateVRC(self, vupAngle, uAngle): # rotates about the center of the view volume
		# Make a translation matrix to move the point ( VRP + VPN * extent[Z] * 0.5 ) to the origin. Put it in t1.
		t1 = self.translateMatrix( self.vrp + self.vpn * self.extent[0,2] * 0.5 )
		# Make an axis alignment matrix Rxyz using u, vup and vpn.
		rXYZ = self.alignMatrix()
		# Make a rotation matrix about the Y axis by the VUP angle, put it in r1.
		r1 = self.yRotate(vupAngle)
		# Make a rotation matrix about the X axis by the U angle. Put it in r2.
		r2 = self.xRotate(uAngle)
		# Make a translation matrix that has the opposite translation from step 1.
		t2 = t1.I
		# Make a numpy matrix where the VRP is on the first row, with a 1 in the homogeneous coordinate, and u, vup, and vpn are the next three rows, with a 0 in the homogeneous coordinate.
		homog = np.matrix([1,0,0,0]) # homogenous coords for addition later
		tvrc =  np.concatenate( (np.concatenate((self.vrp, self.u, self.vup,
			self.vpn), axis=0), homog.T), axis=1 )
		# Execute the following: tvrc = (t2*Rxyz.T*r2*r1*Rxyz*t1*tvrc.T).T
		tvrc = (t2*rXYZ.T*r2*r1*rXYZ*t1*tvrc.T).T
		# Then copy the values from tvrc back into the VRP, U, VUP, and VPN fields and normalize U, VUP, and VPN.
		forCopy = tvrc[:,:3]
		self.vrp = self.normalize(forCopy[0])
		self.u = self.normalize(forCopy[1])
		self.vup = self.normalize(forCopy[2])
		self.vpn = self.normalize(forCopy[3])

def main(argv):
	test = View()
	print( "\n\nBuild:\n", test.build() )
	print( "\n\n---\n\nCloned:\n", test.clone().build(), "\n\n" )
	print( "\n\n---\n\nTranslate:\n", test.translate(1,2,3), "\n\n" )
	print( "\n\n---\n\nScale:\n", test.scale(1,2,3), "\n\n" )


if __name__ == "__main__":
	main(sys.argv)