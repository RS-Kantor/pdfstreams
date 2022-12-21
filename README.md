# pdfstreams.py

Firstly, note the following - I was knocking the rust off of my Python skills when I authored this script. It has a number of idiosyncracies and likely more than a few bugs. Notable among the former is the fact that this tool uses subprocesses to run Didier Stevens' pdf-parser.py where appropriate rather than simply importing from that tool. (It's not completely ridiculous - pdf-parser.py was written for Python 2.7.x, while this script was written for Python 3) Furthermore, the commands passed to subprocess.check_output were written with my environment in mind, which is to say that they invoke the py launcher for Windows. Time permitting, this tool should probably be rewritten to some extent, but it is functional as-is.

pdfstreams.py is a tool for breaking PDFs down into their individual components. A few relevant modes of operation are described below:

 -a - parse out all objects. (only stream objects are extracted by default)
 -g - processes extracted objects further; replaces references between objects with generic type identifiers so that parsed objects can be combined into new configurations easily.
 -r - includes extra data in the output which is necessary for recombination of parsed objects.
 
For the purposes of this project, all of the above switches should generally be used when calling pdfstreams.py. Their inclusion as options rather than default functionality can be attributed to my having written the first few versions of this tool before fully making sense of its purpose.

 -d - process all PDFs in a directory. I have not implemented parallel processing at the time of writing, but I still find this option preferable to manually running this tool over and over again.
 -s - show the stats of all target PDFs as provided by pdf-parser.py. This functionality is only included as a way to run the former against multiple PDFs.
 
Usage:

`./pdfstreams.py [OPTIONS] [TARGET]`

TARGET will be a PDF file unless -d is specified, in which case it should be the path to a directory containing PDF files.

# recombine.py

Usage:

`./recombine.py [INPUT] [OUTPUT]`

INPUT is a file containing a series of parsed PDF objects in the format offered by running pdfstreams.py;

`./pdfstreams.py -a -g -r [TARGET]`

Objects included in INPUT can be from one or multiple PDFs. OUTPUT is a file to contain a complete PDF file created by reassembling the objects from INPUT. recombine.py adds an xref table and some boilerplate to make a readable PDF; most importantly, though, it works to resolve references between objects which, as a part of the parsing performed in pdfstreams.py, are replaced with placeholders specifying the type of object each reference is expected to be. As a result, recombine.py should be capable of assembling PDFs out of arbitrary collections of objects, so long as objects of sufficiently diverse types are included.

# commoncrawldltool.py

Firstly, note the following - This tool contains a bug which should be addressed before it is used again. I have not had an opportunity to focus on finding the specific issue, but it should not be terribly hard to troubleshoot. The unintended behavior is this: the downloaded WARC files are named incorrectly. The names given by the script include single quotes and other formatting characters which should not be there. This bug does not affect the core functionality of the tool (AFAIK) but it stands to be a thorn in the side of the user proportional to how many files the tool is used to create. I already experienced this during my 'trial run' on mess.poly.edu, as you may recall.

Usage:

`./commoncrawldltool.py [INPUT]`

INPUT is a gzipped paths file acquired from Common Crawl, generally named like 'cc-index.paths.gz.'

This tool extracts the paths file, then downloads all of the index files (manifests specifying the contents of each web archive offered by common crawl) specified within to a directory called 'indexes.' Upon completion, the tool will parse the index files in order and download all of the archives which the manifest states contain PDF files into a directory called 'warcs.' These files come in the form of .WARC files, which are very large and are likely to contain a great deal of extraneous data in addition to the PDFs.

# pdf-extractor.py

Usage:

`./pdf-extractor.py [TARGET]`

TARGET is a directory containing WARC files, as downloaded using commoncrawldltool.py. The functionality of this tool should probably be incorporated into the aforementioned rather than maintaining this as a separate tool so that large WARCs need not be stored any longer than necessary.

Simply put, this tool parses PDFs out of WARC files which contain them. This process is not a complicated one; PDFs are generally present as plaintext among the other content in each WARC.