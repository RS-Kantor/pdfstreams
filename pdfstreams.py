#!/usr/bin/env python3
#Ryan Kantor
#Fall 2022
#Requires Python's Py launcher to be installed and to share a directory with Didier Stevens' pdf-parser.py

import sys
import os
import io
import subprocess

def schedule(directory, stat_switch, allobjs, generics):
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
                output += extract_streams((directory+x),output, allobjs, generics, recom)
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

#this function now also retrieves objects on which the stream may depend such as fonts and font descriptors.
def extract_streams(filename, output, allobjs, generics, recom):
    refdict = {}
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
                streamtype = '{'+tokens[1]+'} '
            else:
                streamtype = '{/UnknownStreamType} '
            line = stats.readline()
            tokens = line[:-2].split(':')[1].split(',')
            #object num:object type
            if not tokens[0] == ' ':
                for i in range(0, len(tokens)):
                    refnum = tokens[i].split()[0]
                    if not (tokens[i] in refdict.keys()):
                        refcontent = subprocess.check_output(['py', '-2', 'pdf-parser.py', '-o', refnum, filename]).decode('utf-8')
                        refcontent = io.StringIO(refcontent)
                        refcontent.readline()
                        reftype = refcontent.readline().split()
                        if len(reftype) > 1:
                            refdict[tokens[i].strip()] = '{'+' '.join(reftype[1:])+'}'
                        else:
                            refdict[tokens[i].strip()] = '{/UnknownStreamType}'
            line = stats.readline()
            tokens = line.split()
            if len(tokens) < 2:
                tokens.append('dummy')
                tokens.append('dummy')
            #the following conditional makes this program only parse out objects which contain streams
            #unless allobjs is true
            if allobjs or tokens[0]+tokens[1] == 'Containsstream':
                output += streamtype
                if tokens[0]+tokens[1] == 'Containsstream':
                    content = subprocess.check_output(['py', '-2', 'pdf-parser.py', '-f', '-o', num, '-c', filename]).decode('utf-8')
                else:
                    content = subprocess.check_output(['py', '-2', 'pdf-parser.py', '-o', num, filename]).decode('utf-8')
                content = io.StringIO(content)
                data = False
                while len(line) > 0: #and not data:
                    line = content.readline()
                    tokens = line.split()
                    if len(tokens) < 1: tokens.append('dummy')
                    if tokens[0] == '<<':
                        carrotlevel = 1
                        output += ' '.join(tokens) + ' '
                        while carrotlevel > 0:
                            line = content.readline()
                            tokens = line.split()
                            output += ' '.join(tokens) + ' '
                            if '<<' in tokens:
                                carrotlevel += 1
                            if '>>' in tokens:
                                carrotlevel -= 1
                    #if tokens[0].startswith("'") and not line.startswith(" 'No filters'"): data = True
                    #if data: output += ' '.join(tokens)
                    #if tokens[-1][-1] == "'" and tokens[-1][-2] != "\\": data = False
                    if line.startswith(" 'No filters'"):
                        line = content.readline()
                        tokens = line.split()
                    if tokens[0].startswith("'"):
                        output += 'stream '
                        while len(line) > 0:
                            output += (' '.join(tokens)).strip('\'\"')
                            line = content.readline()
                            tokens = line.split()
                        output += ' endstream'
                content.close()
            output += '\n\n'
        line = stats.readline()
    stats.close()
    if generics:
        for i in refdict:
            #print(i + ' = ' + refdict[i])
            output = output.replace(i, refdict[i])
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
        print("    -a - all objects: parse out objects which do not contain streams as well.")
        print("    -g - generics: replaces explicit references to other objects with generic type identifiers.")
        print("    -r - recombinable: includes information necessary for recombination in output.")
        quit()
    stat_switch = False
    if '-r' in sys.argv:
        recom = True
    else:
        recom = False
    if '-s' in sys.argv:
        stat_switch = True
    else:
        stat_switch = False
    if '-a' in sys.argv:
        allobjs = True
    else:
        allobjs = False
    if '-g' in sys.argv:
        generics = True
    else:
        generics = False
    if '-d' in sys.argv:
        print(schedule(sys.argv[-1], stat_switch, allobjs, generics))
    else:
        if stat_switch:
            outdict = {}
            searchdict = {}
            get_stats(sys.argv[-1], outdict, searchdict)
            render_stats(outdict, searchdict)
        else:
            output = ""
            print(extract_streams(sys.argv[-1], output, allobjs, generics, recom))

if __name__=="__main__":
    main()
