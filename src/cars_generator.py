from collections import namedtuple, defaultdict
from datetime import date

#  Summons Number: int
#  Plate ID: str
#  Registration State: str
#  Plate Type: str
#  Issue Date: date
#  Violation Code: int
#  Vehicle Body Type: str
#  Vehicle Make: str
#  Violation Description str


class FileReader:

    def __init__(self, filename, column_to_track, *, date_column: int = None):
        if not(isinstance(column_to_track, str)):
            raise TypeError('column_to_track must be of type str')
        self.filename = filename
        self.column_to_track = column_to_track
        self.column_counter = defaultdict(int)
        self.date_column = int(date_column)
        self.data_key = None
        self.headers = None
        self.track_column_index_number = None
        self.column_track_name = None
        self.column_counter_highest_frequency_key = None
        self.highest_frequency_item = None

    def __iter__(self):
        return FileReader.clean_row(self)

    def infer_data_type(self):
        for value in self.data_key:
            if value is None:
                self.data_key[self.data_key.index(value)] = None
            elif all(c.isdigit() for c in value):
                self.data_key[self.data_key.index(value)] = int(value)

            elif value.count('.') == 1:
                try:
                    self.data_key[self.data_key.index(value)] = float(value)
                except ValueError:
                    self.data_key[self.data_key.index(value)] = str(value)

            else:
                self.data_key[self.data_key.index(value)] = str(value)

    def clean_row(self):
        with open(self.filename) as file:
            next(file)
            data_string = next(file).strip('\n')
            self.data_key = data_string.split(',')
            self.infer_data_type()
        with open(self.filename) as file:

            # class io.TextTOWrapper
            # strip out the row ending '\n'
            headers = next(file).strip('\n')

            # clean out white space in header labels
            headers_clean: str = headers.replace(" ", "_")
            # spiting the headers string into a list of strings

            self.headers = headers_clean.split(',')
            self.track_column_index_number = self.headers.index(str(self.column_to_track))
            self.column_track_name = self.headers[self.track_column_index_number]
            # namedtuple unpacking headers string separating elements by comma
            Row = namedtuple('Row', headers_clean)
            yield self.headers

            for row in file:
                # extract data as a list of strings from second row down
                data: list = row.strip('\n').split(',')
                final_data_list = ([FileReader.cast(data_type, value) for
                                    data_type, value in zip(self.data_key, data)])
                print('79:', 'final_data_list ''='' ', final_data_list)

                # parse date into data object
                if self.date_column is not None:
                    # noinspection PyTypeChecker
                    final_data_list[self.date_column] = FileReader.date_modifier(final_data_list[self.date_column])
                finaldatarow = Row(*final_data_list)

                # store tracking column in frequency counter dictionary
                if getattr(finaldatarow, self.column_track_name) in self.column_counter.keys():
                    current_vehicle_count = self.column_counter.get(getattr(finaldatarow, self.column_track_name))
                    current_vehicle_count += 1
                    self.column_counter[getattr(finaldatarow, self.column_track_name)] = current_vehicle_count
                else:
                    self.column_counter[getattr(finaldatarow, self.column_track_name)] = 1

                # return item name
                self.column_counter_highest_frequency_key = sorted(self.column_counter, key=lambda k:
                                                                   self.column_counter[k], reverse=True)
                
                # return tuple(item, frequency)
                self.highest_frequency_item = (self.column_counter_highest_frequency_key[0],
                                               self.column_counter.get(self.column_counter_highest_frequency_key[0]))
                yield finaldatarow
        yield ('File Processed!')

    @staticmethod
    def cast(single_data_value, data_value):
        if single_data_value is None:
            return None
        elif single_data_value == 'float':
            return float(data_value)
        elif single_data_value == 'int':
            return int(data_value)
        else:
            if len(str(data_value)) is 0:
                return None
            return str(data_value)

    @staticmethod
    def date_modifier(date_string: str) -> date:
        date_list = date_string.split('/')
        # noinspection PyUnusedLocal
        date_format_key = ['int' for i in range(3)]
        print('121:', 'date_format_key ''='' ', date_format_key)
        finaldate = [FileReader.cast(date_format_key, date_list)
                     for date_format_key, date_list in zip(date_format_key, date_list)]
        assert all(isinstance(i, int) for i in finaldate)
        date_object = date(finaldate[2], finaldate[0], finaldate[1])
        # assert date_object.year == 2016
        # assert date_object.month == 5
        # assert date_object.day == 10
        return date_object

    def __repr__(self):
        return 'FileReader({0}, {1}, date_column={2})'.format(self.filename, self.column_to_track, self.date_column)


# source_file = 'nyc_parking_tickets_extract.csv'
# file_reader = FileReader(source_file, 'Vehicle_Make', date_column=4)
# filegen = iter(file_reader)
# for line in filegen:
#     print(line)
#
# print('136:', 'file.highest_frequency_item ''='' ', file_reader.highest_frequency_item)
