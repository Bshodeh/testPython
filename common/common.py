'''
Created on Mar 19, 2017

@author: marko
'''
import errno, logging, os, shutil, string

def createDirectory(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def getFileList (source_dir, recursive=True, file_ext=['.xml'], skip_ext=[], ignore_files_list=[]):

    '''
    Gets a list of files in the specified directory.
    :param source_dir: root directory to begin searching from
    :param recursive: if True, performs recursive search
    :param file_ext: list of file extensions to match, if empty, matches all
    :param skip_ext: list of file extensions to skip
    :param ignore_files_list: list of specific file names
    :returns: a list of filenames (including full path)
    '''
    file_list = []
    # Create a lower case list of the match terms
    [x.lower() for x in file_ext]
    # Create a lower case list of the exclude terms
    [x.lower() for x in skip_ext]
    for path, subdirs, files in os.walk(source_dir):
        check_it = True;
        if recursive == False and source_dir != path:
            check_it = False
        
        if check_it == True:
            for name in files:
                # Test if this file should be explicitly excluded
                if (name not in ignore_files_list):
                    the_ext = str.lower(os.path.splitext(name)[1])
                    # Should this file extension be skipped
                    if the_ext not in skip_ext:
                        # Check if this file extension should be retained
                        if the_ext in file_ext:
                            file_list.append(os.path.join(path, name))
                        # If there are no restrictions on file extension matching, record it
                        if file_ext == []:
                            file_list.append(os.path.join(path, name))
                            
            
    return file_list

def setupLogging (logger_name, log_filename, stream=False, level=logging.INFO, mode='w'):
    '''
    Basic function to create a logger. Can be used to create
    more than one logger.
    Default is to disable stream handler.
    '''
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(levelname)s : %(message)s')
    logger.setLevel(level)
    fileHandler = logging.FileHandler(log_filename, mode=mode)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    if stream:
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)



def stringToFileNameChars (s):
    # Valid chars
    valid_chars = "-_. %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ','_')
    return filename















