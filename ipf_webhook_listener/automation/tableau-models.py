from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Snapshot(Base):
    __tablename__ = "snapshot"
    snapshot_id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String)
    start = Column(DateTime)
    end = Column(DateTime)
    version = Column(String)
    total_devices = Column(Integer)
    licensed_devices = Column(Integer)
    status = Column(String)


class Errors(Base):
    __tablename__ = "errors"
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshot.snapshot_id"))
    parsing_failures = Column(Integer)
    result_mapping_failures = Column(Integer)
    command_auth_failures = Column(Integer)
    invalid_command = Column(Integer)
    device_issue = Column(Integer)
    auth_error = Column(Integer)


class Site(Base):
    __tablename__ = "sites"
    site_key = Column(Integer, primary_key=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshot.snapshot_id"))
    site_name = Column(String)
    site_id = Column(Integer)
    site_uid = Column(String)
    devices = Column(Integer)
    networks = Column(Integer)
    routers = Column(Integer)
    switches = Column(Integer)
    users = Column(Integer)
    vlans = Column(Integer)
    stp_domains = Column(Integer)
    routing_domains = Column(Integer)


class Device(Base):
    __tablename__ = "sites"
    device_id = Column(String, primary_key=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshot.snapshot_id"))
    site_key = Column(Integer, ForeignKey("sites.site_key"))
    device_type = Column(String)
    family = Column(String)
    hostname = Column(String)
    task_key = Column(String)
    login_ip = Column(String)
    login_type = Column(String)
    mac = Column(String)
    total_memory = Column(Integer)
    used_memory = Column(Integer)
    memory_utilization = Column(Float)
    model = Column(String)
    platform = Column(String)
    processor = Column(String)
    serial_number = Column(String)
    hw_serial_number = Column(String)
    uptime = Column(Integer)
    vendor = Column(String)
    version = Column(String)
    reload = Column(String)
    config_reg = Column(String)
