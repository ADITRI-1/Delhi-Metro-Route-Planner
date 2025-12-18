# Delhi-Metro-Route-Planner(pyDatalog + GTFS)
This repository implements a Delhi Metro Route Plannar using pyDatalog and GTFS data. it supports direct, 1- transfer, 2- transfer route discovery , fare-based sorting , stop avoidance and constrainted query outputs , emphasizing logical reasoning and rule-based inference.

### Overview

This project implements a Delhi Metro route planner using GTFS transit data and a pyDatalog-based knowledge base. It supports:

* Finding direct routes between two stops

* Discovering routes with 1 transfer and 2 transfers

* Finding direct routes that avoid a specific stop

* Returning results sorted by fare (ascending)

* Limiting results to at most 5 entries per category

#### Tech Stack

* Python

* Pandas (for GTFS preprocessing)

* pyDatalog (for knowledge base + logical rules)

* Dataset (GTFS Files)

The project uses GTFS files provided in pyDatalog DataFolder:
https://drive.google.com/drive/folders/1miaGaoy_qrkuapK6_adxAPJHrvQ98JGe

* routes.txt — route_id, route_long_name

* trips.txt — maps trip_id → route_id

* stop_times.txt — trip_id, stop_id, arrival_time, departure_time

* stops.txt — stop_id, stop_name, coordinates

* fare_rules.txt — route_id, origin_id, destination_id, fare_id

* fare_attributes.txt — fare_id, price, currency, etc. (used for merging fares)

#### Notes

* Times may exceed 24 hours (e.g., 25:30 is valid); time parsing is not required for route connectivity.

* All IDs must be treated as integers.

* Output for each query category must be sorted by fare and limited to 5 results.

### A. Core Data Structures
#### 1) route_to_stops
  * A dictionary mapping each route_id to an ordered list of stop_ids.
    Example:
route_to_stops = {
  142: [146, 148, 233, 3569],
  10001: [146, 915, 2170]
}

#### 2) fares
* A dictionary mapping (route_id, origin_id, destination_id) → price.

Example:

fares = {
  (142, 146, 148): 5.0,
  (142, 146, 149): 5.0
}

### B. Knowledge Base (pyDatalog)
#### Facts

The system stores GTFS-derived facts in pyDatalog:

* RouteHasStop(route_id, stop_id)

* TripFare(route_id, origin_id, dest_id, fare)

These are used to infer valid routes and total fares across transfers.

#### Terms

All fact variables, intermediate variables, and rule predicates are created using:

pyDatalog.create_terms(...)

### C. Supported Queries & Rules
#### 1) Direct Routes

##### Rule: DirectRoute(X, Y, R, P)
True if route R connects stop X to stop Y directly, with fare P.

##### Output format (max 5, sorted by fare):

[(route_id, fare), ...]

#### 2) 1-Transfer Routes

##### Rule: Transfer1Route(X, Y, R1, Z, R2, P)
Finds routes from X to Y using exactly one transfer stop Z with routes R1 and R2.

##### Constraints:

R1 and R2 must be different.

Total fare P = fare(R1) + fare(R2) (computed from available fare mappings)

##### Output format (max 5, sorted by fare):

[(route1_id, transfer_stop_id, route2_id, total_fare), ...]

#### 3) 2-Transfer Routes

##### Rule: Transfer2Route(X, Y, R1, Z1, R2, Z2, R3, P)
Finds routes from X to Y using two transfer stops Z1 and Z2 with three distinct routes.

##### Constraints:

R1, R2, and R3 must all be different.

Total fare is the sum of the three route segments’ fares.

##### Output format (max 5, sorted by fare):

[(route1_id, transfer_stop_id1, route2_id, transfer_stop_id2, route3_id, total_fare), ...]

#### 4) Avoid a Specific Stop (Direct Only)

##### Rule: AvoidStopRoute(X, Y, AvoidStop, R, P)
Finds direct routes from X to Y on route R such that the route does not include AvoidStop.

##### Output format (max 5, sorted by fare):

[(route_id, fare), ...]

### D. Output Requirements

All query functions must:

* Accept stop IDs as integers

* Return results in the exact required tuple formats

* Sort results by fare ascending

* Return at most 5 results per category

##### Example expected-style outputs:

Direct routes: [(142, 8.0), (143, 12.0), (144, 15.0)]
1-transfer: [(142, 10001, 233, 20.0), (145, 10002, 234, 25.0)]
2-transfer: [(142, 10001, 146, 20002, 148, 35.0)]
Avoid Stop: [(142, 12.0), (143, 15.0)]

## Project Structure :-
pyDatalog DataFolder/
  routes.txt
  trips.txt
  stop_times.txt
  stops.txt
  fare_rules.txt
  fare_attributes.txt

metro_route_planner.py   # main submission file with preprocessing + KB + queries
README.md

## How to Run

* Place GTFS files in the expected folder structure.

* Run the script:

* python metro_route_planner.py

### Deliverables

The Python file contains:

* Functions to build route_to_stops and fares

* pyDatalog knowledge base setup (terms + facts)

* Rule definitions (Direct / 1-transfer / 2-transfer / avoid-stop)

* Query functions that return results in the required format

