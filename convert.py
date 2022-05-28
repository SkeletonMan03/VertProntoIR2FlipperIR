from bs4 import BeautifulSoup
import sys
import os
import re
import math
import shutil

#Take input
try:
	inputfile=sys.argv[1]
except IndexError:
	print("Provide a filename with", sys.argv[0], "example.html")
	sys.exit(1)

#create temp file to fix
tempfile=inputfile+"_temp"
shutil.copy(inputfile, tempfile)

#fix the temp file since it has a bunch of opened <div> tags that are never closed and breaks everything
with open(tempfile, 'r') as file:
	filedata=file.read()
filedata=filedata.replace('<div align="left"><br>', '</div><div align="left"><br>')
with open(tempfile, 'w') as file:
	file.write(filedata)

#Open and start finding information
url=tempfile
page=open(url)
soup=BeautifulSoup(page.read(), 'html.parser')
buttons=soup.find_all('font', size='+1')

#create output file in ir Flipper format
outputfile=os.path.splitext(inputfile)[0]+'.ir'
outfile=open(outputfile, 'w+')
outfile.write("Filetype: IR signals file\n")
outfile.write("Version: 1\n")
outfile.close
outfile=open(outputfile, 'a')
for button in buttons:
	#find all of the information, output it and also put it into the ir file
	fulldiv=button.find_previous('div', align="left")
	print("Button:", button.text.strip())
	outfile.write("#\n")
	outfile.write("name: "+button.text.strip()+"\n")
	osc=button.find_next('font', color="#666666")
	print("Oscillate:", osc.text.strip())
	outfile.write("type: raw\n")
	frequencycode=button.find_next('font', color="#800080")
	onetimebyte=button.find_next('font', color='#009900')
	repeatbyte=button.find_next('font', color='#993300')
	print("One Time Byte:", onetimebyte.text.strip())
	print("Repeat Byte:", repeatbyte.text.strip())
	print("Frequency Code:", frequencycode.text)
	ir01s=fulldiv.find_all('span', class_=['IR1', 'IR0'])
	hirs=[]
	for ir01 in ir01s:
		hirs.append(ir01.text.strip())

	#conversion math from http://www.remotecentral.com/features/irdisp1.htm
	frequency=round(1000000/(int(frequencycode.text.strip(), 16)*.241246))
	onetimecode=int(onetimebyte.text.strip(), 16)
	repeatcode=int(repeatbyte.text.strip(), 16)
	#I could be wrong, but from MY understanding, the dutycycle can be anywhere between 25 and 50, but it seemed like all of the existing files I saw was at 0.330000, so I went with that
	dutycycle="0.330000"
	print("One time Code:", onetimecode)
	print("Repeat Code:", repeatcode)
	print("Frequency:", frequency)
	outfile.write("frequency: "+str(frequency)+"\n")
	print("Duty Cycle:", dutycycle)
	outfile.write("duty_cycle: "+str(dutycycle)+"\n")
	print("Converted:")
	outfile.write("data:")
	decoded=[]
	for hir in hirs:
		#Decoded IR math
		decoded.append(round(1000000*int(hir, 16)/frequency))
	for decodedd in decoded:
		print(decodedd, "", end="")
		outfile.write(" "+str(decodedd))
	print("\n")
	outfile.write("\n")
#delete the tempfile
os.remove(tempfile)
