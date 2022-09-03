import numpy as np
import uproot as up
import sys
import pickle as pkl
import time
import histlite as hl

#####################################################################
# Inverts a fit of the form y = ax^2 + bx + c
def InverseQuadratic( ADC, a, b, c):
    numerator = ADC + b**2/(4*a) - c
    return np.sqrt(numerator/a) - b/(2*a)


# Calibration constants given in terms of quadratic fit coefficients
# assuming the form ADC = a * (energy)^2 + b * (energy) + c
ge_ecal = [
    np.array([1.16745874e-04, 9.40198923e+01, -1.44391007e+01]),    
    np.array([2.35621651e-04, 9.85061664e+01, 1.86582321e+01]),
    np.array([1.18000296e-05, 2.10868879e+01, 3.23892458e+00]),
    np.array([9.12337961e-06, 2.18929782e+01, 2.81999066e+00])]


ge_tcal = [-184.1,
           -202.1,
           -151.9,
           -190.5]

ns_per_ch = 0.09765

ge_channels = [0,2,4,6]


start = time.time()
def GetElapsedTime():
    return (time.time()-start)/60.

if len(sys.argv) != 2:
    print('Usage: ')
    print('\tMakeReducedSinglesFiles.py <datafile>')
    print('\n')

datadir = '/p/lustre1/lenardo1/tunl_cs136_data/'
filename = sys.argv[1]

filetitle = (filename.split('/')[-1]).split('.')[0]


if 'bin_tree' not in filename or not filename.endswith('.root'):
    print('ERROR: not a valid data file.')
    sys.exit()


print('Opening file...')
#tree = up.open(datadir + filename)['Xe136']
raw_data = {}
variables = ['scp_pickoff', 'scp_amplitude', 'scp_time', 'scp_timestamp', 'scp_pileup']
active_channels = [0,2,4,6]

for var in variables:
    raw_data[var] = []

with up.open(datadir + filename)['Xe136'] as tree:
    counter = 0
    for data in tree.iterate(variables, library='np'):
        counter += 1
        print('\tLoop {}...'.format(counter))
        #print(data)
        #print(len(data['scp_amplitude']))
        #print(len(data['scp_pileup']))
        for var in variables:
            if 'scp_amplitude' == var or 'scp_time' == var or 'scp_pileup' == var:
                raw_data[var].append(data[var][:,active_channels])
            else:
                raw_data[var].append(data[var][:,0])
                
        #if counter > 5: break
    print('\t...done. Time elapsed: {:4.4} min'.format(GetElapsedTime()))

for var in variables:
    raw_data[var] = np.concatenate(raw_data[var])

print('Finished concatenating variables...')
#print(raw_data)

#with open(datadir+'output_test.pkl','wb') as pklfile:
#    pkl.dump(raw_data, pklfile)
#sys.exit()

#######################################################################################

print('...done. Time elapsed: {:4.4} min'.format(GetElapsedTime()))
print(raw_data.keys())



ge_data = {}


for i in range(4):
    print('Reducing Ge{}'.format(2*i))
    tmp_ge_energy = np.copy( raw_data['scp_amplitude'][:,i] )
    calibrated_ge_energy = InverseQuadratic( tmp_ge_energy, *ge_ecal[i] )
    calibrated_ge_time = ( np.copy(raw_data['scp_time'][:,i]) - \
				np.copy(raw_data['scp_pickoff']) ) * ns_per_ch -\
                            ge_tcal[i]

    ge_pileup = np.copy( raw_data['scp_pileup'][:,i] )
    mask = (calibrated_ge_energy == calibrated_ge_energy)
    print('\tNaN cut removes {} of {} events.'.format(np.sum(mask),len(mask)))

    subdict = {}
    subdict['energy'] = calibrated_ge_energy[mask]
    subdict['time']   = calibrated_ge_time[mask]
    subdict['pileup'] = ge_pileup[mask]
    subdict['timestamp']  = raw_data['scp_timestamp']
    #ge_data['Ge{}'.format(i*2)] = subdict
    print('\t...done. Time elapsed: {:4.4} min'.format(GetElapsedTime()))
        
    print('Saving data to pkl file...')
    with open(datadir + 'pickle_files/' + filetitle+'_ge{}.pkl'.format(2*i), 'wb') as pklfile:
       pkl.dump(subdict,pklfile)
    print('\t...done. Time elapsed: {:4.4} min'.format(GetElapsedTime()))

    if i < 2:
         lower = 0.
         upper = 700.
         nbins = 5000
    else:
         lower = 0.
         upper = 3200.
         nbins = 15000 
    
    mask = subdict['pileup'] < 1.
    print('\t\tGenerating histogram...')
    hist = hl.hist( subdict['energy'][mask], \
                                   bins = np.linspace(lower,upper,nbins))

    with open(datadir + 'histograms/' + filetitle + 'hist_{}-{}_ge{}_no_time_cut.pkl'.format(int(lower),int(upper),2*i), 'wb') as pklfile:
       pkl.dump( hist, pklfile )
  

