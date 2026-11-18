# Additional public datasets for the trace-driven access-point simulation

Scope: public datasets usable for a trace-driven simulation of an Internet access point (public Wi-Fi hotspot or home gateway), in addition to the two already in use (City of Paris Wi-Fi session logs; HSDPA 3G commute logs of Riiser et al., MMSys 2013).

All downloads are in separate sub-directories of `data/raw/` (git-ignored). Nothing downloaded was executed. Formats were inspected with small `python3 -I` snippets. Total new data on disk: about 1.28 GB (limit 1.5 GB). Dates of retrieval: November 2026. All TLS connections verified normally through the configured proxy; no host needed a TLS workaround.

Host-level blocks seen (policy/proxy, not TLS): `www.fcc.gov` (HTTP 403), `opendata.bcn.cat` (403), `api.github.com` and `codeload.github.com` for repositories not attached to the session (403; public git clones over the git proxy worked and were used instead).

## 1. Ranked summary of what was downloaded

| Rank | Local directory | What it gives | Main use in the simulation |
|---|---|---|---|
| 1 | `data/raw/grandparissud_wifi_sessions/` | 38,465 RADIUS accounting sessions of a French public Wi-Fi network (start, duration, bytes in/out, terminate cause, device type, site category), Jul-Aug 2026 | arrivals, stays, per-session volume, site-type mix |
| 2 | `data/raw/socrata_mesa_wifi_sessions/` | 913,507 per-association records of the City of Mesa (Arizona) Wi-Fi (start, end, duration, bytes, SSID, AP, OS, disconnect reason), three months from 2018, 2023, 2025 | arrivals, stays, volume, multi-year drift |
| 3 | `data/raw/socrata_canberra_uc_wifi_sessions/` | 510,111 campus Wi-Fi sessions, 1-14 April 2017 (duration in minutes, average kbit/s, device vendor, AP) | stays, per-session rate, campus arrivals |
| 4 | `data/raw/zenodo_raca_4g_lte/` | 135 four-G traces, 1 s resolution, five mobility types, with channel metrics | capacity series (4G) |
| 5 | `data/raw/github_uccmisl_5Gdataset/` | 83 five-G production traces, 1 s resolution (video streaming and file download, static and driving) | capacity series (5G) |
| 6 | `data/raw/ghent_4g_lte/` | 40 four-G bandwidth logs, about 1 s, Ghent 2015-16, six transport modes | capacity series (4G), direct counterpart of the HSDPA logs |
| 7 | `data/raw/mahimahi_traces/` | cellular packet-delivery traces (Verizon, AT&T, T-Mobile; 3G/4G; up and down) | capacity series, ms-level |
| 8 | `data/raw/nantes_wifi_daily_stats/` | daily per-hotspot sessions, mean duration, traffic, hourly session counts, Feb 2022 - Oct 2026 | diurnal and weekly arrival profile, mean stay and demand |
| 9 | `data/raw/bologna_wifi_hourly_occupancy/` | hourly device counts per Wi-Fi zone (76 zones, 2024) plus daily unique connections 2023-2026 | arrival-rate shape, occupancy |
| 10 | `data/raw/purdue_vca_dataset/` | packet-level traces of Zoom, Teams, Meet, Webex under constant, changing and competing load (sample, 20 experiments plus map) | real-time class rate and packet-size model |
| 11 | `data/raw/zenodo_vlc_data_pcap/` | six pcapng captures labelled by application (Netflix, Teams, Roblox, Spotify, web) | per-application rates, class mix |
| 12 | `data/raw/zenodo_commect_5g_satellite_rural/` | 1 s throughput of two 5G operators and a satellite link (Denmark, 2023) | capacity series, multi-link uplink |
| 13 | `data/raw/zenodo_nordicdat/` | 91,456 one-second LTE/5G samples with throughput and radio metrics (Finland, Sweden, Norway) | capacity series with mobility |
| 14 | `data/raw/zenodo_monroe_speedtest_tstat/` | 30,295 HTTP download flows from stationary MONROE nodes (Tstat) | per-flow bytes and duration, stationary mobile access |
| 15 | `data/raw/zenodo_hanoi_market_wifi/` | per-device, per-market dwell summaries (hashed MAC, minutes) from free-Wi-Fi routers | stay and revisit distribution (aggregated) |
| 16 | `data/raw/socrata_act_cbrfree_monthly/`, `socrata_linknyc_usage/`, `socrata_austin_library_wifi/`, `pittsburgh_clp_wifi/`, `wyndham_libraries_wifi/` | monthly or weekly aggregates (sessions, mean duration, traffic) | sanity checks of mean stay and volume per session |
| 17 | `data/raw/zenodo_starlink_athens/` | 7-day Starlink latency and throughput, 60 s cycle | backhaul variability for a home gateway (coarse) |

## 2. Per-dataset records

### 2.1 Grand Paris Sud "Wifi territorial" user sessions

- **Name, publisher:** "[Nouveaux Flux / Wifi territorial] Table des sessions utilisateurs" and "[Nouveaux flux Wifi territorial] Durée des sessions utilisateurs"; publisher field "QoS Télécom", portal "Opendatasoft de Grand Paris Sud".
- **URL:** https://data.grandparissud.fr/explore/dataset/nouveaux-flux-wifi-territorial-table-sessions-utilisateurs/ and https://data.grandparissud.fr/explore/dataset/nouveaux-flux-wifi-territorial-duree-des-sessions-utilisateurs/ (downloaded through the federated catalogue `data.opendatasoft.com`, dataset ids with suffix `@grandparissud`).
- **Licence:** not stated (the licence and licence-URL fields are null in the portal metadata).
- **Citation requested:** none stated. Suggested: publisher, title, URL, access date.
- **Local files:** `sessions.csv` (15 MB; selected columns, the pseudonymised hashed user, MAC and e-mail fields inside the raw JSON blob were deliberately not exported), `durations.csv`, `meta_sessions.json`.
- **Time span:** 2026-07-29 to 2026-08-31 (session start). **Records:** 38,465 (both tables).
- **Columns, `sessions.csv`:** `uuid`; `timestamp` (record time, UTC); `start_time_session` (UTC); `acct_session_time` (ISO-8601 duration, e.g. P0DT00H02M12S); `acct_terminate_cause` (Lost-Carrier 18,140, Idle-Timeout 15,597, Ghost Session 3,668, NAS-Request 862, Session-Timeout 191, Admin-Reset 7); `device_type` (computer / phone;make;model); `city`; `hotspot_name`; `sites` (category such as équipement sportif, culturel, point d'information, hôtel de ville, transport; 1,203 blank); `type_site` (piscine 15,989, médiathèque 4,378, mairie 2,454, gare routière 1,537, conservatoire, centre de formation, ...); `commune`; `perimetre`; `donnees_recues_en_go` and `donnees_envoyees_en_go` (decimal GB, i.e. bytes/1e9, received and sent by the device); `year_extract`.
- **Columns, `durations.csv`:** `uuid`, `timestamp`, `acct_session_time`, `city`, `designation` (site), `acct_start_time` (Unix s), `duration_in_seconds`, `duration_in_days`.
- **Resolution:** per session, 1 s.
- **Observed statistics:** session duration median 77 s, 90th percentile 3,093 s, 99th percentile 17,943 s, maximum 43,905 s (376 sessions of 0 s); bytes received median 0.12 MB, 90th percentile 36 MB, total 1.45 TB.
- **Could replace:** arrivals (start times by site type and hour), stay-time distribution (very heavy tail), per-session downlink and uplink volume, a class proxy via `type_site` and `device_type`. It is the closest analogue of the Paris logs and has a paid/free-like field only through `type_site`; no plan field.
- **Limitations:** one 5-week window; some "Ghost Session" records; terminate cause "Lost-Carrier" means the end time is inferred; no per-application label; no packets; user identifiers withheld by the publisher so repeat visits cannot be linked in the export used here.

### 2.2 City of Mesa (Arizona) Wi-Fi activity on city-owned access points

- **Publisher:** City of Mesa, Information Technology. **URL:** https://citydata.mesaaz.gov/d/2vtm-mpvz (Socrata API `https://citydata.mesaaz.gov/resource/2vtm-mpvz`).
- **Licence:** the portal field reads "See Terms of Use" pointing to https://data.mesaaz.gov/stories/s/2dcd-j2nx/ ; the text of that page could not be retrieved (it is rendered by script). Treat as: terms not retrievable. The description says: "Sensitive fields such as device MAC address have been scrambled and are not actual addresses."
- **Citation requested:** not stated.
- **Size on disk:** 157 MB (`mesa_2018_04.csv` 37 MB, `mesa_2023_10.csv` 25 MB, `mesa_2025_07.csv` 95 MB). The full dataset has 47,797,716 rows from 2017-01 to 2026-10 and is too large; whole calendar months were downloaded as representative parts (2018-04: 230,278 rows; 2023-10: 141,309; 2025-07: 541,920). Monthly record counts for the whole series were queried and range from 9 thousand to 4.3 million.
- **Columns:** `starttime`, `endtime`, `session_duration` (s, AP-reported), `calcdsession_duration` (s, recomputed when several APs overlap), `bytes_from_user` and `bytes_to_user` (bytes per session), `ssid` (`@mesa` is the public network, 40,997,227 rows overall; `private-ssidN` are city SSIDs), `ap_name`, `ap_location` (text, often blank), `client_mac` (scrambled, consistent per device), `os_type`, `encryption`, `disconnect_reason` (802.11 reason code or text). Columns `ap_mac`, `disconnecttime`, geometry were not exported.
- **Observed:** 2018-04 median duration 991 s, mean 1,701 s; 2023-10 median 41 s, mean 5,244 s (behaviour changed over years); 96% (2018) and 82% (2023) of rows are `@mesa`.
- **Resolution:** per association, 1 s.
- **Could replace:** arrivals (inter-arrival per AP), stay times, volume per session in both directions, device-class mix by `os_type`; the scrambled but consistent `client_mac` allows revisit and returning-user statistics.
- **Limitations:** associations, not user logins (re-associations split stays); part of the traffic belongs to city devices on private SSIDs, filter `ssid = '@mesa'`; no application label; byte counters may be 0 for short sessions; terms of use not retrievable.

### 2.3 University of Canberra Wi-Fi usage

- **Publisher:** University of Canberra via ACT Government open data. **URL:** https://www.data.act.gov.au/d/pawc-bj4d
- **Licence:** "Creative Commons Attribution 4.0 International" (portal licence field, terms link http://creativecommons.org/licenses/by/4.0/legalcode).
- **Citation requested:** attribution to University of Canberra; no paper.
- **Size:** 108 MB local (14 days). Full dataset 2,446,421 rows (2017-03-31 to 2017-05; 1.23 M in April, 1.19 M in May). Local file `uc_wifi_2017_04_01_to_14.csv`: 510,111 sessions, all SSID `UC-Student`.
- **Columns:** `user_id` (pseudonym), `mac_address` (pseudonym number), `vendor` (device maker), `location_code`, `location_desc`, `ssid`, `profilename`, `vlan`, `protocol` (802.11a/g/n/ac), `session_duration` (text, e.g. "5min 0sec"), `policy_type`, `avg_kbps` (text, may be "<0.1"), `session_duration_formatted` (minutes), `avg_kbps_formatted` (kbit/s, session average), `connect_date` (local time, no zone), `latitude`, `longitude` (AP). `ip_address` column of the original was not exported.
- **Observed:** session duration median 5.0 min, mean 18.9 min.
- **Resolution:** per session; duration rounded to seconds; average rate is a single number per session.
- **Could replace:** campus arrivals with day/night pattern, stays, per-session average rate (a demand proxy: bytes = rate times duration), device-vendor mix. Fixed 5-minute modal stay suggests a re-association timer, which should be checked.
- **Limitations:** one month (two weeks kept); no byte counts (only average rate); sessions of a few minutes are probably forced re-authentication cycles; 2017 vintage; times without time zone (Australian Eastern).

### 2.4 Nantes Métropole "Nantes Wifi Public" usage statistics

- **Publisher:** Nantes Métropole. **URL:** https://data.nantesmetropole.fr/explore/dataset/244400404_statistiques-utilisation-wifi-public-exterieur-nantes-metropole/
- **Licence:** "Licence Ouverte-LO" (Etalab; https://www.etalab.gouv.fr/licence-ouverte-open-licence). **Citation:** attribution to the publisher (Licence Ouverte requirement).
- **Size:** 3.4 MB; 19,610 rows; 2022-02-01 to 2026-10-31; 45 hotspots.
- **Columns:** `jour` (date), `hotspot`, `nb_utilisateurs_uniques` (monthly unique users), `nb_nouveaux_utilisateurs`, `nb_sessions` (per day), `moy_duree_session` (mm:ss), `total_trafic` (GB per day), `moy_dowload` and `moy_upload` (MB per session), `h00`...`h23` (sessions started per hour of day), `nb_utilisateurs_uniques_day`, `nb_nouveaux_utilisateurs_day`, `mois`, `nb_min`, `nb_sec`, `nb_secondes_duree_session`, `vacances_zone_b`, `statut` (working/holiday day), `jour_semaine`.
- **Resolution:** daily per hotspot with hourly session counts.
- **Could replace:** time-of-day and weekday arrival intensity per hotspot (24 values per day), mean stay and mean demand per session, holiday effects. Gives an out-of-sample check against the Paris and Grand Paris Sud logs.
- **Limitations:** aggregated; only means (no distribution of durations); one mean duration per day.

### 2.5 BolognaWiFi hourly occupancy and daily connections

- **Publisher:** Comune di Bologna (Iperbole). **URLs:** https://data.opendatasoft.com/explore/dataset/bolognawifi-affluenza-storico-2024@bologna/ and `bolognawifi-connessioni-giornaliere@bologna`. Further years (2021, 2022, 2023, 2025 for "affluenza", and "affollamento" series) exist with the same schema and were not downloaded (about 47 MB each).
- **Licence:** "CC BY 4.0" (https://creativecommons.org/licenses/by/4.0/). **Citation:** attribution to Comune di Bologna.
- **Files:** `affluenza_2024.csv` (46.9 MB; 666,869 rows; 76 zones; 2023-12-31T23:00Z to 2024-12-31T22:00Z) with columns `id` (zone code), `name`, `data` (hour, UTC), `value` (average number of devices present in the zone in that hour; mean over all rows 59.4). `connessioni_giornaliere.csv` (1,414 rows, 2023-01-01 to 2026-11-16): `data`, `connessioni` (distinct devices per day, about 90-105 thousand in mid-November 2026).
- **Could replace:** hourly offered-load shape across a whole city network (occupancy, not sessions), seasonality.
- **Limitations:** occupancy of devices, not sessions, volumes or stays; aggregated in time and zone.

### 2.6 Hanoi traditional-market free Wi-Fi (Zenodo)

- **Publisher:** Alliance of Bioversity International and CIAT with General Statistics Office of Vietnam. **URL / DOI:** https://doi.org/10.5281/zenodo.5707312 . Published 2021-11-17.
- **Licence:** Creative Commons Attribution 4.0 International (Zenodo licence field `cc-by-4.0`). **Citation:** Reymondin, Le, Vantalon, Pham et al., "Free WiFi to monitor flow in Hanoian traditional markets", Zenodo, 2021, doi 10.5281/zenodo.5707312 (no paper).
- **Size:** 55 MB, three CSV files (`baseline.csv` 229,938 rows, `preshock.csv` about 230,785, `shock.csv` about 192,985 rows). Time span of the three periods is not stated in the record.
- **Columns (units from the record description):** `mac` (SHA-3 256 hash of the MAC, in the files as a shortened colon-separated string), `market`, `role`, `gender` (self-declared if the user filled the Wi-Fi form, else UNKNOWN/ANY), `median_first_seen` and `median_last_seen` (minutes after midnight), `average_time_day` (mean number of visits per day; two hours gap starts a new visit), `average_duration_day` (mean minutes spent per day), `average_day_week` (mean visits per week), `average_total_day_seen` (days seen), `total_durantion` (total minutes, column name spelled so in the file).
- **Could replace:** distribution of dwell time, visit frequency and time-of-day of presence of individual devices (seen by probe requests, whether connected or not).
- **Limitations:** already aggregated per device and market; no session timestamps; presence, not traffic; markets not an Internet-access-point workload; unspecified collection dates.

### 2.7 Raca et al. 4G/LTE dataset (UCC)

- **Publisher:** University College Cork (Raca, Quinlan, Zahran, Sreenan). **URL / DOI:** https://doi.org/10.5281/zenodo.1219679 (published 2018-06-12).
- **Licence:** Creative Commons Attribution 4.0 International (Zenodo `cc-by-4.0`). **Citation requested:** by the associated paper.
- **Size:** 2.2 MB zip, 19.5 MB extracted (`LTE_Dataset.zip`; the 4 MB ns-3 synthetic zip was not downloaded). 135 traces (car 53, pedestrian 31, train 20, bus 16, static 15), 174,523 one-second rows, Dec 2017 - Feb 2018 (from file names), two operators (A, B), Cork, Ireland.
- **Columns:** `Timestamp` (yyyy.mm.dd_hh.mm.ss), `Longitude`, `Latitude`, `Speed` (km/h), `Operatorname`, `CellID`, `NetworkMode`, `RSRP` (dBm), `RSRQ` (dB), `SNR` (dB), `CQI`, `RSSI` (dBm), `DL_bitrate`, `UL_bitrate` (kbit/s; observed maximum 173,016 which matches the published 173 Mbit/s), `State` (D download, I idle, ...), `NRxRSRP`, `NRxRSRQ`, `ServingCell_Lon`, `ServingCell_Lat`, `ServingCell_Distance` (m).
- **Statistics:** downlink median 5.4 Mbit/s, 95th percentile 41.5 Mbit/s.
- **Resolution:** 1 s (non-rooted Android monitor, so values are application-level throughput).
- **Could replace:** link capacity time series for a mobile backhaul or a cellular user device; mobility class as a covariate.
- **Limitations:** throughput is measured while the application downloads, so low values may reflect application pauses rather than capacity; one country, two operators; sampling timestamps sometimes repeated within a second.

### 2.8 Raca et al. 5G production dataset (UCC)

- **Publisher:** University College Cork. **URL:** https://github.com/uccmisl/5Gdataset (public git clone, `5G-production-dataset.zip`, 2.2 MB, extracted 23 MB).
- **Licence:** repository licence file is GNU General Public License v3 ("GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"). The README asks: "We kindly ask that should you mention our dataset or framework, or use our code, in your publication, that you would reference the following paper".
- **Contents:** 83 csv traces, 188,711 one-second rows: Amazon Prime (Driving 21, Static 8), Netflix (Driving 23, Static 10), Download (Driving 16, Static 5), December 2019, Cork area.
- **Columns:** `Timestamp`, `Longitude`, `Latitude`, `Speed`, `Operatorname`, `CellID`, `NetworkMode`, `RSRP`, `RSRQ`, `SNR`, `CQI`, `RSSI`, `DL_bitrate`, `UL_bitrate` (kbit/s; maximum 194,256), `State`, `PINGAVG`/`PINGMIN`/`PINGMAX`/`PINGSTDEV`/`PINGLOSS`, `CELLHEX`, `NODEHEX`, `LACHEX`, `RAWCELLID`, `NRxRSRP`, `NRxRSRQ`.
- **Statistics:** downlink median 0 (many idle seconds between video chunks), 95th percentile about 10 Mbit/s for the streaming traces.
- **Could replace:** capacity series for 5G; the Download traces approximate saturated capacity, the streaming traces show the application-limited rate of a video client (one real-time/bulk example).
- **Limitations:** much of the data is application-limited; the repository holds only the production part (the ns-3 framework is not included in the clone); a single operator.

### 2.9 Ghent University 4G/LTE bandwidth logs

- **Publisher:** IDLab, Ghent University - imec. **URL:** https://users.ugent.be/~jvdrhoof/dataset-4g/ (files `logs/logs_all.zip`, 384 KB).
- **Licence:** not stated. Request on the page: "If you use the traces, please refer to the related journal paper as follows: J. van der Hooft, S. Petrangeli, T. Wauters, R. Huysegems, P. Rondao Alface, T. Bostoen, and F. De Turck, HTTP/2-Based Adaptive Streaming of HEVC Video over 4G/LTE Networks, IEEE Communications Letters, vol. 20, no. 11, pp. 2177-2180, 2016."
- **Contents:** 40 logs (bicycle, bus, car, foot, train, tram), 18,036 rows, 2015-12-16 to 2016-02-04, 166-758 s each, about 5 hours total, Ghent.
- **Columns (six, space separated):** Unix ms; ms since experiment start; GPS latitude; GPS longitude; bytes received since the last data point; ms since the last data point. Throughput = column 5 / column 6 (bytes per ms; times 8 for kbit/s).
- **Resolution:** about 1 s. **Could replace:** a second source of 4G capacity series with the same construction as the HSDPA logs, so it can be pooled with them.
- **Limitations:** short, mostly saturated downloads over a 100 Mbit/s server link, so the cap is near 95 Mbit/s; one phone; no uplink.

### 2.10 Mahimahi / Sprout cellular traces

- **Publisher:** Winstein, Sivaraman, Balakrishnan (MIT) via the Mahimahi repository. **URL:** https://github.com/ravinet/mahimahi (public clone; `traces/`, 30 MB; the rest of the repository is source code that was not run).
- **Licence:** repository is GPL (`COPYING`). The traces README states they "were recorded using the 'Saturator' tool described in the research paper: K. Winstein, A. Sivaraman, and H. Balakrishnan, Stochastic Forecasts Achieve High Throughput and Low Delay over Cellular Networks".
- **Files:** 16 traces (`*.up`, `*.down`): ATT-LTE-driving (2 versions), TMobile-LTE (driving, short), TMobile-UMTS-driving, Verizon-EVDO-driving, Verizon-LTE (driving, short). Each file lists, one integer per line, the millisecond timestamp at which a 1,500-byte packet delivery opportunity occurred. Durations 120 s to 1,365 s; average rates from 0.5 Mbit/s (Verizon EVDO down) to 19 Mbit/s (T-Mobile LTE up).
- **Could replace:** capacity at ms resolution for uplink and downlink of 2012-13 US cellular networks; also usable directly in a packet-level link emulator.
- **Limitations:** old networks; saturated measurement; only a handful of traces; time stamps are packet opportunities, not rates (aggregate per second to obtain a series).

### 2.11 Purdue video-conferencing application dataset (sample)

- **Publisher:** Purdue University (Cherian, Prasad, Fahmy). **URL:** https://www.cs.purdue.edu/homes/fahmy/datasets/VCAPurdue (file `pam2026.zip`, 2.59 GB, too large).
- **Licence:** not stated on the page. **Citation requested:** "This dataset was collected for our paper: Nathaniel Cherian, Akhil Prasad, Sonia Fahmy, 'A Microscopic View of Congestion Control Behavior in Video Conferencing Applications,' In Proc. of Passive and Active Measurement Conference (PAM), March 2026."
- **Part downloaded:** 178 MB (by HTTP range requests of selected zip members): 20 experiment directories (per application, two ConstantBandwidth, one ChangeBandwidth, one TCPBackground, one UDPBackground for Zoom, Microsoft Teams, Google Meet and Cisco Webex) plus `ip_company_map.csv`.
- **Files per experiment:** `inbound_traffic_buffer_in.csv`, `..._out.csv`, `outbound_traffic_buffer_in.csv`, `..._out.csv` (columns `time` Unix s, `src`, `dst`, `src_port`, `dst_port`, `protocol`, `size` bytes, `rtp_PT`, `rtp_ssrc`, `rtp_seq`, `rtp_ts`; IP addresses anonymised), `*_buffer.log` (queue log), `qoe.csv` (`timestamp` ms, `qr_code_data`, `time_sent`, `time_received`, `latency`, `vif_score`, `ssim_score`, `psnr_score`, `vmaf_score`).
- **Could replace:** packet-size and rate model of a real-time class with its response to a bottleneck (constant rates of 1.2 to several Mbit/s, step changes, competing TCP or UDP), plus quality metrics as a function of capacity.
- **Limitations:** controlled testbed with an emulated bottleneck, not an access network; two-party calls; only a sample of the experiments; licence unknown.

### 2.12 VLC Data multi-class traffic (Zenodo), sample

- **Publisher:** MaxLinear Hispania and Universitat de València (Rau, Herranz, Val, Georgieva, Perez). **URL / DOI:** https://doi.org/10.5281/zenodo.15121418 (published 2025-04-01; 58 pcapng files, 24 GB in total).
- **Licence:** Creative Commons Attribution 4.0 International (Zenodo `cc-by-4.0`). **Citation requested:** "If you find this dataset useful for your work, please consider citing us: Francisco Rau, Carlos Herranz, Iñaki Val, Petia Georgieva, Joaquin Perez, 'A Novel Flow-Based Online Network Traffic Classification Using Machine Learning', TechRxiv 2025. https://doi.org/10.36227/techrxiv.175459507.75164419/v1" (DOI as stated in the record; not independently resolved).
- **Part downloaded:** 536 MB, six files: `web_linux_5m_google`, `web_linux_5m_bbc`, `spotify_windows_30m_02`, `teams_linux_20m_01`, `netflix_windows_10m_01`, `roblox_windows_20m_01`. Application is in the file name; the full set additionally has YouTube (HD and 4K), Prime Video, other Netflix, Teams, Spotify and web runs, durations 2-50 min.
- **Format:** pcapng (little-endian), full-length packets; the first packet block parses with a small pure-Python reader. Rough average rates computed from original lengths over the capture time (capture includes protocol overhead; time units differ between the Linux and Windows files): Teams 0.8 Mbit/s over 20 min, Netflix about 1.9 Mbit/s, Roblox about 0.7 Mbit/s, Spotify about 0.27 Mbit/s, one 5-minute web page about 0.7-1.7 Mbit/s.
- **Could replace:** per-application mean rate and burstiness for a class mix (streaming, real-time conferencing, gaming, audio, web). Rates must be recomputed with a proper pcap tool before use.
- **Limitations:** single clients on a lab network, VM-less laptops; no flow table; packets, not sessions; few repeats.

### 2.13 CoMMECT multi-connectivity throughput (Denmark)

- **Publisher:** Aalborg University (Horizon Europe COMMECT project). **URL / DOI:** https://doi.org/10.5281/zenodo.14616441 (2025-01-09; sister record 10.5281/zenodo.16919305 with a highway campaign in Matlab format, not downloaded).
- **Licence:** Creative Commons Attribution Share-Alike 4.0 (`cc-by-sa-4.0`). **Citation:** dataset DOI; the zip also contains two PDF papers.
- **Size:** 5 MB zip. `Operator_A_throughput.csv`, `Operator_B_throughput.csv` (columns `Time`, `RSRP (dBm)`, `RSRQ (dB)`, `SNR (dB)`, `Throughput (Mbps)`) and `Satellite_throughput.csv` (`Time`, `Latitude`, `Longitude`, `Throughput (Mbps)`); about 3,766 rows each (about 1 h), 1 s resolution, starting 2023-10-04 10:08:24.
- **Could replace:** simultaneous capacity series for two terrestrial links and one satellite link (uplink aggregation, failover).
- **Limitations:** one hour, one route; satellite series is capped near 100 Mbit/s in the first rows (probably a test cap).

### 2.14 NordicDat

- **Publisher:** Miekkala, Pyykonen, Drainakis et al. **DOI:** https://doi.org/10.5281/zenodo.10964584 (2024-04-12). **Licence:** CC BY 4.0 (`cc-by-4.0`).
- **Size:** 14.3 MB, one CSV, 91,456 rows at about 1 s (Unix epoch with fraction; first sample 2024-01-08).
- **Columns:** `timestamp`, `latitude`, `longitude`, `elevation`, `velocity_abs`, `acceleration_abs`, `rsrq`, `rssi`, `rsrp`, `sinr`, `band`, `ran` (LTE or 5G), `serving_cell_id`, `velocity_long`, `acceleration_lat`, `acceleration_long`, `delay`, `heading`, `gnss_mode`, `service_status`, `operator`, `throughput_downlink`, `throughput_uplink`. Units of throughput are not stated in the record; values such as 3,360 suggest kbit/s (to be confirmed before use).
- **Could replace:** capacity series with roaming effects and mobility. **Limitations:** units unconfirmed; border areas only; the associated paper was not checked.

### 2.15 MONROE speedtest-like flows (Zenodo)

- **Publisher:** Politecnico di Torino, Karlstad University and partners. **DOI:** https://doi.org/10.5281/zenodo.887541 (2017-09-07). **Licence:** CC BY 4.0 (`cc-by-4.0`).
- **Part downloaded:** `clients_tstat_tcp_log.zip` (1.3 MB, 4 MB extracted): 30,295 flows with columns `start` (Unix s), `s_bytes` (server-to-client bytes), `duration` (s), `node_id`, `interface`, `c_rtt_avg`, `s_rtt_avg` (ms), `c_ttl_max`, `s_ttl_max`, `c_first`, `s_first_ack`, `c_ip`, `c_win_scl`, `c_mss`, `c_win_0`, `c_f1323_opt`, `c_tm_opt`, `s_ip`, `s_port`, `c_port`. Single-thread curl download of a 40 MB file for at most 10 s, every 3 h, Sep-Oct 2016, stationary nodes in four countries. The server-side log (79 MB) and node metadata (63 MB) were not downloaded.
- **Citation:** Khatouni, Mellia, Ajmone Marsan, Alfredsson, Karlsson, Brunstrom et al., ITC 29, 2017, doi 10.23919/ITC.2017.8064353.
- **Could replace:** achievable per-flow throughput (`s_bytes/duration`) of stationary 3G/4G access. **Limitations:** 10-second saturated samples every 3 h; no per-second series.

### 2.16 Small aggregate tables (Wi-Fi sessions and traffic per period)

All are small CSVs, useful only to cross-check mean session length and volume per session.

| Directory | Source and licence statement | Content |
|---|---|---|
| `socrata_act_cbrfree_monthly/` | CBRfree Wi-Fi (Pipe Networks for ACT Government), CC BY 4.0 per portal field | 130 monthly rows, Nov 2014 - Sep 2026: unique clients, sessions, unique users, APs, mean session minutes, total traffic MB, mean traffic per session (kB), mean throughput |
| `socrata_linknyc_usage/` | LinkNYC kiosks, NYC Office of Technology and Innovation; no licence field (NYC Open Data terms apply; the portal host returned HTTP 403 to page requests but the data API answered) | historical weekly sessions, bandwidth (TB), mean session duration, subscribers (200 weeks from 2016-02-29) and weekly 2020-01-05 to 2026-11-08 (358 rows: sessions, mean session length, unique clients, TB down and up) |
| `socrata_austin_library_wifi/` | Austin Public Library; no licence field | 2,508 monthly rows per branch, Oct 2017 - Oct 2026: sessions and GB |
| `pittsburgh_clp_wifi/` | Carnegie Library of Pittsburgh via WPRDC; "Open Data Commons Public Domain Dedication and License (PDDL)" | 532 rows from 2016: sessions and minutes per branch and month, with data dictionary |
| `wyndham_libraries_wifi/` | Wyndham City Libraries; CC BY 4.0 | five yearly tables, four libraries each, sessions and GB (2013-2018; the first two years are mostly empty) |

Limitation of all: monthly or weekly aggregation, no distribution.

### 2.17 Starlink Athens 7-day characterisation

- **Publisher:** NEXASPHERE project (Horizon Europe grant 101192912). **DOI:** https://doi.org/10.5281/zenodo.20796667 (2026-06-23). **Licence:** CC BY 4.0.
- **Size:** 6 MB zip (54 MB extracted): `throughput_Down.csv` (2,025 rows: `timestamp_utc`, `cycle`, `iperf3_dl_mbps`, loss, `speedtest_dl_mbps`, `speedtest_ping_ms`, dish-reported bps, server), `latency.csv` (20,243 rows: min/avg/max ms, loss % to 8.8.8.8 and 1.1.1.1), JSON copies and logs; 60 s measurement cycle, throughput every fifth cycle, 11-18 May 2026.
- **Could replace:** coarse variability of a satellite backhaul and its latency for a home gateway. **Limitations:** one-minute or five-minute resolution; one dish.

## 3. Candidates reached but not downloaded

| Candidate | Reachable? | Why not downloaded |
|---|---|---|
| Barcelona Wireless Footprints (Zenodo 10.5281/zenodo.24159218, published 2026-11-13, 277 MB zip) | yes | Not session logs: Wi-Fi/cellular signal scans and passive captures; licence CC BY-NC-ND 4.0 forbids derivatives; kept under budget. Contains "observed client activity" per access point (70,908 networks) which might give a station-count proxy. |
| Mobile broadband speedtest traces (Zenodo 814898, 1.4 GB, Torino, includes the open WoW-Fi community Wi-Fi) | yes | Too large for the budget (single zip of 1.43 GB); packet traces from 600 s iperf uploads; CC BY 4.0. |
| MIRAGE-2019 (https://traffic.comics.unina.it/mirage/mirage-2019.html; also Zenodo 23158592) | yes, direct link | 1.46 GB tarball alone would exceed the remaining budget; licence CC BY-NC-ND 4.0 ("Creative Commons Attribution-NonCommercial-NoDerivatives 4.0"). Related sets MIRAGE-COVID-CCMA-2022 (3.1 GB), MIRAGE-Video (2.0 GB), MIRAGE-AppAct-2024 (7 GB) are larger. Citation requested: Aceto, Ciuonzo, Montieri, Persico, Pescapè, ICCCS 2019 (BibTeX below). |
| Purdue VCA remainder | yes | 2.59 GB zip; a 178 MB sample was taken. |
| Starlink latency and downlink throughput (Zenodo 10020034, 1.2 GB) | yes | Too large for the remaining budget; the small Athens set was taken instead. |
| MONROE SOMETIME (Zenodo 1300512, 654 MB) | yes | Pathload/Yaz available-bandwidth experiments with packet traces; large and tool-specific; CC BY-SA 4.0. |
| Longitudinal WiFi, EPFL campus (Zenodo 1038622, 4 MB, doi 10.1016/j.jocm.2016.04.003) | yes | Licence CC BY-NC-SA 4.0; it is a model-estimation archive (software, processed choice data) rather than a session log, not inspected. |
| LinkNYC and other Socrata portals | yes (API) | Only weekly aggregates exist; included in 2.16. |
| Geelong / Western Parklands nCounter Wi-Fi device counts (Opendatasoft, e.g. 894,880 rows) | yes | People counting by probe requests, not access-point sessions. |
| Other Opendatasoft portals searched (Rennes, Toulouse, Strasbourg, Bordeaux, Ile-de-France Mobilités, SNCF, RATP) | yes | Only locations of access points; no usage data found. |
| Toronto free public Wi-Fi (CKAN) | yes | Locations only. |
| UK rail, Helsinki, Singapore, Madrid, Barcelona (opendata.bcn.cat) | not found / host blocked | No per-session Wi-Fi dataset found by catalogue searches (UK and Helsinki CKAN endpoints did not return usable results; Singapore catalogue API did not answer; opendata.bcn.cat returned HTTP 403 from the proxy). |

## 4. Not reachable without a login, registration or request

| Dataset | Where | Reason |
|---|---|---|
| CRAWDAD ilesansfil/wifidog (Montreal free hotspots 2004-2010; user id, MAC, login/logout, hotspot id, bytes in and out; licence listed as Creative Commons Attribution) | https://ieee-dataport.org/open-access/crawdad-ilesansfilwifidog (doi 10.15783/C7H883) | Page states "LOGIN TO ACCESS DATASET FILES ... You need a free IEEE account". Not attempted. Files: csv.gz, sql.gz. |
| CRAWDAD dartmouth/campus (several versions 2004-2009; campus Wi-Fi syslog, SNMP and tcpdump) | IEEE DataPort collection "crawdad", pages `crawdad-dartmouthcampus-v-2004-08-05` ... `v-2009-09-09` | Login required (same collection). |
| CRAWDAD iitkgp/apptraffic (application traffic), srfg/lte-4g-highway-drive-tests-salzburg, kaist/wibro, microsoft/vanlan, mit/reality, umass/diesel, uw/sigcomm2004, standrews/locshare, rutgers/apdensity | same collection | Login required; listed as potentially relevant. |
| MIRAGE on IEEE DataPort (doi 10.21227/maj9-vh13) | https://ieee-dataport.org/node/1725 | Needs an IEEE account; a direct download without login exists at the authors' site (see section 3). |
| ISCX VPN-nonVPN 2016 (UNB CIC) | https://www.unb.ca/cic/datasets/vpn.html leading to https://cicresearch.ca/CICDataset/ISCX-VPN-NonVPN-2016/ | The download page is a registration form (name, e-mail, organisation, country); excluded by the "no registration" condition. Citation: Draper-Gil et al., ICISSP 2016 (below). |
| Lumos5G v1.0 (UMN, CC BY 4.0 per project page) | https://networking.umn.edu/lumos5g , https://networking.umn.edu/datasets | The current UMN datasets page sends users to a "dataset request" form (institution, project, intended use); IEEE DataPort mirror needs a login (https://ieee-dataport.org/node/3598). Not attempted. |
| FCC Measuring Broadband America raw data | https://www.fcc.gov/oet/mba/raw-data-releases | Request through the proxy returned HTTP 403 (policy denial); not retried. |
| MONROE project site | https://www.monroe-project.eu | Returned HTTP 520; the data are reachable via the Zenodo records above instead. |
| NYU/other cellular traces, UNSW datasets | not located | No public direct download found in the time spent. |
| Barcelona open data portal | https://opendata.bcn.cat | HTTP 403 from the proxy. |

## 5. Citations

BibTeX entries were checked against Crossref (DOI, authors, venue, year) except where noted.

```bibtex
@inproceedings{raca2020beyond5g,
  author    = {Raca, Darijo and Leahy, Dylan and Sreenan, Cormac J. and Quinlan, Jason J.},
  title     = {Beyond Throughput, The Next Generation: A 5G Dataset with Channel and Context Metrics},
  booktitle = {Proceedings of the 11th ACM Multimedia Systems Conference (MMSys '20)},
  year      = {2020},
  pages     = {303--308},
  doi       = {10.1145/3339825.3394938}
}

@inproceedings{raca2018beyond4g,
  author    = {Raca, Darijo and Quinlan, Jason J. and Zahran, Ahmed H. and Sreenan, Cormac J.},
  title     = {Beyond Throughput: A 4G {LTE} Dataset with Channel and Context Metrics},
  booktitle = {Proceedings of the 9th ACM Multimedia Systems Conference (MMSys '18)},
  year      = {2018},
  pages     = {460--465},
  doi       = {10.1145/3204949.3208123}
}

@article{vanderhooft2016http2,
  author    = {van der Hooft, J. and Petrangeli, S. and Wauters, T. and Huysegems, R. and Rondao Alface, P. and Bostoen, T. and De Turck, F.},
  title     = {{HTTP/2}-Based Adaptive Streaming of {HEVC} Video over {4G/LTE} Networks},
  journal   = {IEEE Communications Letters},
  volume    = {20},
  number    = {11},
  pages     = {2177--2180},
  year      = {2016},
  doi       = {10.1109/LCOMM.2016.2601087}
}

@inproceedings{winstein2013sprout,
  author    = {Winstein, Keith and Sivaraman, Anirudh and Balakrishnan, Hari},
  title     = {Stochastic Forecasts Achieve High Throughput and Low Delay over Cellular Networks},
  booktitle = {10th USENIX Symposium on Networked Systems Design and Implementation (NSDI 13)},
  year      = {2013}
}

@inproceedings{narayanan2020lumos5g,
  author    = {Narayanan, Arvind and Ramadan, Eman and Mehta, Rishabh and Hu, Xinyue and Liu, Qingxu and Fezeu, Rostand A. K. and Dayalan, Udhaya Kumar and Verma, Saurabh and Ji, Peiqi and Li, Tao and Qian, Feng and Zhang, Zhi-Li},
  title     = {Lumos5G: Mapping and Predicting Commercial mmWave 5G Throughput},
  booktitle = {Proceedings of the ACM Internet Measurement Conference (IMC '20)},
  year      = {2020},
  pages     = {176--193},
  doi       = {10.1145/3419394.3423629}
}

@inproceedings{aceto2019mirage,
  author    = {Aceto, Giuseppe and Ciuonzo, Domenico and Montieri, Antonio and Persico, Valerio and Pescap{\`e}, Antonio},
  title     = {{MIRAGE}: Mobile-app Traffic Capture and Ground-truth Creation},
  booktitle = {2019 4th International Conference on Computing, Communications and Security (ICCCS)},
  year      = {2019},
  pages     = {1--8},
  doi       = {10.1109/CCCS.2019.8888137}
}

@inproceedings{drapergil2016vpn,
  author    = {Draper-Gil, Gerard and Lashkari, Arash Habibi and Mamun, Mohammad and Ghorbani, Ali A.},
  title     = {Characterization of Encrypted and {VPN} Traffic Using Time-Related Features},
  booktitle = {Proceedings of the 2nd International Conference on Information Systems Security and Privacy (ICISSP)},
  year      = {2016},
  pages     = {407--414},
  doi       = {10.5220/0005740704070414}
}

@inproceedings{khatouni2017monroe,
  author    = {Khatouni, Ali Safari and Mellia, Marco and Ajmone Marsan, Marco and Alfredsson, Stefan and Karlsson, Jonas and Brunstrom, Anna and others},
  title     = {Speedtest-Like Measurements in {3G/4G} Networks: The {MONROE} Experience},
  booktitle = {29th International Teletraffic Congress (ITC 29)},
  year      = {2017},
  pages     = {169--177},
  doi       = {10.23919/ITC.2017.8064353}
}

@incollection{cherian2026vca,
  author    = {Cherian, Nathaniel and Prasad, Akhil and Fahmy, Sonia},
  title     = {A Microscopic View of Congestion Control Behavior in Video Conferencing Applications},
  booktitle = {Passive and Active Measurement (PAM 2026), Lecture Notes in Computer Science},
  year      = {2026},
  pages     = {152--167},
  doi       = {10.1007/978-3-032-18268-5_7}
}

@inproceedings{rajiullah2023carlw,
  author    = {Rajiullah, Mohammad and Caso, Giuseppe and Brunstrom, Anna and Karlsson, Jonas and Alfredsson, Stefan and Alay, {\"O}zg{\"u} and others},
  title     = {{CARL-W}: a Testbed for Empirical Analyses of {5G} and Starlink Performance},
  booktitle = {Proceedings of the 3rd ACM Workshop on 5G and Beyond Network Measurements, Modeling, and Use Cases},
  year      = {2023},
  pages     = {1--7},
  doi       = {10.1145/3609382.3610510}
}

@inproceedings{rau2025vlc,
  author    = {Rau, Francisco and Herranz, Carlos and Val, I{\~n}aki and Georgieva, Petia and Perez, Joaquin},
  title     = {A Novel Flow-Based Online Network Traffic Classification Using Machine Learning},
  howpublished = {TechRxiv preprint},
  year      = {2025},
  doi       = {10.36227/techrxiv.175459507.75164419/v1},
  note      = {DOI as given in the dataset record; not independently resolved}
}

@misc{reymondin2021hanoi,
  author    = {Reymondin, Louis and Le, Trung Hieu and Vantalon, Thibaud and Pham, Huong and others},
  title     = {Free {WiFi} to monitor flow in Hanoian traditional markets},
  year      = {2021},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.5707312}
}
```

Venue pages for NSDI '13 were confirmed on the USENIX site (title only; page numbers not checked, hence omitted). The PAM 2026 entry is listed by Crossref as a Lecture Notes in Computer Science chapter; the dataset page cites it as PAM, March 2026. Datasets without an associated paper (Grand Paris Sud, Mesa, Canberra, Nantes, Bologna and the small aggregates) should be cited as web resources with publisher, title, URL and access date.

## 6. Suggested use in the simulation

- Arrivals and stay times: Grand Paris Sud (session level, 2026), Mesa (association level, three epochs), Canberra (campus); use Nantes and Bologna to validate the hourly and weekly profile and the Paris logs as the primary source.
- Demand per session: bytes in Grand Paris Sud and Mesa (both directions); Canberra gives rate times duration.
- Class mix: only partial. `type_site` and `device_type` (Grand Paris Sud) and `os_type` (Mesa) are venue and device labels, not application labels. Per-application rates come from the VLC sample and the Purdue sample (real-time) and the 5G Netflix/Prime traces (video). Larger labelled flow sets (MIRAGE, ISCX) need a download of more than 1.4 GB or a registration.
- Capacity: pool Ghent, Raca 4G, Raca 5G, NordicDat, CoMMECT and the Mahimahi traces with the HSDPA logs; Lumos5G and FCC data were not reachable.
