from pymongo import MongoClient
from bson.objectid import ObjectId


class AnimalShelter(object):
    """
    Database access layer for animal shelter operations.
    Provides CRUD (Create, Read, Update, Delete) operations for MongoDB animal collection.
    """

    def __init__(self):
        """
        Initialize MongoDB connection using configuration settings.
        Establishes connection to the animal shelter database and collection.
        """
        from config import MONGO_CONFIG

        # Extract database connection parameters from configuration
        USER = MONGO_CONFIG['USER']
        PASS = MONGO_CONFIG['PASS']
        HOST = MONGO_CONFIG['HOST']
        PORT = MONGO_CONFIG['PORT']
        DB = MONGO_CONFIG['DB']
        COL = MONGO_CONFIG['COL']

        # Establish MongoDB connection
        try:
            self.client = MongoClient(f'mongodb://{USER}:{PASS}@{HOST}:{PORT}')
            self.database = self.client[DB]
            self.collection = self.database[COL]
            print("✅ Connected to MongoDB successfully!")
        except Exception as e:
            print(f"❌ Connection error: {e}")

    def create(self, data):
        """
        Insert a new animal record into the database.

        Args:
            data (dict): Animal record data to insert

        Returns:
            bool: True if insertion successful, False otherwise
        """
        if data and isinstance(data, dict):
            try:
                result = self.collection.insert_one(data)
                print(f"✅ Success! New document inserted with ID: {result.inserted_id}")
                return result.acknowledged
            except Exception as e:
                print(f"❌ Error inserting document: {e}")
                return False
        else:
            print("❌ Error: Invalid data format. Expected a dictionary but got", type(data))
            return False

    def read(self, query):
        """
        Query the database for animal records matching specified criteria.

        Args:
            query (dict): MongoDB query parameters

        Returns:
            list: List of matching animal records, empty list if none found or error occurs
        """
        if query and isinstance(query, dict):
            try:
                results = self.collection.find(query)
                return list(results)
            except Exception as e:
                print(f"❌ Error reading from database: {e}")
                return []
        else:
            print("❌ Error: Invalid query format. Expected a dictionary but got", type(query))
            return []

    def read_all(self):
        """
        Retrieve all animal records from the database.
        Performs data cleaning to handle null values that could cause display issues.

        Returns:
            list: All animal records with null values replaced by empty strings
        """
        try:
            results = list(self.collection.find({}))

            # Clean null values to prevent dashboard display issues
            for doc in results:
                for key, value in doc.items():
                    if value is None:
                        doc[key] = ""

            return results
        except Exception as e:
            print(f"❌ Error reading all records: {e}")
            return []

    def update(self, query, new_values, multiple=False):
        """
        Update existing animal records in the database.

        Args:
            query (dict): MongoDB query to identify records to update
            new_values (dict): New field values to apply
            multiple (bool): If True, update all matching records; if False, update only first match

        Returns:
            int: Number of documents successfully modified
        """
        if isinstance(query, dict) and isinstance(new_values, dict):
            try:
                update_action = {"$set": new_values}
                if multiple:
                    result = self.collection.update_many(query, update_action)
                    print(f"✅ Success! {result.modified_count} document(s) updated.")
                else:
                    result = self.collection.update_one(query, update_action)
                    print(f"✅ Success! {result.modified_count} document updated.")
                return result.modified_count
            except Exception as e:
                print(f"❌ Error updating document: {e}")
                return 0
        else:
            print("❌ Error: Invalid query or update format. Both must be dictionaries.")
            return 0

    def delete(self, query, multiple=False):
        """
        Remove animal records from the database.

        Args:
            query (dict): MongoDB query to identify records to delete
            multiple (bool): If True, delete all matching records; if False, delete only first match

        Returns:
            int: Number of documents successfully deleted
        """
        if isinstance(query, dict):
            try:
                if multiple:
                    result = self.collection.delete_many(query)
                    print(f"✅ Success! {result.deleted_count} document(s) deleted.")
                else:
                    result = self.collection.delete_one(query)
                    print(f"✅ Success! {result.deleted_count} document deleted.")
                return result.deleted_count
            except Exception as e:
                print(f"❌ Error deleting document: {e}")
                return 0
        else:
            print("❌ Error: Invalid query format. Expected a dictionary.")
            return 0