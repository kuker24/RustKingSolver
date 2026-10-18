# Public Intelligence Data Feeds (God's Eye View OSINT)

Curated inventory of real-time public telemetry, geospatial feeds, and observational streams derived from `bilawalsidhu/gods-eye-view`.

## 1. Flight Tracking (ADS-B)

- **OpenSky Network**
  - Type: REST API & State Vectors
  - URL: `https://opensky-network.org/api/states/all`
  - Coverage: Global air traffic with anonymous access limits; includes ICAO 24-bit transponder addresses, callsigns, latitude, longitude, barometric altitude, velocity, true track.
- **adsb.lol / ADS-B One**
  - Type: Open community ADS-B aggregator
  - URL: `https://api.adsb.lol/v2/`
  - Features: Unfiltered transponder tracking, military/VIP airframe tracking, no censorship/blocking of military or private registrations.

## 2. Maritime Vessel Tracking (AIS)

- **AISStream**
  - Type: WebSocket Streaming API
  - Endpoint: `wss://stream.aisstream.io/v0/stream`
  - Coverage: Real-time global Automatic Identification System (AIS) messages broadcast by commercial vessels, cargo ships, tankers, and passenger liners.
  - Data points: MMSI, ship name, IMO number, navigational status, rate of turn, speed over ground (SOG), position coordinates, destination port, ETA.

## 3. Satellite & Space Object Tracking (TLE / Orbit)

- **CelesTrak**
  - Type: Two-Line Element (TLE) and Orbit Ephemeris Data
  - URL: `https://celestrak.org/NORAD/elements/`
  - Catalogs: Active satellites, space stations (ISS, Tiangong), Starlink constellations, debris, classified payloads.
  - SGP4 Propagation: Enables precise ground track and orbital intercept modeling given epoch coordinates and timestamp.

## 4. Seismic & Geological Activity

- **USGS Earthquake Hazards Program**
  - Type: GeoJSON real-time feeds
  - Endpoints:
    - Significant past 30 days: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson`
    - All past 24 hours (M1.0+): `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson`
  - Attributes: Epicenter lat/lon/depth, Richter/moment magnitude, timestamp UTC, tsunami warning flags.

## 5. Thermal Anomalies & Wildfire Feeds

- **NASA FIRMS (Fire Information for Resource Management System)**
  - Sensors: MODIS (Terra/Aqua) and VIIRS (Suomi NPP, NOAA-20/21)
  - URL: `https://firms.modaps.eosdis.nasa.gov/api/`
  - Applications: Thermal signature detection, explosion verification, frontline combat thermal tracking, industrial flare monitoring, forest fire hotspots.

## 6. Space Launches & Celestial Missions

- **Launch Library 2 (The Space Devs)**
  - Type: REST API
  - URL: `https://ll.thespacedevs.com/2.2.0/launch/`
  - Attributes: Upcoming/past global orbital rocket launches, launchpad geographic coordinates, vehicle configurations, orbit apogee/perigee, mission payload descriptions.
