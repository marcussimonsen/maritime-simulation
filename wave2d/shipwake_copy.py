import numpy as np
import namelist
import wave2d_2
import pickle

import matplotlib.pyplot as plt
plt.ion()

ships = []
defaults = {'typewave': 'gwshort',
            'Lx': 2,
            'Ly': 1,
            'nx': 1024,
            'ny': 512,
            'g': 1.,                            # Gravity
            'H': .1,                            # Water depth
            'sigma': float,                     # Ship length
            'tend': 2,                          # How long the simulation runs
            'tplot': .1,                        # Time intervale between two consecutive frames
            'dt': 1e-2,                         # Time step used in the computation
            'cax': np.asarray([-1., 1.])*20,    # Colorbar interval
            'figwidth': 1080,                   # Figure width (in pixels)
            'plotvector': 'None',               #'energyflux'  # Vector field to superimpose during the animation
            'vectorscale': 10.,                 # Larger 'vectorscale' makes the arrows shorter
            'aspect_ratio': 4.,                 # For the ship, between x and y lengths
            'U': 0.2,                           # Speed
            'generation': 'wake'
            }

defaults['sigma'] = 0.01*defaults['Lx']



# Ship 1
ship1 = namelist.Namelist()
ship1.alphaU = 0*np.pi/180.     # Heading (in degrees)
ship1.x0 = 0.5
ship1.y0 = 0.1                  # x coordinate of the wavepacket
ships.append(ship1)

# Ship 2
ship2 = namelist.Namelist()
ship2.alphaU = 0*np.pi/180.
ship2.x0 = 0.5
ship2.y0 = 0.7
ships.append(ship2)

# Ship 3
ship3 = namelist.Namelist()
ship3.alphaU = 0*np.pi/180.
ship3.x0 = 0.5
ship3.y0 = 1.
ships.append(ship3)


model = wave2d_2.Wave2d(ships, defaults)
model.run(ships, defaults, anim=True)

dt = defaults['dt']
en = model.energy
time = np.arange(0, len(en))*dt
drag = np.mean(np.diff(en)[-50:]/dt) / defaults['U']
print('Estimated drag: %.3g / U = %.2f' % (drag, defaults['U']))
