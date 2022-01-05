from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Float, BigInteger
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

FK = "snapshot.snapshot_id"

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
    error_id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey(FK))
    error_type = Column(String)
    error_count = Column(Integer)


class Site(Base):
    __tablename__ = "sites"
    site_id = Column(BigInteger, unique=True)
    site_key = Column(BigInteger, primary_key=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey(FK), primary_key=True)
    site_name = Column(String)
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
    __tablename__ = "devices"
    device_id = Column(BigInteger, primary_key=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey(FK))
    site_key = Column(Integer)
    device_type = Column(String)
    family = Column(String)
    hostname = Column(String)
    task_key = Column(String)
    login_ip = Column(String)
    login_type = Column(String)
    mac = Column(String)
    total_memory = Column(BigInteger)
    used_memory = Column(BigInteger)
    memory_utilization = Column(Float)
    model = Column(String)
    platform = Column(String)
    processor = Column(String)
    serial_number = Column(String)
    hw_serial_number = Column(String)
    uptime = Column(BigInteger)
    vendor = Column(String)
    version = Column(String)
    reload = Column(String)
    config_reg = Column(String)
    __table_args__ = (ForeignKeyConstraint((site_key, snapshot_id), [Site.site_key, Site.snapshot_id]), {})
