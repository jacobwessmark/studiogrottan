from sqlalchemy import Column, Integer, String, DateTime, func, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

# to create new migration run: alembic revision --autogenerate -m "msg" and then alembic upgrade head

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    discord_id = Column(String(50))
    mac_addresses = Column(JSON)
    presence = Column(Boolean)
    role = Column(String(50))


    def __repr__(self):
        return f"<User(name={self.name}, discord_id={self.discord_id}, mac_addresses={self.mac_addresses}, presence={self.presence}, role={self.role})>"


class BLEScanData(Base):
    __tablename__ = 'ble_scan_data'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=func.now())
    devices_found = Column(Integer)

    def __repr__(self):
        return f"<BLEScanData(timestamp={self.timestamp}, devices_found={self.devices_found})>"


# create user log table
class UserLog(Base):
    __tablename__ = 'user_log'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=func.now())
    presence = Column(Boolean)

    def __repr__(self):
        return f"<UserLog(user_id={self.user_id}, timestamp={self.timestamp}, presence={self.presence})>"