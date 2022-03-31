'''
Created on Mar 19, 2017

@author: marko
'''

version = 'Version: 1.2, 2017.03.30'

# Dirs
source_dir = None
root_dir = None

output_dir = None
output_dir_name = '_output'

debug_dir = None
debug_dir_name = 'debug'
sgml_dir= None
sgml_dir_name = 'sgml'
xml_dir = None
xml_dir_name = 'xml'


xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n\
<!-- Fragment document type declaration subset:\n\
Arbortext, Inc., 1988-2009, v.4002\n\
<!DOCTYPE uni-doc PUBLIC "-//Alcatel-Lucent//DTD UNIDOC-DTD 1.0//EN" "unidoc-dtd.dtd">\n\
<?Pub Inc?>\n\
-->\n'

dita_dir = None
dita_dir_name = 'dita'
error_messages_dir_name=  'ncc_error_messages'

dita_header ="""<?xml version="1.0" encoding="utf-8"?> 
<!DOCTYPE concept PUBLIC "-//OASIS//DTD DITA Concept//EN" "concept.dtd">"""

dita_map_header = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">"""