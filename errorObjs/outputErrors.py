'''
Created on Mar 21, 2017

@author: marko
'''
import codecs, logging, os
import xml.etree.cElementTree as ET
from uuid import uuid4

import common.common as common
import common.control as control

# Get the logger
log_basic = logging.getLogger('dsc.basic')
log_error = logging.getLogger('dsc.error')

class OutputErrors (object):
    def __init__ (self, messages):
        self.messages = messages

        # For ids
        self.prefix_root = 'em'
        self.id = 1

    def getCategories (self, category_names=[]):
        # Returns lists of (sorted) categories to be output
        # Optionally uses category_names to restrict list
        categories=[]
        # if file doesn't have a title , default it to empty string
        for category in sorted(self.messages, key=lambda x: x.title or ""):
            # If no restrictions, keep category
            if not category_names:
                categories.append(category)
            # If any restriction, must match category
            elif category.category in category_names:
                categories.append(category)
        return categories


    def outputUnidoc (self, file_name, title, categories):
        file_name = common.stringToFileNameChars(file_name).replace('-','').replace('_','')

        # Create the unidoc output dir
        control.xml_dir = ''.join([control.output_dir, os.sep, control.xml_dir_name])
        common.createDirectory(control.xml_dir)

        # Create the output file
        output_file_name = ''.join([control.xml_dir, os.sep, file_name, '.xml'])
        # Create the root element
        chapter_root = ET.Element('chapter')
        # Chapter root id is the same as the file_name. This
        # provides a simple means to link to specific chapters.
        # chapter_root.attrib['ID'] = self.createId(file_name)
        chapter_root.attrib['ID'] = ''.join([self.prefix_root, file_name])
        # Add the chapter-title
        chap_title = ET.SubElement(chapter_root, 'title')
        chap_title.text = title

        # Add the description-block for the content
        d_block = ET.SubElement(chapter_root, 'description-topic')
        d_block.attrib['topic-type'] = 'structure'
        d_block.attrib['ID'] = self.createId(file_name)
        d_block_title = ET.SubElement(d_block, 'title')
        d_block_title.text = title
        # Create the content block
        block = ET.SubElement(d_block, 'block')
        label = ET.SubElement(block, 'label')
        label.text = title

        # Add a table for each of the categories
        for category in categories:
            if category.is_valid:
                self.addCategoryTable(category, block)
            else:
                log_error.error(''.join(['Skipping output: ',
                                         category.file_name,
                                         ' is invalid']))

        self.writeToFile(output_file_name, control.xml_header, chapter_root)

    def outputDita(self,  title, grouped_files,release):
        # Create the Dita XML output dir
        dita_map_dir = ''.join([control.output_dir, os.sep, control.dita_dir_name])
        control.dita_dir_name = ''.join(
            [control.output_dir, os.sep, control.dita_dir_name, os.sep, control.error_messages_dir_name])
        common.createDirectory(control.dita_dir_name)
        # Create map for mapdita file
        map = ET.Element('map')
        # add map meta data
        self.createMapMetaData(map,title,release);
        # create ID using uuid
        map.attrib['id'] = "id{}".format(uuid4)
        # loop each file
        # create topic ref for each file in the ditamap
        # add all messages into tables to dita files
        for main_ref in grouped_files:
            clean_main_ref = self.removeSpecialChracters(main_ref)
            # get list of related categories
            grouped_categories = grouped_files[main_ref]
            # create output filename for the dita file containing all errors
            chapter = ''.join([control.dita_dir_name, os.sep, clean_main_ref, '.dita'])
            # create main category ref
            chapter_ref = ET.SubElement(map, "topicref")
            chapter_ref.attrib["href"] = "ncc_error_messages/{}.dita".format(clean_main_ref)
            chapter_ref.attrib["type"] = "concept"
            for category in grouped_categories:
                id = uuid4();
                # add topic ref without special characters for the current category ,type and href
                topic_ref = ET.SubElement(chapter_ref, "topicref")
                clean_title = self.removeSpecialChracters(category.title)
                topic_ref.attrib["href"] = "ncc_error_messages/{}_{}_{}.dita".format(clean_main_ref,clean_title,id)
                topic_ref.attrib["type"] = "concept"
                # Create the root element
                concept = ET.Element('concept')
                # add id for root and xref elements ( must be the same id )
                concept.attrib['id'] = "id{}".format(id)
                # Add the title for the dita file ( same  title of the error file )
                title = ET.SubElement(concept, 'title')
                title.text = category.title.title()
                # add body
                conbody = ET.SubElement(concept, "conbody")
                # add xref for referencing the table and description
                p = ET.SubElement(conbody, "p")
                p.text = "This table {}".format(category.description)
                # create table
                self.addCategoryTable(category, conbody, False)
                # create output filename without special characters  for the dita file containing all errors
                topic_ref_file_name = ''.join([control.dita_dir_name, os.sep, "{}_{}_{}".format(clean_main_ref,clean_title,id), '.dita'])
                self.writeToFile(topic_ref_file_name, control.dita_header, concept)

            # create content of chapter itself
            chapter_concept = ET.Element('concept')
            id = uuid4();
            chapter_concept.attrib['id'] = "id{}".format(id)
            # Add the title for the dita file ( same  title of the error file )
            title = ET.SubElement(chapter_concept, 'title')
            title.text = main_ref.title()
            # add body
            chapter_conbody = ET.SubElement(chapter_concept, "conbody")
            # add table description
            p = ET.SubElement(chapter_conbody, "p")
            p.text = "This chapter describes the {}  you may receive when you use the NCC.".format(main_ref)
            self.writeToFile(chapter, control.dita_header, chapter_concept)

        ditamap_file_name = ''.join([dita_map_dir, os.sep, "ncc_error_messages", '.ditamap'])
        self.writeToFile(ditamap_file_name, control.dita_map_header, map)

    def addCategoryTable(self, category, parent, xml_type=True):
        # Create the table object and header
        # xml_type refer to type of file being generated , default is xml .
        # xml has different properties than dita so it's handled using xml_type flag
        table = ET.SubElement(parent, 'table')
        if not xml_type:
            table.attrib["frame"] = "all"
            table.attrib["pgwide"] = "1"
            table.attrib["colsep"] = "1"
            table.attrib["rowsep"] = "1"

        table_title = ET.SubElement(table, 'title')
        table_title.text = category.title
        tgroup = self.createTgroup(table, xml_type)

        # Add the tbody
        tbody = ET.SubElement(tgroup, 'tbody')

        # Add the rows
        for message in sorted(category.messages):
            error_id, title, description, http_code = message
            row = ET.SubElement(tbody, 'row')
            cell = ET.SubElement(row, 'entry')
            if xml_type:
                para = ET.SubElement(cell, 'para')
                para.text = error_id
            else:
                cell.text = error_id

            cell = ET.SubElement(row, 'entry')
            for p in title:
                 if xml_type:
                    para = ET.SubElement(cell, 'para')
                    para.text = p
                 else:
                    cell.text = p

            cell = ET.SubElement (row, 'entry')
            if xml_type:
                  para = ET.SubElement(cell, 'para')
                  para.text = http_code.strip()
            else:
                    cell.text = http_code.strip()

            cell = ET.SubElement (row, 'entry')
            for p in description:
                if xml_type:
                  para = ET.SubElement(cell, 'para')
                  para.text = p.strip()
                else:
                    cell.text = p.strip()


    def createTgroup (self, table,xml_type = True):
        tgroup = ET.SubElement(table, 'tgroup')
        tgroup.attrib['cols'] = '4'
        # Add the colspec elements
        colspec = ET.SubElement(tgroup, 'colspec')
        colspec.attrib['colname'] = 'col1'
        colspec.attrib['colwidth'] = '1.75*'
        colspec = ET.SubElement(tgroup, 'colspec')
        colspec.attrib['colname'] = 'col2'
        colspec.attrib['colwidth'] = '2.25*'
        colspec = ET.SubElement(tgroup, 'colspec')
        colspec.attrib['colname'] = 'col3'
        colspec.attrib['colwidth'] = '3.25*'
        colspec = ET.SubElement(tgroup, 'colspec')
        colspec.attrib['colname'] = 'col4'
        colspec.attrib['colwidth'] = '3.25*'
        # Add the header elements
        self.addTHead(tgroup, ['Number', 'Message','HTTP Error Code' ,'Description'],xml_type)
        return tgroup


    def addTHead (self, tgroup, header_text,xml_type = True):
        # Create the thead
        thead = ET.SubElement(tgroup, 'thead')
        # Create the row
        row = ET.SubElement(thead, 'row')
        # Add each entry and para elements
        for header in header_text:
            entry = ET.SubElement(row, 'entry')
            if xml_type :
                 para = ET.SubElement(entry, 'para')
                 para.text = header
            else :
                entry.text = header

    def createElemWithTitle (self, elem_name, title_name, title_text, prefix, add_id=False):
        elem = ET.Element (elem_name)
        if add_id == True:
            elem.attrib['ID'] = self.createId(prefix)
        title = ET.SubElement(elem, title_name)
        title.text = title_text
        return elem



    def createId (self, prefix=None):
        self.id+=1
        if prefix is None:
            new_id = self.prefix_root + str(self.id)
        else:
            new_id = prefix + str(self.id)
        # Check the first character - it cannot be a digit
        if new_id[0].isdigit():
            return 'a' + new_id
        return new_id

    def addCRsToXml (self, stream, breakCount=70):
        '''
        After every breakCount th character, insert a carriage return before the following "<",
        unless the next char is "/"
        '''
        #return stream
        count = 0
        new_stream=[]
        prev_char=''
        for c in stream:
            count+=1
            # convert ASCII code to character required by python 3.10
            c = chr(c)
            if count > breakCount and prev_char == '<' and c != '/':
                new_stream.append('\n')
                count = 0
            new_stream.append(prev_char)
            prev_char = c

        new_stream.append(prev_char)
        return ''.join(new_stream)

    def groupFiles(self, categories, source_dir):
        grouped_files = {}
        for category in categories:
            # path proccessing
            path = category.file_name.split(source_dir)[1]
            path = path.split(os.sep)
            # always ignore system seperator at the beginning
            path = path[1:]
            # first dir is the root of properties files
            key = path[0]
            if category.is_valid:
                if key not in grouped_files:
                    grouped_files[key] = []
                grouped_files[key].append(category)
            else:
                log_error.error(''.join(['Skipping output: ',
                                         category.file_name,
                                         ' is invalid']))
        return grouped_files

    def writeToFile(self, file_name, header, content):
        # open file
        write_file = codecs.open(file_name, 'w', 'utf-8')
        # write content of the file
        write_file.write(header)
        write_file.write(self.addCRsToXml(ET.tostring(content)))
        # Close the files
        write_file.close()

    def removeSpecialChracters(self, dirty_string):
        return ''.join(e for e in dirty_string if e.isalnum())

    def createMapMetaData(self,map,title,release):
        # add title for the ditamap file
        title_element = ET.SubElement(map, 'title')
        title_element.text = title
        # add topic ref for this document
        topic_meta = ET.SubElement(map,"topicmeta")
        other_meta = ET.SubElement(topic_meta,'othermeta')
        other_meta.attrib['name'] = 'issue'
        other_meta.attrib['content'] = '1'
        other_meta = ET.SubElement(topic_meta, 'othermeta')
        other_meta.attrib['name'] = 'review-status'
        other_meta.attrib['content'] = 'Approved'
        other_meta = ET.SubElement(topic_meta, 'othermeta')
        other_meta.attrib['name'] = 'maptype'
        other_meta.attrib['content'] = 'document'
        other_meta = ET.SubElement(topic_meta, 'othermeta')
        other_meta.attrib['name'] = 'docnumber'
        other_meta.attrib['content'] = "P556766-DN1000055003-{}".format(release)
