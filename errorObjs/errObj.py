'''
Created on Mar 19, 2017

@author: marko
'''

import logging, os, re

import common.common as common
import common.control as control


# Get the logger
log_basic = logging.getLogger('dsc.basic')
log_error = logging.getLogger('dsc.error')


def getField (lines, i, l):
    field = []
    # Always read the current line
    field.append(lines[i].rstrip().rstrip('\\'))
    # Iterate through the lines
    # Need to explicitly test for lines that end with the continuation character, '\',
    # but which don't actually continue correctly
    has_valid_continue = True
    # i+1 to handle list index out of range if files ends at the same line of last code
    if i+1<l:
        next_line = lines[i+1]
        if re.match('.*?_DETAIL', next_line):
            has_valid_continue = False

    while lines[i].rstrip().endswith('\\') and has_valid_continue == True:
        i+=1
        field.append(lines[i].rstrip().rstrip('\\'))
    # Merge the lines
    field = ' '.join(field)
    # Remove consecutive spaces
    field = ' '.join(field.split())
    return i+1, field

def cleanField (s, skip_first=False):
    if '\\n' in s:
        description = [x.strip() for x in s.split('\\n')]
        if skip_first:
            return description[1:]
        return description[:]
    return [s]



class ErrorMessages (object):
    def __init__ (self):
        self.messages = []
        self.files_to_process = []
        self.httperrorcodes = {}
        self.counter = 0

    def getPropertiesFiles (self, dir_name):
        # Gets the list of all properties files to be process
        self.files_to_process = common.getFileList(dir_name, file_ext=['.properties'])

    def processErrorCode(self):
        exist = False
        for file_name in self.files_to_process:
            base_file_name = os.path.basename(file_name).replace('.properties', '')
            if base_file_name.lower() == "httpcodes":
                exist = True
                log_basic.info(['Processing HTTP Error Codes: ', file_name])
                with open(file_name) as f:
                    lines = f.readlines()
                self.processHttpErrorCodesLines(lines)
                # remove http error code file from files list
                index = self.files_to_process.index(file_name)
                self.files_to_process = self.files_to_process[:index] + self.files_to_process[index + 1:]
        if not exist:
            log_basic.warning(
                ["Missing File", "httpcodes.properties doesn't exist . this will lead to give all errors empty code "])

    def processPropertiesFiles(self):
        for file_name in self.files_to_process:
            self.processPropertyFile (file_name)

    def processPropertyFile (self, file_name):
        lines=[]
        log_basic.info (['Processing: ', file_name])
        with open (file_name) as f:
            lines = f.readlines()

        # Process the lines for this file
        # Some files contain multiple error objects
        self.processLines (lines, file_name)

    def processLines (self, lines, file_name):
        # Iterate through the lines
        i = 0
        l = len(lines)
        # There may be multiple objects, and some do not have titles,
        # so we need to test if there is a current error_object
        error_data = None
        base_file_name = os.path.basename(file_name).replace('.properties', '')
        # Iterate through the lines
        while (i < l):
            line = lines[i]
            # Category title
            if line.startswith('docTitle'):
                i, title = getField (lines, i, l)
                # Create new category object
                error_data = ErrorCategory(base_file_name)
                self.messages.append(error_data)
                error_data.title = title.split('=', 1)[1]
                error_data.file_name = file_name
                error_data.base_file_name = base_file_name
                log_basic.info (''.join(['Title: ', error_data.title]))

            # Category description
            elif line.startswith('docDescription'):
                i, description = getField(lines, i, l)
                if error_data is None:
                    error_data = ErrorCategory(base_file_name)
                    self.messages.append (error_data)
                    error_data.file_name = file_name
                    error_data.base_file_name = base_file_name
                description = cleanField(description)
                error_data.description = description[0].split('=')[1]
            # Ignore Notes
            elif line.startswith('#### N'):
                i+=1
            # Specific error message
            elif re.match('.*?=', line) and not re.match('.*?_DETAIL', line) \
                    and not re.match('.*?_RETURN_CODE', line):
                if error_data is None:
                    error_data = ErrorCategory(base_file_name)
                    self.messages.append (error_data)
                    error_data.file_name = file_name
                    error_data.base_file_name = base_file_name
                # Read the error code and title
                i, field = getField (lines, i, l)
                error_code = field.split('=', 1)[0]
                title = cleanField(field.split('=', 1)[1])
                # 2019.09.17: Hack fix: check if next line is a valid description
                if i < l and lines[i].startswith(error_code) and re.match('.*?_DETAIL', lines[i]):
                    # Read the error description
                    i, field = getField(lines, i, l)
                    description = cleanField(field.split('=', 1)[1], skip_first=True)
                    # remove error codes from description message
                    description = self.processDescription(description, error_code)
                else:
                    #  add empty description if there is no error details
                    description = [""]
                http_code = self.getHttpErrorCode(error_code, title,base_file_name);
                error_data.messages.append((error_code, title, description, http_code))
            # Error message if any other lines contain '='
            elif '=' in line:
                log_error.warning(''.join(['Non-standard key/value: ', file_name, '\n', line]))
                i += 1
            else:
                i += 1

    def processHttpErrorCodesLines(self, lines):
        # read errors . lines with  equal sign "=" are taken and split
        l = len(lines)
        i = 0
        while i < l:
            line = lines[i];
            if re.match('.*?=.*', line):
                i,line = getField(lines,i,l)
                line=line.split("=")
                self.httperrorcodes[line[0].strip()] = line[1].strip()
            else:
                i+=1


    def processDescription(self, description, error_code):
        description = description[0]
        if not description.startswith("Error Reference Number:"):
            return [description]
        # Remove Error Reference Number form error detail ( description )
        new_description = description.split("Error Reference Number:")[1].strip()
        error_code_index = description.find(error_code)
        if error_code_index > -1:
            new_description = new_description[len(error_code) + 1:].strip()
        return [new_description]

    def getHttpErrorCode(self, error_code, title,filename):
        # get error code , some error lines title is same as key value of error code
        http_code = self.httperrorcodes.get(error_code,  self.httperrorcodes.get(title[0],""))
        return http_code

    def validateErrorData (self):
        for category in self.messages:
            category.validateErrorData()



class ErrorCategory (object):
    def __init__(self,base_file_name):
        self.file_name = None
        self.base_file_name = None
        self.category = None
        self.title = base_file_name
        self.description = []
        self.messages=[]
        self.is_valid = True


    def validateErrorData (self):
        if self.title is None:
            print(self.title)
            log_error.error(''.join(['No title: ', self.file_name]))
            self.is_valid = False
        if self.description is None:
            log_error.warning (''.join(['No description: ', self.file_name]))
            self.is_valid = False
        if len (self.messages) == 0:
            log_error.warning (''.join(['No error messages: ', self.file_name]))
            self.is_valid = False






