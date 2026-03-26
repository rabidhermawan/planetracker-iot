from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from datetime import datetime, timezone

from src import db

# Column reference : https://openskynetwork.github.io/opensky-api/rest.html

class Plane(db.Model):
  id: so.Mapped[int] = so.mapped_column(primary_key=True)
  
  created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, index=True,
    default= lambda: datetime.now(timezone.utc)
    )
  
  icao24:          so.Mapped[str] = so.mapped_column(sa.String(10), index=True, unique=True)
  callsign:        so.Mapped[Optional[str]] = so.mapped_column(sa.String(10), index=True)
  origin_country:  so.Mapped[str] = so.mapped_column(sa.String(60), index=True)
  
  plane_data: so.WriteOnlyMapped['PlaneData'] = so.relationship(
        back_populates='plane')
  def __init__(
      self, icao24 :str, callsign: str, origin_country: str
  ):
    self.icao24 = icao24
    self.callsign = callsign
    self.origin_country = origin_country
     
  def __repr__(self):
    return '<Plane Info {}>'.format(self.icao24)
  
  
class PlaneData(db.Model):
  id: so.Mapped[int] = so.mapped_column(primary_key=True)
  
  plane_id: so.Mapped[str] = so.mapped_column(sa.ForeignKey("plane.id"))
  
  time_fetched: so.Mapped[datetime] = so.mapped_column(sa.DateTime, index=True)
  
  time_position:   so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime)
  last_contact:    so.Mapped[datetime] = so.mapped_column(sa.DateTime)
  longitude:       so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
  latitude:        so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
  baro_altitude:   so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
  on_ground:       so.Mapped[bool] = so.mapped_column(sa.Boolean)
  velocity:        so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
  true_track:      so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
  vertical_rate:   so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
  sensors:         so.Mapped[Optional[list[int]]] = so.mapped_column(sa.JSON)
  geo_altitude:    so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
  squawk:          so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
  spi:             so.Mapped[bool] = so.mapped_column(sa.Boolean)
  position_source: so.Mapped[int] = so.mapped_column(sa.Integer)
  
  plane:        so.Mapped[Plane] = so.relationship(
        back_populates='plane_data')  
  
  def __init__(
      self, plane_icao24 :str, time_fetched: int, time_position: int,
      last_contact: int, longitude: float, latitude: float, baro_altitude: float,
      on_ground: bool, velocity: float, true_track: float, vertical_rate: float,
      sensors: list[int], geo_altitude: float, squawk: str, spi: bool, position_source: int
    ):
    
    self.plane_icao24 = plane_icao24
    
    self.time_fetched = datetime.fromtimestamp(time_fetched)
    
    self.time_position = datetime.fromtimestamp(time_position)
    self.last_contact = datetime.fromtimestamp(last_contact)
    self.longitude = longitude
    self.latitude = latitude
    self.baro_altitude = baro_altitude
    self.on_ground = on_ground
    self.velocity = velocity
    self.true_track = true_track
    self.vertical_rate = vertical_rate
    self.sensors = sensors
    self.geo_altitude = geo_altitude
    self.squawk = squawk
    self.spi = spi
    self.position_source = position_source
    
  def __repr__(self):
    return '<Flight Info {}>'.format(self.plane_icao24)