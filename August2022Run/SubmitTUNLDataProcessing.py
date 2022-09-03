#!/usr/local/bin/python

import os
datadir = "/p/lustre1/lenardo1/tunl_cs136_data/"

execdir = "/g/g20/lenardo1/Cs136Measurements/August2022Run/"
macro = "/g/g20/lenardo1/Cs136Measurements/August2022Run/MakeReducedSinglesFiles_Iterate.py"
base = "process_tunl_data"

files = os.listdir(datadir)
#binfiles = [f for f in files if (f.endswith('ls_hit.root') and not f.endswith('reduced.root'))]

#binfiles = [f for f in files if (f.endswith('.root') and not f.endswith('reduced.root') \
#							and not f.endswith('ls_hit.root') \
#							and not f.endswith('xe_hit.root'))]
binfiles = [f for f in files if f.endswith('bin_tree.root')]

numfiles = len(binfiles)
print('{} bin files to process...'.format(numfiles))

i=0
print(datadir)

for i,f in enumerate(binfiles):
	print('{} ({}/{})'.format(f,i,len(binfiles)))
	#if i > 10: break
	#print(f)

	filenum = f.split('.')[0][-3:]
	
	basename = base + '_{}'.format(filenum) 

	scriptfilename = datadir + basename + ".sub"
	os.system( "rm -f " + scriptfilename )
	outfilename = datadir + basename + ".out"
	os.system( "rm -f " + outfilename )

	filetitle = f.split('.')[0]
	
	thescript = "#!/bin/bash\n" + \
		"#SBATCH -t 00:15:00\n" + \
		"#SBATCH -A nuphys\n" + \
		"#SBATCH --ntasks-per-node=1\n" + \
		"#SBATCH -e " + outfilename + "\n" + \
		"#SBATCH -o " + outfilename + "\n" + \
		"#SBATCH --mail-user=bglenardo@gmail.com --mail-type=fail\n" + \
		"#SBATCH -J " + basename + "\n" + \
		"#SBATCH --export=ALL \n" + \
		"source ~/.profile.linux \n" + \
                "cd " + execdir + "\n" + \
		"export STARTTIME=`date +%s`\n" + \
		"echo Start time $STARTTIME\n" + \
		"python " + macro  + " " + f + "\n" + \
		"cd " + datadir + "\n" + \
		"chmod g+rwx *\n" + \
		"export STOPTIME=`date +%s`\n" + \
		"echo Stop time $STOPTIME\n" + \
		"export DT=`expr $STOPTIME - $STARTTIME`\n" + \
		"echo CPU time: $DT seconds\n"
	
	scriptfile = open( scriptfilename, 'w' )
	scriptfile.write( thescript )
	scriptfile.close()
	
	os.system( "sbatch " + scriptfilename )


