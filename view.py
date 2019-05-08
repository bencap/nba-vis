# Ben Capodanno
# CS251, data.py
# This file contains a view class that is capable of displaying 3D data
# 02/26/2019 updated 03/08/2019

import numpy as np
import math

class View:

    def __init__( self ):
        self.reset_view()
        self.display = self.build()

    def reset_view( self ):
        self.vrp    = np.matrix( [0.5, 0.5, 1] )
        self.vpn    = np.matrix( [ 0, 0, -1] )
        self.vup    = np.matrix( [ 0, 1, 0] )
        self.u      = np.matrix( [ -1, 0, 0] )
        self.extent = np.matrix( [ 1., 1., 1.] )
        self.screen = np.matrix( [400., 400.] )
        self.offset = np.matrix( [20., 20.] )

    def get_vrp( self ):
        return self.vrp

    def set_vrp( self, vrp ):
        self.vrp = vrp

    def get_vpn( self, ):
        return self.vpn

    def set_vpn( self, vpn ):
        self.vpn = vpn

    def get_vup( self ):
        return self.vup

    def set_vup( self, vup ):
        self.vup = vup

    def get_u( self ):
        return self.u

    def set_u( self, u ):
        self.u = u

    def get_extent( self ):
        return self.extent

    def set_extent( self, extent ):
        self.extent = extent

    def get_screen( self ):
        return self.screen

    def set_screen( self, screen ):
        self.screen = screen

    def get_offset( self ):
        return self.offset

    def set_offset( self, offset ):
        self.offset = offset

    def get_display( self ):
        return self.display

    def normalize( self, v ):
        length = math.sqrt( v[0,0]*v[0,0] + v[0,1]*v[0,1] + v[0,2]*v[0,2] )
        return np.matrix( [v[0,0] / length, v[0,1] / length, v[0,2] / length] )

    def build( self ):
        vtm = np.identity( 4, float )

        t1 = np.matrix( [[1, 0, 0, -self.vrp[0, 0]],
                         [0, 1, 0, -self.vrp[0, 1]],
                         [0, 0, 1, -self.vrp[0, 2]],
                         [0, 0, 0, 1] ] )
        vtm = t1 * vtm

        # order is tu, tvup, tvpn
        transitions = []
        transitions.append( np.cross( self.vup, self.vpn ) )
        transitions.append( np.cross( self.vpn, transitions[0] ) )
        transitions.append( self.vpn )

        for v in transitions:
            v = self.normalize( v )

        self.u = transitions[0]
        self.vup = transitions[1]
        self.vpn = transitions[2]

        # align the axes
        r1 = np.matrix( [[  self.u[0, 0],   self.u[0, 1],   self.u[0, 2], 0.0 ],
                        [ self.vup[0, 0], self.vup[0, 1], self.vup[0, 2], 0.0 ],
                        [ self.vpn[0, 0], self.vpn[0, 1], self.vpn[0, 2], 0.0 ],
                        [              0,              0,              0, 1.0 ]] )

        vtm = r1 * vtm

        vtm = np.matrix( [[1, 0, 0, 0.5 * self.extent[0, 0] ],
                          [0, 1, 0, 0.5 * self.extent[0, 1] ],
                          [0, 0, 1, 0 ],
                          [0, 0, 0, 1 ]] ) * vtm

        vtm = np.matrix( [[ -self.screen[0,0] / self.extent[0,0], 0,0, 0 ],
                         [  0, -self.screen[0,1] / self.extent[0,1], 0, 0 ],
                         [ 0, 0, 1.0 / self.extent[0,2], 0 ],
                         [ 0,  0,  0, 1 ]] ) * vtm

        vtm = np.matrix( [[ 1, 0, 0, self.screen[0,0] + self.offset[0,0] ],
                         [ 0, 1,  0, self.screen[0,1] + self.offset[0,1] ],
                         [ 0, 0,  1, 0 ],
                         [ 0, 0,  0, 1 ]] ) * vtm
        return vtm

    def rotateVRC( self, theta1, theta2 ):
        t1 = np.matrix( [[1, 0, 0, -(self.vrp[0,0] + self.vpn[0,0] * self.extent[0,2] * 0.5)],
                         [0, 1, 0, -(self.vrp[0,1] + self.vpn[0,1] * self.extent[0,2] * 0.5)],
                         [0, 0, 1, -(self.vrp[0,2] + self.vpn[0,2] * self.extent[0,2] * 0.5)],
                         [0, 0, 0,                                                       1]] )

        Rxyz = np.matrix( [[   self.u[0, 0],   self.u[0, 1],   self.u[0, 2], 0.0 ],
                           [ self.vup[0, 0], self.vup[0, 1], self.vup[0, 2], 0.0 ],
                           [ self.vpn[0, 0], self.vpn[0, 1], self.vpn[0, 2], 0.0 ],
                           [              0,              0,              0, 1.0 ]] )

        r1 = np.matrix(  [[ np.cos( theta1 ), 0, np.sin( theta1 ), 0.0 ],
                          [                0, 1,                0, 0.0 ],
                          [-np.sin( theta1 ), 0, np.cos( theta1 ), 0.0 ],
                          [                0, 0,                0, 1.0 ]] )

        r2 = np.matrix(  [[1,                0,              0.0, 0.0 ],
                          [0, np.cos( theta2 ), -np.sin( theta2 ), 0.0 ],
                          [0, np.sin( theta2 ), np.cos( theta2 ), 0.0 ],
                          [0,                0,              0.0, 1.0 ]] )

        t2 = np.matrix( [[1, 0, 0, self.vrp[0,0] + self.vpn[0,0] * self.extent[0,2] * 0.5],
                         [0, 1, 0, self.vrp[0,1] + self.vpn[0,1] * self.extent[0,2] * 0.5],
                         [0, 0, 1, self.vrp[0,0] + self.vpn[0,2] * self.extent[0,2] * 0.5],
                         [0, 0, 0,                                                      1]] )

        tvrc = np.matrix( [[ self.vrp[0, 0],  self.vrp[0,1], self.vrp[0, 2], 1.0 ],
                           [   self.u[0, 0],   self.u[0, 1],   self.u[0, 2], 0.0 ],
                           [ self.vup[0, 0], self.vup[0, 1], self.vup[0, 2], 0.0 ],
                           [ self.vpn[0, 0], self.vpn[0, 1], self.vpn[0, 2], 0.0 ]] )

        tvrc = (t2*Rxyz.T*r2*r1*Rxyz*t1*tvrc.T).T

        self.vrp = np.matrix( tvrc[0, 0:3] )
        self.u = self.normalize( tvrc[1, 0:3] )
        self.vup = self.normalize( tvrc[2, 0:3] )
        self.vpn = self.normalize( tvrc[3, 0:3] )

        return

    def clone( self ):
        view = View()
        view.set_vrp( self.get_vrp().copy() )
        view.set_vpn( self.get_vpn() )
        view.set_vup( self.get_vup() )
        view.set_u( self.get_u() )
        view.set_extent( self.get_extent() )
        view.set_screen( self.get_screen() )
        view.set_offset( self.get_offset() )

        return view


if __name__ == "__main__":
    view = View()
    print( view.get_display() )

    view2 = view.clone()
    print( view2.get_display() )
