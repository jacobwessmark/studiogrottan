from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
from datetime import datetime, timedelta
from models import *

class UserManager:
    def __init__(self, database_uri="postgresql://postgres:secret@localhost:5432/studiodb"):
        self.engine = create_engine(database_uri)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_users(self, user_data):
        """
        Add multiple users to the database.

        :param user_data: List of dictionaries with user data
        """
        for data in user_data:
            user = User(**data)
            self.session.add(user)
        self.session.commit()
        print(f"{len(user_data)} users added successfully.")

    def delete_all_users(self):
        """
        Delete all users from the database.
        """
        try:
            num_deleted = self.session.query(User).delete()
            self.session.commit()
            print(f"{num_deleted} users deleted successfully.")
        except Exception as e:
            self.session.rollback()
            print(f"Error occurred during user deletion: {e}")

    def list_all_users(self):
        """
        Print all users in the database.
        """
        users = self.session.query(User).all()
        for user in users:
            print(user)

    def update_counter_for_all_users(self, new_counter_value):
        """
        Update the 'counter' attribute for all users in the database.

        :param new_counter_value: The new value for the 'counter' attribute.
        """
        try:
            self.session.query(User).update({"counter": new_counter_value})
            self.session.commit()
            print(f"All users' counters updated to {new_counter_value}.")
        except Exception as e:
            self.session.rollback()
            print(f"Error occurred during counter update: {e}")



    def close(self):
        """
        Close the database session.
        """
        self.session.close()


    def calculate_average_ble_devices(self):
        """
        Calculate the average number of discovered BLE devices in the last hour.
        class BLEScanData(Base):
    __tablename__ = 'ble_scan_data'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=func.now())
    devices_found = Column(Integer)

    def __repr__(self):
        return f"<BLEScanData(timestamp={self.timestamp}, devices_found={self.devices_found})>"
        """
        # Get the current time
        current_time = datetime.now()

        # Calculate the time one hour ago
        one_hour_ago = current_time - timedelta(hours=1)

        # Query the database for BLE scan data in the last hour
        scan_data = self.session.query(BLEScanData).filter(BLEScanData.timestamp >= one_hour_ago).all()

        # Calculate the average number of devices found
        total_devices = sum([data.devices_found for data in scan_data])
        average_devices = total_devices / len(scan_data) if scan_data else 0

        print(f"Average BLE devices found in the last hour: {average_devices}")

    def delete_all_data(self):
        """
        Delete all data from all tables in the database.
        """
        try:
            # Iterate over all tables and delete their contents
            for table in reversed(Base.metadata.sorted_tables):
                self.session.execute(table.delete())
            self.session.commit()
            print("All data deleted successfully.")
        except Exception as e:
            self.session.rollback()
            print(f"Error occurred during data deletion: {e}")

# Example usage:
if __name__ == "__main__":


    presence = False

    user_data = [
        {"name": "Jacob", "discord_id": "701481059140894731", "mac_addresses": ["c2:44:1a:25:23:20"], "presence": False, "role": "admin"},
        {"name": "Alan", "discord_id": "932638302543151134", "mac_addresses": ["92:68:56:7d:a1:00", "a4:77:f3:07:1a:dd"], "presence": False, "role": "member"},
        {"name": "David", "discord_id": "292696985213992961", "mac_addresses": ["N/A"], "presence": False, "role": "member"},
        {"name": "Juan", "discord_id": "N/A", "mac_addresses": ["72:09:a8:9a:7b:94"], "presence": False, "role": "member"},
        {"name": "Oscar Person", "discord_id": "N/A", "mac_addresses": ["be:71:fd:34:5e:c5"], "presence": False, "role": "member"},
        {"name": "Agnese", "discord_id": "N/A", "mac_addresses": ["04:d6:aa:b3:55:60"], "presence": False, "role": "member"},
        {"name": "Guile", "discord_id": "N/A", "mac_addresses": ["6e:f0:56:e3:f5:97"], "presence": False, "role": "member"},
        # {"name": "Router", "discord_id": "N/A", "mac_addresses": ["2a:d8:48:70:ad:05"], "presence": False, "role": "member"},
    ]
    # , "d4:3b:04:d8:06:53"

    # {'28:cd:c1:0d:76:51', 'd4:3b:04:d8:06:53', '3e:9e:90:12:35:d6', '04:d6:aa:b3:55:60', 'd8:3a:dd:3f:a8:3d', , 'c2:44:1a:25:23:20', 'd8:3a:dd:36:a1:e0', '6e:f0:56:e3:f5:97'}
    manager = UserManager()
    manager.delete_all_data()

    # To update the counter for all users
    # manager.update_counter_for_all_users(new_counter_value=10)

    # add users
    manager.add_users(user_data) 

    # delete all users
    # manager.delete_all_users()

    # To list all users to verify the update
    manager.list_all_users()
   #  manager.calculate_average_ble_devices()

    # Don't forget to close the session
    manager.close()
    