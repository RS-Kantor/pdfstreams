#!/usr/bin/env python

import sys
import os
from io import BytesIO
from shutil import copyfileobj
from warcio.archiveiterator import ArchiveIterator

def parseone(fname):
    with open(fname, 'rb') as stream:
        shortname = os.path.split(fname)[-1].split('.')[0]
        print("Parsing "+shortname+".warc...")
        cnt = 0
        for record in ArchiveIterator(stream):
            if record.rec_type != 'response' and record.rec_type != 'resource':
                continue
            buf = BytesIO()
            copyfileobj(record.content_stream(), buf)
            buf.seek(0)
            if buf.getbuffer()[0:4] == b"%PDF":
                cnt += 1
                try:
                    os.mkdir('exoutput')
                except:
                    pass
                outf = open(os.path.join('exoutput',shortname+'pdf'+str(cnt)+'.pdf'), 'wb')
                outf.write(buf.read())

def main():
    directory = sys.argv[1]
    print("Reading in "+directory+"...")
    for x in os.listdir(directory):
        if x.split('.')[-1] == 'warc':
            parseone(os.path.join(directory,x))

if __name__=="__main__":
    main()

    
'''

with open('indexes/test3.warc', 'rb') as infil:
    line = infil.readline()
    cnt = 0
    inpdf = False
    while line != '':
        if b'%PDF-' in line:
            cnt += 1
            inpdf = True
            outf = open('extract_out/pdf'+str(cnt)+'.pdf', 'wb')
        if b'WARC/' in line:
            inpdf = False
        if inpdf:
            outf.write(line)
        if b'%%EOF' in line:
            inpdf = False
        if not inpdf:
            try:
                outf.close()
            except:
                pass
        line = infil.readline()
'''
