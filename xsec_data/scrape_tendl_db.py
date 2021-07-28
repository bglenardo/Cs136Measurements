import urllib.request

urlbase = 'https://tendl.web.psi.ch/tendl_2019/proton_file/Ta/Ta181/tables/xs/'

max_num = 3

for a in range(0,max_num+1):
  for he3 in range(0,max_num+1):
    for t in range(0,max_num+1):
      for d in range(0,max_num+1):
        for p in range(0,max_num+1):
          for n in range(0,max_num+1):
             tag = 'xs{}{}{}{}{}{}.tot'.format(n,p,d,t,he3,a)
             url = urlbase + tag
             print('Opening {}'.format(url))
             try:
                 infile = urllib.request.urlopen(url)
             except urllib.error.HTTPError:
                 continue
             output_file_tag = ''
             if a > 0:
                output_file_tag += '{}a'.format(a)
             if he3 > 0:
                output_file_tag += '{}he3'.format(he3)
             if t > 0:
                output_file_tag += '{}t'.format(t)
             if d > 0:
                output_file_tag += '{}d'.format(d)
             if p > 0:
                output_file_tag += '{}p'.format(p)
             if n > 0:
                output_file_tag += '{}n'.format(n)
            
             outfile_name = 'Ta181_p{}_xsec.txt'.format(output_file_tag)
             with open(outfile_name,'w') as outputfile:
                 for line in infile:
                    outputfile.write(line.decode('utf-8'))
                    #decoded_line = line.decode('utf-8')
                    #print(decoded_line)
                    
					

