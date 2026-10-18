# Real-Time Geospatial & OSINT Telemetry Data Sources

Harvested from global telemetry frameworks (including God's Eye View reference catalog) for OSINT investigations, flight tracking, maritime movement, satellite passes, and environmental sensors.

---

## 1. Flight Tracking & ADS-B

| Source | Endpoint / Access | Protocol / Format | Notes & Attribution |
|---|---|---|---|
| **OpenSky Network** | `opensky-network.org/api/states/all` | REST / JSON | Worldwide live flight state vectors. Non-commercial research license. Attribution: Schäfer et al. |
| **adsb.lol** | `api.adsb.lol/v2/lat/{lat}/lon/{lon}/dist/{radius}` | REST / JSON | Community ADS-B feed, ODbL 1.0. Covers military flights, traces, and GNSS integrity (NIC/NACp). |
| **adsbdb** | `api.adsbdb.com/v0/aircraft/{icao}` | REST / JSON | Aircraft type, registration, airline, callsign enrichment by ICAO hex code. |

---

## 2. Maritime & Vessel Tracking (AIS)

| Source | Endpoint / Access | Protocol / Format | Notes & Attribution |
|---|---|---|---|
| **AISStream.io** | `wss://stream.aisstream.io/v0/stream` | WebSocket / JSON | Live real-time worldwide maritime AIS broadcast stream (positions, vessel metadata, ship types). |
| **MarineTraffic** | `marinetraffic.com` (Web / API) | REST / Web | Commercial global ship tracking with port arrival/departure registries. |

---

## 3. Satellite Tracking & Orbital Telemetry (TLE / SGP4)

| Source | Endpoint / Access | Protocol / Format | Notes & Attribution |
|---|---|---|---|
| **CelesTrak** | `celestrak.org/NORAD/elements/` | HTTP / TLE text | Comprehensive NORAD two-line element sets for active satellites, space stations, debris. |
| **The Space Devs** | `ll.thespacedevs.com/2.3.0/launch/` | REST / JSON | Launch Library 2: orbital launch dates, payload catalogs, booster stages, recovery coordinates. |

---

## 4. Earthquakes & Seismic Monitoring

| Source | Endpoint / Access | Protocol / Format | Notes & Attribution |
|---|---|---|---|
| **USGS Earthquakes** | `earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php` | GeoJSON | Real-time global seismic events (M1.0+, M2.5+, M4.5+) updated every minute. US public domain. |
| **EMSC** | `www.seismicportal.eu/fdsnws/event/1/` | GeoJSON / FDSN-WS | Euro-Mediterranean Seismological Centre real-time earthquake telemetry. |

---

## 5. Atmosphere, Weather & Environmental Sensors

| Source | Endpoint / Access | Protocol / Format | Notes & Attribution |
|---|---|---|---|
| **NOAA GFS** | `noaa-gfs-bdp-pds.s3.amazonaws.com` | GRIB2 / S3 | Global 10m wind, temperature, mean sea-level pressure. Keyless public dataset. |
| **NOAA nowCOAST** | `nowcoast.noaa.gov/geoserver/` | WMS 1.1.1 | Contiguous US radar reflectivity (MRMS) and GOES infrared satellite imagery. |
| **Open-Meteo** | `api.open-meteo.com/v1/forecast` | REST / JSON | Keyless meteorological conditions, hourly historical records, atmospheric modeling (CC BY 4.0). |
| **NASA GIBS / CMR** | `gibs.earthdata.nasa.gov` | WMTS / REST | True-color satellite imagery (Sentinel-2, Landsat 8/9, VIIRS) and granule footprints. |
| **NIFC WFIGS** | `data-nifc.opendata.arcgis.com` | ArcGIS Feature Service | Real-time wildfire perimeters and active incident telemetry across North America. |

---

## 6. Public Traffic Cameras & Webcams (CCTV)

- **Caltrans**: `cwwp2.dot.ca.gov` (California highway CCTV)
- **TxDOT ITS**: `its.txdot.gov` (Texas traffic camera streams)
- **TfL JamCams**: `tfl.gov.uk/info-for/open-data-users/` (London traffic camera frames)
- **Statens vegvesen**: `kamera.atlas.vegvesen.no` (Norway highway webcams and HLS feeds)
- **Live Traffic NSW**: `opendata.transport.nsw.gov.au` (Australia NSW traffic cameras)
- **Ontario 511**: `511on.ca` (Ontario highway camera feeds)
