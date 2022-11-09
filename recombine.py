#!/usr/bin/env python3
#Ryan Kantor
#Fall 2022

import sys

def recombine(infile, outfile):

    refdict = ["{/None}"]
    xrefs = []
    
    output = '%PDF-1.1\n\n'
    
    i = 1
    
    for cobj in infile:
        
        tokens = cobj.split()
        
        if len(tokens) > 1:
            '''
            print(cobj)
            print(tokens)
            '''      
            refdict.append(tokens[0])
            xrefs.append(len(output))

            nextline = ' '.join(tokens[1:])
            output += str(i)+" 0 obj "
            i += 1
            output += nextline
            output += ' endobj\n\n'

    for i in range(len(refdict)):
        print(str(i) + ' = ' + refdict[i])

    done = False
    while not done:
        done = True
        for j in range(len(refdict)):
            if refdict[j] in output:
                done = False
                output = output.replace(refdict[j], str(j)+" 0 R", 1)

    
    xrefpos = len(output)
    output += 'xref\n0 '+str(len(refdict))+'\n0000000000 65535 f\n'
    for i in range(len(xrefs)):
        output += str(output.find((str(i+1)+' 0 obj'))).rjust(10, '0') + ' 00000 n\n'
    output += 'trailer\n<<\n /Size 8\n/Root 1 0 R\n>>\nstartxref'
    output += str(xrefpos)
    output += '%%EOF'
    print(output)
    outfile.write(output)

def main():
    f = open(sys.argv[1], 'r', encoding='utf-16')
    o = open(sys.argv[2], 'w')
    recombine(f, o)

if __name__=="__main__":
    main()
