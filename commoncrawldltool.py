#!/usr/bin/env python2
#Ryan Kantor
#Fall 2022

import sys
import os
import requests
import gzip
import warc

from clint.textui import progress

def queue_fromfile(indexfile):

    if not os.path.exists(".\indexes"):
        os.mkdir(".\indexes")

    indices = gzip.open(indexfile)
    line = indices.readline()
    while len(line) > 0:
        dl_file("https://data.commoncrawl.org/" + line.strip(), os.path.join(".\indexes", line.split('/')[-1].strip()))
        line = indices.readline()
    queue_index(".\indexes")

def queue_index(indexdir):

    for x in os.listdir(indexdir):
        print("Searching for PDFs in "+indexdir+"\\"+x+"...")
        find_pdfs(os.path.join(indexdir, x))

def queue_paths(pathsgz):
    
    if not os.path.exists(".\warcs"):
        os.mkdir(".\warcs")

    with gzip.open(pathsgz) as fp:
        for count, line in enumerate(fp):
            pass
    
    i = 1
    pathfile = gzip.open(pathsgz)
    line = pathfile.readline()
    while len(line) > 0:
        print("Downloading WARC file " + str(i) + " of " + str(count + 1))
        i += 1
        warcgz = dl_file("https://data.commoncrawl.org/" + line.strip(), os.path.join(".\warcs", line.split('/')[-1].strip()))
        find_pdfs(warcgz)
        line = pathfile.readline()

def find_pdfs(indices):

    if not os.path.exists(".\warcs"):
        os.mkdir(".\warcs")

    indfile = gzip.open(indices)
    line = indfile.readline()
    while len(line) > 0:
        if 'pdf' in line:
            for i in line.split():
                if 'crawl-data' in i:
                    print("Downloading "+i[1:-2].split('/')[-1])
                    dl_file("https://data.commoncrawl.org/" + i[1:-2], os.path.join(".\warcs", i[1:-2].split('/')[-1]))
        line = indfile.readline()


def find_pdfs_warc(warcgzfile):
    
    for record in warc.open(warcgzfile):
        print(record['Content-Type'])
        if 'pdf' in record['Content-Type']:
            print("found pdf")

def dl_file(dest, filename):

    newpath = '\\'.join(filename.split('\\')[:-1])
    if not os.path.exists(newpath):
        os.mkdir(newpath)
    
    r = requests.get(dest, stream=True)
    
    with open(filename, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
            if chunk:
                f.write(chunk)
                f.flush()
                
    return filename

def main():
    queue_fromfile('cc-index.paths.gz')
       
if __name__=="__main__":
    main()
