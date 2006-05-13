"""command line tool for MIME type based transformation

USAGE: transform [OPTIONS] input_file output_file

OPTIONS:
 -h / --help
   display this help message and exit.

 -o / --output <output mime type>
   output MIME type. (conflict with --transform)

 -t / --transform <transform id>
   id of the transform to apply. (conflict with --output)

EXAMPLE:
 $ transform -o text/html dev_manual.rst dev_manual.html
"""

from TransformTool import TransformTool
from getopt import getopt
from os.path import dirname, join

def run(*args):
    s_opt = 'ho:t:'
    l_opt = ['help', 'output=', 'transform=']
    options, args = getopt(args, s_opt, l_opt)
    output = None
    transform = None
    for name, value in options:
        if name in ('-h', '--help'):
            print __doc__
            return
        if name in ('-o', '--format'):
            output = value
        elif name in ('-t', '--transform'):
            tranform = value
    if len(args) != 2:
        print __doc__
        return 0
    if transform and output:
        print 'You can\'t use -o/--output and -t/--transform options together'
        return 1
    if not transform and not output:
        print 'You must use one of the -o/--output or -t/--transform options'
        return 1
    filename = args[0]
    in_data = open(filename).read()
    engine = TransformTool()
    try:
        import transform_customize
        transform_customize.initialize(engine)
    except ImportError:
        import transforms
        transforms.initialize(engine)
    if transform:
        datastream = engine.convert(transform, in_data, filename=filename)
    else:
        datastream = engine.convertTo(output, in_data, filename=filename)
    if datastream is None:
        print 'Unable to transform', filename
        return 2
    destfilename = args[1]
    print 'Writing main output to', destfilename
    output = open(destfilename, 'w')
    output.write(datastream.getData())
    output.close()
    dest_dir = dirname(destfilename)
    for id, data in datastream.getSubObjects():
        dest_file = join(dest_dir, id)
        print 'Writing sub-object output to', dest_file
        output = open(dest_file, 'w')
        output.write(data)
        output.close()

if __name__ == '__main__':
    import sys
    run(*sys.argv[1:])
