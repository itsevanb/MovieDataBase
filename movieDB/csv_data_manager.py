import csv
from data_manager_interface import DataManagerInterface

class CSVDataManager(DataManagerInterface):
    #Initialize the class with the file name
    def __init__(self, filename):
        self.filename = filename

    def _read_data(self):
        #Open the file and read the data
        with open(self.filename, 'r') as file:
            reader = csv.reader(file)
            return list(reader)

    def _write_data(self, data):
        #Open the file and write the data
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def get_all_users(self):
        #Return all users
        data = self._read_data()
        users = set(row[0] for row in data)
        return [{'id': user} for user in users]

    def get_user_movies(self, user_id):
        #Return all movies for a user
        data = self._read_data()
        return [row[1:] for row in data if row[0] == user_id]
