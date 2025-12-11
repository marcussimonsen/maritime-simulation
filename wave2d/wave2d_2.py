from __future__ import print_function
import numpy as np

import plotting
import fourier
import wavepackets as wp
import nc_tools as nct
from netCDF4 import Dataset

import matplotlib.pyplot as plt
plt.ion()


class Wave2d(object):
    def __init__(self, param, defaults):
        self.ships = param      # Store list
        self.boats = []         # Each ship has its own wave packet (boat)
        self.set_fourier_space(param[0], defaults)  # Fourier space is ship-independent → initialize once

        # Precompute wave packets for each ship
        for p in param:
            p.checkall() # måske slette?
            self.set_wave_packet(p, defaults)
            self.boats.append(self.hphi0.copy())
            

    def set_fourier_space(self, param, defaults):
        fspace = fourier.Fourier(param, defaults)
        self.fspace = fspace

    def set_wave_packet(self, param, defaults, heading=None):
        if heading is None:
            alphaU = param.alphaU
        else:
            alphaU = heading
        sigma = defaults['sigma']
        aspect_ratio = defaults['aspect_ratio']
        x0, y0 = param.x0, param.y0
        xx, yy = self.fspace.xx, self.fspace.yy
        z = (xx-x0) + 1j*(yy-y0)
        z = z*np.exp(-1j*alphaU)

        if param.waveform == 'gaussian':
            d2 = np.real(z)**2 + (aspect_ratio*np.imag(z))**2
            phi0 = np.exp(-d2/(2*sigma**2))

        elif param.waveform == 'triangle':
            phi0 = wp.triangle(np.real(z), aspect_ratio *
                               np.imag(z), sigma)

        elif param.waveform == 'square':
            phi0 = wp.square(np.real(z), aspect_ratio*np.imag(z), sigma)

        elif param.waveform == 'packet':
            kxx = self.fspace.kxx
            kyy = self.fspace.kyy

            Lx = defaults['Lx']
            k0x = self.fspace.kx[60]
            k0y = self.fspace.kx[30]
            sigma = 10.

            d2 = ((kxx-k0x)*k0x+(kyy-k0y)*k0y)**2
            d2 += 20*((kxx-k0x)*k0y-(kyy-k0y)*k0x)**2
            d2 /= (k0x**2+k0y**2)

            self.hphi = np.exp(-d2/(2*sigma**2)) * np.exp(1j*(kxx*x0+kyy*y0))

            self.hphi *= np.sqrt(param.nx*param.ny)
            self.hphi0 = self.hphi

            phi0 = np.real(np.fft.ifft2(self.hphi))

        self.phi0 = phi0
        if param.waveform != 'packet':
            self.hphi0 = np.fft.fft2(self.phi0)
        self.boat = self.hphi0


    def run(self, param, defaults, anim=True):
        # Single global wave field
        self.hphi = np.zeros_like(self.boats[0])
        # Multiple ships should contribute to one global wave field, not one per ship.

        if anim:
            self.plot = plotting.Plotting(param[0], defaults)
            var = self.fspace.compute_all_variables(self.hphi)
            if defaults['plotvector'] == 'velocity':
                self.plot.init_figure(self.phi0, u=var['u'], v=var['v'])

            elif defaults['plotvector'] == 'energyflux':
                self.plot.init_figure(self.phi0, u=var['up'], v=var['vp'])

            else: # dette er hvad vi gør
                self.plot.init_figure(self.phi0)

        tend = defaults['tend']
        dt = defaults['dt']
        nt = int(tend/dt)
        kxx, kyy = self.fspace.kxx, self.fspace.kyy
        omega = self.fspace.omega
        propagator = np.exp(-1j*omega*dt)

        sigma = defaults['sigma']
        aspect_ratio = defaults['aspect_ratio']
        for p in param:
            x0, y0 = p.x0, p.y0
        xx, yy = self.fspace.xx, self.fspace.yy

        time = 0.
        kplot = np.ceil(defaults['tplot']/dt)
        for p in param:
            #xb, yb = p.x0+defaults['Lx']/2, p.y0+defaults['Ly']/2
            #xb, yb = 0, 0 #p.x0, p.y0
        
            if p.netcdf:
                attrs = {"model": "wave2d_2",
                        "wave": defaults['typewave']}

                sizes = {"y": defaults['ny'], "x": defaults['nx']}

                variables = [{"short": "time",
                            "long": "time",
                            "units": "s",
                            "dims": ("time")},
                            {"short": "p",
                            "long": "pressure anomaly",
                            "units": "m^2 s^-2",
                            "dims": ("time", "y", "x")},
                            {"short": "u",
                            "long": "velocity x-component",
                            "units": "m s^-1",
                            "dims": ("time", "y", "x")},
                            {"short": "v",
                            "long": "velocity y-component (or z-)",
                            "units": "m s^-1",
                            "dims": ("time", "y", "x")},
                            {"short": "up",
                            "long": "up flux x-component",
                            "units": "m^3 s^-3",
                            "dims": ("time", "y", "x")},
                            {"short": "vp",
                            "long": "vp flux y-component",
                            "units": "m^3 s^-3",
                            "dims": ("time", "y", "x")}
                            ]

                fid = nct.NcTools(variables, sizes, attrs,
                                ncfilename=p.filename)
                fid.createhisfile()
                ktio = 0

        energy = np.zeros((nt,))
        
        for kt in range(nt):
            energy[kt] += 0.5*np.mean(np.abs(self.hphi.ravel())**2) # accumulate global energy
            self.hphi = self.hphi*propagator                        # propagate the wave field

            
            if kt == 1:
                print("Max hphi after forcing:", np.max(np.abs(self.hphi)))

            for i, p in enumerate(param):
                # heading
                kalpha = np.cos(p.alphaU)*kxx + np.sin(p.alphaU)*kyy

                # ship position shift in Fourier domain
                shift = np.exp(-1j*(kxx*p.x0 + kyy*p.y0))

                # add forcing from this ship
                self.hphi -= 1j * 1e2 * dt * self.boats[i] * defaults['U'] * kalpha * shift

                # update ship position
                p.x0 += dt * defaults['U'] * np.cos(p.alphaU)
                p.y0 += dt * defaults['U'] * np.sin(p.alphaU)


            kt += 1
            time += dt

            if anim:
                if (kt % kplot == 0):
                    var = self.fspace.compute_all_variables(self.hphi)
                    z2d = var[p.varplot]
                    self.var = var
                    if defaults['plotvector'] == 'velocity':
                        self.plot.update(kt, time, z2d, u=var['u'], v=var['v'])
                    elif defaults['plotvector'] == 'energyflux':
                        self.plot.update(
                            kt, time, z2d, u=var['up'], v=var['vp'])
                    else:
                        self.plot.update(kt, time, z2d)

                    if p.netcdf:
                        with Dataset(p.filename, "r+") as nc:
                            nc.variables["time"][ktio] = time
                            nc.variables["p"][ktio, :, :] = z2d
                            for v in ["u", "v", "up", "vp"]:
                                nc.variables[v][ktio, :, :] = var[v]

                            ktio += 1
            else:
                print('\rkt=%i / %i' % (kt, nt), end='')

        var = self.fspace.compute_all_variables(self.hphi)
        self.energy = energy
        self.var = var