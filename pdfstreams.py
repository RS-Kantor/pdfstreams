#!/usr/bin/env python3
#Ryan Kantor
#Fall 2022
#Requires Python's Py launcher to be installed in order to run pdf-parser.py

import sys
import os
import io
import subprocess

def schedule(directory, stat_switch):
    output = ""
    outdict = {}
    searchdict = {}
    for x in os.listdir(directory):
        print("Parsing "+directory+x+"...")
        if stat_switch:
            if x.endswith(".pdf"):
                get_stats((directory+x),outdict, searchdict)
        else:
            if x.endswith(".pdf"):
                output += extract_streams((directory+x),output)
    if stat_switch:
        render_stats(outdict, searchdict)
    else:
        print(output)

def render_stats(outdict, searchdict):
    for key,val in outdict.items():
        print(key, ':', val)
    print("Search keywords:")
    for key,val in searchdict.items():
        print(key, ':', val)

def extract_streams(filename, output):
    stats = subprocess.check_output(['py', '-2', 'pdf-parser.py', filename]).decode('utf-8')
    stats = io.StringIO(stats)
    line = stats.readline()
    while len(line) > 0:
        tokens = line.split()
        if not tokens:
            tokens.append('dummy')
        if tokens[0] == 'obj':
            num = tokens[1]
            line = stats.readline()
            tokens = line.split()
            streamtype = ''
            if len(tokens) > 1:
                streamtype = '<'+tokens[1]+'>'
            else:
                streamtype = '</Unknown>'
            stats.readline()
            line = stats.readline()
            tokens = line.split()
            if len(tokens) < 2:
                tokens.append('dummy')
                tokens.append('dummy')
            if tokens[0]+tokens[1] == 'Containsstream':
                output += streamtype
                content = subprocess.check_output(['py', '-2', 'pdf-parser.py', '-f', '-o', num, '-c', filename]).decode('utf-8')
                content = io.StringIO(content)
                data = False
                while len(line) > 0 and not data:
                    line = content.readline()
                    tokens = line.split()
                    if len(tokens) < 1: tokens.append('dummy')
                    if tokens[0].startswith("'") and not line.startswith(" 'No filters'"): data = True
                    if data: output += line
                    #if tokens[-1][-1] == "'" and tokens[-1][-2] != "\\": data = False
                content.close()
        line = stats.readline()
    stats.close()
    return output

def get_stats(filename, outdict, searchdict):
    stats = subprocess.check_output(['py', '-2', 'pdf-parser.py', '--stats', filename]).decode('utf-8')
    stats = io.StringIO(stats)
    line = stats.readline()
    while len(line) > 0 and not line.startswith("Search keywords"):
        oncolon = line.split(':')
        if len(oncolon[0].split()) > 1:
            if oncolon[0].split()[-1].isnumeric():
                if not ' '.join(oncolon[0].split()[:-1]) in outdict:
                    outdict[' '.join(oncolon[0].split()[:-1])] = 0
                outdict[' '.join(oncolon[0].split()[:-1])] += int(oncolon[0].split()[-1])
            else:
                if not oncolon[0] in outdict:
                    outdict[oncolon[0]] = 0
                outdict[oncolon[0]] += int(oncolon[1].split()[0].strip(','))
        else:
            if not oncolon[0] in outdict:
                outdict[oncolon[0]] = 0
            outdict[oncolon[0]] += int(oncolon[1].split()[0].strip(','))
        line = stats.readline()
    while len(line) > 0:
        if line.startswith("Search keywords"):
            line = stats.readline()
        oncolon = line.split(':')
        if len(oncolon[0]) > 1:
            if oncolon[0].split()[-1].isnumeric():
                if not ' '.join(oncolon[0].split()[:-1]) in searchdict:
                    searchdict[' '.join(oncolon[0].split()[:-1])] = 0
                searchdict[' '.join(oncolon[0].split()[:-1])] += int(oncolon[0].split()[-1])
            else:
                if not oncolon[0] in searchdict:
                    searchdict[oncolon[0]] = 0
                searchdict[oncolon[0]] += int(oncolon[1].split()[0].strip(','))
        else:
            if not oncolon[0] in searchdict:
                searchdict[oncolon[0]] = 0
            searchdict[oncolon[0]] += int(oncolon[1].split()[0].strip(','))
        line = stats.readline()
        
def main():
    if not os.path.exists(sys.argv[-1]):
        print("Usage: pdfstreams.py [OPTIONS] [TARGET]")
        print("Options:")
        print("    -d - directory: process all pdfs in a directory. Target must be a directory.")
        print("    -s - stats: show the stats of the target pdf(s).")
        quit()
    stat_switch = False
    if '-s' in sys.argv:
        stat_switch = True
    if '-d' in sys.argv:
        print(schedule(sys.argv[-1], stat_switch))
    else:
        if stat_switch:
            outdict = {}
            searchdict = {}
            get_stats(sys.argv[-1], outdict, searchdict)
            render_stats(outdict, searchdict)
        else:
            output = ""
            print(extract_streams(sys.argv[-1], output))

if __name__=="__main__":
    main()
