from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, BigInteger, ForeignKeyConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.attributes import InstrumentedAttribute


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
    site_id = Column(BigInteger)
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
    device_id = Column(BigInteger)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey(FK), primary_key=True)
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
    serial_number = Column(String, primary_key=True)
    hw_serial_number = Column(String)
    uptime = Column(BigInteger)
    vendor = Column(String)
    version = Column(String)
    reload = Column(String)
    config_reg = Column(String)
    __table_args__ = (ForeignKeyConstraint((site_key, snapshot_id), [Site.site_key, Site.snapshot_id]), {})


class Part(Base):
    __tablename__ = "parts"
    part_id = Column(BigInteger, primary_key=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey(FK))
    serial_number = Column(String)
    device_serial_number = Column(String)
    description = Column(String)
    hostname = Column(String)
    model = Column(String)
    platform = Column(String)
    name = Column(String)
    vendor = Column(String)
    part_number = Column(String)
    part_version_id = Column(String)
    __table_args__ = (ForeignKeyConstraint((device_serial_number, snapshot_id),
                                           [Device.serial_number, Device.snapshot_id]), {})


class EoL(Base):
    __tablename__ = "eol"
    eol_id = Column(BigInteger, primary_key=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey(FK))
    part_number = Column(String)
    vendor = Column(String)
    replacement = Column(String)
    url = Column(String)
    description = Column(String)
    end_maintenance = Column(DateTime)
    end_sale = Column(DateTime)
    end_support = Column(DateTime)


class Intent(Base):
    __tablename__ = "intent"
    intent_id = Column(BigInteger, primary_key=True)
    name = Column(String)
    api_endpoint = Column(String)
    web_endpoint = Column(String)
    column = Column(String)
    custom = Column(Boolean)
    default_color = Column(Integer)
    default_color_str = Column(String)
    description = Column(String)
    green_description = Column(String)
    blue_description = Column(String)
    amber_description = Column(String)
    red_description = Column(String)
    green_check = Column(String)
    blue_check = Column(String)
    amber_check = Column(String)
    red_check = Column(String)
    green_url = Column(String)
    blue_url = Column(String)
    amber_url = Column(String)
    red_url = Column(String)

    def update(self, session):
        mapped_values = {k: getattr(self, k) for k, v in Intent.__dict__.items() if
                         isinstance(v, InstrumentedAttribute)}
        session.query(Intent).filter(Intent.intent_id == self.intent_id).update(mapped_values)


class Group(Base):
    __tablename__ = "group"
    group_id = Column(BigInteger, primary_key=True)
    name = Column(String)
    custom = Column(Boolean)

    def update(self, session):
        mapped_values = {k: getattr(self, k) for k, v in Group.__dict__.items() if isinstance(v, InstrumentedAttribute)}
        session.query(Group).filter(Group.group_id == self.group_id).update(mapped_values)


class IntentMapping(Base):
    __tablename__ = "intent_mapping"
    intent_mapping_id = Column(BigInteger, primary_key=True, autoincrement=True)
    group_id = Column(BigInteger, ForeignKey("group.group_id"))
    intent_id = Column(BigInteger, ForeignKey("intent.intent_id"))


class IntentResult(Base):
    __tablename__ = "intent_results"
    intent_id = Column(BigInteger, ForeignKey("intent.intent_id"), primary_key=True)
    snapshot_id = Column(UUID, ForeignKey(FK), primary_key=True)
    total = Column(Integer)
    green = Column(Integer)
    blue = Column(Integer)
    amber = Column(Integer)
    red = Column(Integer)
