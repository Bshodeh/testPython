'''
Created on Mar 19, 2017

@author: marko
'''

import argparse
import os
import logging
import sys

import common.common as common
import common.control as control
import errorObjs.errObj as eo
import errorObjs.outputErrors as oe


# Simplified argparse 
def createScriptConfig():
    parser = argparse.ArgumentParser(description='Process DSC error messages')
    parser.add_argument('-V', '--version', help='Display version', version=control.version, action='version')

    # Add group for the required attributes
    req_args = parser.add_argument_group('required arguments')
    # Must provide a file
    req_args.add_argument('-d', '--dir', help='Source directory containing the .properties files', required=True)
    req_args.add_argument('-r', '--release', help='Release Number', required=True)
    opt_args = parser.add_argument_group("Output Type Options")
    opt_args.add_argument('-dita', '--dita', help='For Generating DITA XML', required=False, action='store_true')
    opt_args.add_argument('-unicode', '--uni', help='For generating UNICODE XML', required=False,
                          action='store_true')

    args = vars(parser.parse_args())

    return args


def Main():
    '''
    Control file for working with DSC error.
    All alarm information is contained in an xml file that is generated  by
    the SAM software group.
    '''
    # Get the script root directory
    control.root_dir = os.path.split(sys.argv[0])[0]

    # Reads the args
    args = createScriptConfig()

    # Check the args
    if not os.path.isdir(args['dir']):
        print('Script cancelled. Must specify a directory that contains the DSC .properties files.')
        return

    if not args["uni"] and not args["dita"]:
        print('Script cancelled. Must specify output type UNICODE XML or DITA XML or both.')
        return
    if not args['release'] :
        print('Script cancelled. Must specify Release Number.')
        return
    release = args["release"]
    uni_flag = args["uni"]
    dita_flag = args["dita"]
    control.source_dir = args['dir']

    # Create the debug and output dirs
    control.output_dir = ''.join([control.source_dir, os.sep, control.output_dir_name])
    common.createDirectory(control.output_dir)

    control.debug_dir = ''.join([control.output_dir, os.sep, control.debug_dir_name])
    common.createDirectory(control.debug_dir)

    # Setup logging
    common.setupLogging('dsc.basic', control.debug_dir + '/dsc_basic.txt', stream=True, mode='w')
    log_basic = logging.getLogger('dsc.basic')
    common.setupLogging('dsc.error', control.debug_dir + '/dsc_error.txt', stream=True, mode='w')
    log_invalid = logging.getLogger('dsc.invalid')

    # Create the error messages object
    errors = eo.ErrorMessages()
    # Process the .properties files
    errors.getPropertiesFiles(control.source_dir)
    errors.processErrorCode()
    errors.processPropertiesFiles()
    errors.validateErrorData()

    # Create the output
    output_errors_xml = oe.OutputErrors(errors.messages)
    categories = output_errors_xml.getCategories()
    if uni_flag:
        output_errors_xml.outputUnidoc('errors', 'Error Messages', categories )
    if dita_flag:
        group_files = output_errors_xml.groupFiles(categories, control.source_dir)
        output_errors_xml.outputDita('Error Messages', group_files,release)


if __name__ == '__main__':
    Main()
