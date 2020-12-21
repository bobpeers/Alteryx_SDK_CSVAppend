"""
AyxPlugin (required) has-a IncomingInterface (optional).
Although defining IncomingInterface is optional, the interface methods are needed if an upstream tool exists.
"""

import AlteryxPythonSDK as Sdk
import xml.etree.ElementTree as Et
import os
import csv


class AyxPlugin:
    """
    Implements the plugin interface methods, to be utilized by the Alteryx engine to communicate with a plugin.
    Prefixed with "pi", the Alteryx engine will expect the below five interface methods to be defined.
    """

    def __init__(self, n_tool_id: int, alteryx_engine: object, output_anchor_mgr: object):
        """
        Constructor is called whenever the Alteryx engine wants to instantiate an instance of this plugin.
        :param n_tool_id: The assigned unique identification for a tool instance.
        :param alteryx_engine: Provides an interface into the Alteryx engine.
        :param output_anchor_mgr: A helper that wraps the outgoing connections for a plugin.
        """

        # Default properties
        self.n_tool_id = n_tool_id
        self.alteryx_engine = alteryx_engine

        # Custom properties
        self.str_file_path: str = None
        self.delimiter: str = None
        self.quote: str = None
        self.codepage: str = None
        self.newline: str = None
        self.is_initialized: bool = True
        self.single_input = None

        self.csv_quote: int = 0

    def pi_init(self, str_xml: str):
        """
        Handles input data verification and extracting the user settings for later use.
        Called when the Alteryx engine is ready to provide the tool configuration from the GUI.
        :param str_xml: The raw XML from the GUI.
        """

        # Getting the user-entered file path string from the GUI, to use as output path.
        root = Et.fromstring(str_xml)
        self.str_file_path = root.find('fileOutputPath').text if root.find('fileOutputPath').text else None
        self.delimiter = root.find('delimiter').text if root.find('delimiter').text else None
        self.quote = root.find('quote').text if root.find('quote').text else None
        self.codepage = root.find('codepage').text if root.find('codepage').text else None
        self.newline = root.find('newline').text if root.find('newline').text else None

        # If there is no error message string returned, set flag to True if validation passes
        error_msg = self.msg_str(self.str_file_path)
        if error_msg != '':
            self.display_error_msg(error_msg)

        # check delimiter
        if not self.delimiter:
            self.display_error_msg('Enter a delimiter')
        elif len(self.delimiter)>1:
            self.display_error_msg('Delimiter must be a single character (for example ; or | or , or : )')

        # check quoting
        if not self.quote:
            self.display_error_msg('Enter a quoting type')

        # check quoting
        if not self.codepage:
            self.display_error_msg('Enter a Code Page')

        # check quoting
        if not self.newline:
            self.display_error_msg('Enter a Line Ending Style')

        if self.quote == 'auto':
            self.csv_quote = csv.QUOTE_MINIMAL
        elif self.quote == 'text':
            self.csv_quote = csv.QUOTE_NONNUMERIC
        elif self.quote == 'none':
            self.csv_quote = csv.QUOTE_NONE
        else:
            self.csv_quote = csv.QUOTE_ALL
        
        if self.newline == 'windows':
            self.newline = '\r\n'
        elif self.newline == 'unix':
            self.newline = '\n'
        else:
            self.newline = '\r'

        if not os.access(self.str_file_path, os.W_OK):
            self.display_error_msg(f'The output file {self.str_file_path} does not exist')
        
    def pi_add_incoming_connection(self, str_type: str, str_name: str) -> object:
        """
        The IncomingInterface objects are instantiated here, one object per incoming connection.
        Called when the Alteryx engine is attempting to add an incoming data connection.
        :param str_type: The name of the input connection anchor, defined in the Config.xml file.
        :param str_name: The name of the wire, defined by the workflow author.
        :return: The IncomingInterface object.
        """

        self.single_input = IncomingInterface(self)
        return self.single_input

    def pi_add_outgoing_connection(self, str_name: str) -> bool:
        """
        Called when the Alteryx engine is attempting to add an outgoing data connection.
        :param str_name: The name of the output connection anchor, defined in the Config.xml file.
        :return: True signifies that the connection is accepted.
        """

        return True

    def pi_push_all_records(self, n_record_limit: int) -> bool:
        """
        Called when a tool has no incoming data connection.
        :param n_record_limit: Set it to <0 for no limit, 0 for no records, and >0 to specify the number of records.
        :return: True for success, False for failure.
        """

        self.display_error_msg('Missing Incoming Connection')
        return False

    def pi_close(self, b_has_errors: bool):
        """
        Called after all records have been processed.
        :param b_has_errors: Set to true to not do the final processing.
        """

        pass

    def display_error_msg(self, msg_string: str):
        self.alteryx_engine.output_message(self.n_tool_id, Sdk.EngineMessageType.error, msg_string)
        self.is_initialized = False

    def display_info(self, msg_string: str):
        self.alteryx_engine.output_message(self.n_tool_id, Sdk.EngineMessageType.info, msg_string)

    def display_file(self, msg_string: str):
        self.alteryx_engine.output_message(self.n_tool_id, Sdk.Status.file_output, msg_string)

    #@staticmethod
    def write_lists_to_csv(self, file_path: str, field_lists: list):
        '''
        A non-interface, helper function that handles writing to csv and clearing the list elements.
        :param file_path: The file path and file name input by user.
        :param field_lists: The data for all fields.
        '''
        csv.register_dialect('default', delimiter=self.delimiter, quoting=self.csv_quote, lineterminator=self.newline, escapechar='\\', doublequote=False)

        try:
            with open(file_path, 'a', encoding=self.codepage, newline='') as output_file:
                for fld in field_lists:
                    fld.pop(0)
                csv.writer(output_file, 'default').writerows(zip(*field_lists))
            for sublist in field_lists:
                del sublist[:]
        except Exception as e:
            self.display_error_msg(str(e))
        
        

    @staticmethod
    def msg_str(file_path: str):
        """
        A non-interface, helper function that handles validating the file path input.
        :param file_path: The file path and file name input by user.
        :return: The chosen message string.
        """

        msg_str = ''
        if len(file_path) > 259:
            msg_str = 'Maximum path length is 259'
        elif any((char in set('/;?*"<>|')) for char in file_path):
            msg_str = 'These characters are not allowed in the filename: /;?*"<>|'
        elif len(file_path) == 0:
            msg_str = 'Enter a filename'
        return msg_str


class IncomingInterface:
    """
    This optional class is returned by pi_add_incoming_connection, and it implements the incoming interface methods, to
    be utilized by the Alteryx engine to communicate with a plugin when processing an incoming connection.
    Prefixed with "ii", the Alteryx engine will expect the below four interface methods to be defined.
    """

    def __init__(self, parent: object):
        """
        Constructor for IncomingInterface.
        :param parent: AyxPlugin
        """

        # Default properties
        self.parent = parent

        # Custom members
        self.record_info_in = None
        self.field_lists = []
        self.counter = 0

    def ii_init(self, record_info_in: object) -> bool:
        """
        Handles the storage of the incoming metadata for later use.
        Called to report changes of the incoming connection's record metadata to the Alteryx engine.
        :param record_info_in: A RecordInfo object for the incoming connection's fields.
        :return: True for success, otherwise False.
        """

        self.record_info_in = record_info_in  # For later reference.

        # Storing the field names to use when writing data out.
        for field in range(record_info_in.num_fields):
            self.field_lists.append([record_info_in[field].name])
        return True

    def ii_push_record(self, in_record: object) -> bool:
        """
        Responsible for writing the data to csv in chunks.
        Called when an input record is being sent to the plugin.
        :param in_record: The data for the incoming record.
        :return: False if file path string is invalid, otherwise True.
        """

        self.counter += 1  # To keep track for chunking

        if not self.parent.is_initialized:
            return False

        # Storing the data of in_record
        for field in range(self.record_info_in.num_fields):
            data_type = self.record_info_in[field].type
            if data_type in (Sdk.FieldType.int32, Sdk.FieldType.int32):
                in_value = self.record_info_in[field].get_as_int32(in_record)
            elif data_type == Sdk.FieldType.int64:
                in_value = self.record_info_in[field].get_as_int64(in_record)
            elif data_type in (Sdk.FieldType.fixeddecimal, Sdk.FieldType.float, Sdk.FieldType.double):
                in_value = self.record_info_in[field].get_as_double(in_record)
            elif data_type == Sdk.FieldType.bool:
                in_value = self.record_info_in[field].get_as_bool(in_record)
            else:
                in_value = self.record_info_in[field].get_as_string(in_record)
            
            self.field_lists[field].append(in_value) if in_value is not None else self.field_lists[field].append('')

        # Writing when chunk mark is met, then resetting counter.
        if self.counter == 1000000:
            self.parent.write_lists_to_csv(self.parent.str_file_path, self.field_lists)
            self.counter = 0
        return True

    def ii_update_progress(self, d_percent: float):
        """
         Called by the upstream tool to report what percentage of records have been pushed.
         :param d_percent: Value between 0.0 and 1.0.
        """

        self.parent.alteryx_engine.output_tool_progress(self.parent.n_tool_id, d_percent)  # Inform the Alteryx engine of the tool's progress

    def ii_close(self):
        """
        Handles writing out any residual data out.
        Called when the incoming connection has finished passing all of its records.
        """

        if len(self.parent.str_file_path) > 0 and self.parent.is_initialized:
            # First element for each list will always be the field names.
            if len(self.field_lists[0]) > 1:
                self.parent.write_lists_to_csv(self.parent.str_file_path, self.field_lists)

            # Outputting the link message that the file was written
            self.parent.display_file("{} | Records were appended to {}".format(self.parent.str_file_path, self.parent.str_file_path))