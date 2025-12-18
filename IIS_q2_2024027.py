import pandas as pd
from pyDatalog import pyDatalog

pyDatalog.clear()
pyDatalog.create_terms(
'RouteHasStop, TripFare, DirectRoute, Transfer1Route, Transfer2Route, AvoidStopRoute, X, Y, Z, Z1, Z2, R, R1, R2, R3, P, P1, P2, P3, AvoidStop'
)

def create_mappings():
    """
    Task 1: Data Preparation (3 Marks)
    Create route-to-stops and fares mappings from GTFS data
    
    Returns:
    - route_to_stops: Dictionary mapping route_id to ordered list of stop_ids
    - fares: Dictionary mapping (route_id, origin_id, dest_id) to price
    """
    # TODO: Read and merge trip data (stop_times.txt and trips.txt)
    
    df_trips = pd.merge(
        pd.read_csv('./GTFS/stop_times.txt'),
        pd.read_csv('./GTFS/trips.txt'),
        on='trip_id'
    )[['trip_id', 'route_id', 'stop_id', 'stop_sequence']]
    
    # TODO: Read and merge fare data (fare_rules.txt and fare_attributes.txt)
    df_fare = pd.merge(
        pd.read_csv('./GTFS/fare_rules.txt'),
        pd.read_csv('./GTFS/fare_attributes.txt'),
        on='fare_id'
    )[['route_id','origin_id','destination_id','price']]
    
    # TODO: Create route_to_stops dictionary with ordered stops
    route_to_stops = {}
    for _, row in df_trips.iterrows():
        route_id=int(row['route_id'])
        stop_id= int(row['stop_id'])
        stop_sequence=int(row['stop_sequence'])
        if route_id not in route_to_stops:
            route_to_stops[route_id] = []
        route_to_stops[route_id].append((stop_sequence,stop_id))
    

    for route_id in route_to_stops:
        route_to_stops[route_id].sort()
        route_to_stops[route_id] = [stop_id for _, stop_id in route_to_stops[route_id]]
    
    # TODO: Create fares dictionary
    fares = {}
    for _, row in df_fare.iterrows():
        route = int(row['route_id'])
        origin = int(row['origin_id'])
        destination= int(row['destination_id'])
        price = float(row['price'])
        fares[(route, origin, destination)] = price
    
    return route_to_stops, fares

def setup_datalog(route_to_stops, fares):
    """
    Task 2: pyDatalog Knowledge Base Setup (2 Marks)
    Setup pyDatalog knowledge base with terms and facts
    """
 
    # TODO: Add facts for routes and stops
    for route, stops in route_to_stops.items():
        for stop in stops:
            +RouteHasStop(route, stop)
    
    # TODO: Add facts for fares
    for (route, origin, dest), price in fares.items():
        +TripFare(route, origin, dest, price)

def define_rules():
    """
    Task 3: Rule Implementation (4 Marks)
    Define pyDatalog rules for route finding
    
    Required Rules:
    1. DirectRoute(X, Y, R, P): Direct route R from X to Y with fare P
    2. Transfer1Route(X, Y, R1, Z, R2, P): 1-transfer route via Z using R1, R2 with fare P
    3. Transfer2Route(X, Y, R1, Z1, R2, Z2, R3, P): 2-transfer route via Z1, Z2 with fare P
    4. AvoidStopRoute(X, Y, AvoidStop, R, P): Direct route avoiding specific stop
    """
    # TODO: Implement DirectRoute rule
    DirectRoute(X, Y, R, P) <= (
        TripFare(R, X, Y, P) & (X!=Y)
    )
    
    # TODO: Implement Transfer1Route rule
    Transfer1Route(X, Y, R1, Z, R2, P) <= ( 
         TripFare(R1, X, Z, P1) & TripFare(R2, Z, Y, P2) & 
        (P == P1 + P2) & (R1 != R2)
    )
    
    # TODO: Implement Transfer2Route rule
    Transfer2Route(X, Y, R1, Z1, R2, Z2, R3, P) <= (
        TripFare(R1, X, Z1, P1) & TripFare(R2, Z1, Z2, P2) & 
        TripFare(R3, Z2, Y, P3) & 
        (P == P1 + P2 + P3) & (R1 != R2) & (R1 != R3) & (R2 != R3)
    )
    
    # TODO: Implement AvoidStopRoute rule
    AvoidStopRoute(X, Y, AvoidStop, R, P) <= (
       DirectRoute(X,Y,R,P)&~RouteHasStop(R,AvoidStop)
    )

def query_routes(start_stop, end_stop, avoid_stop=None):
    """
    Task 4: Query Execution (1 Mark)
    Execute queries and return results in required format
    """
    results = {
        'direct_routes': [],
        'one_transfer': [],
        'two_transfer': [],
        'avoid_stop': []
    }
    
    # TODO: Implement queries and format results
    # Remember to return at most 5 results per category, sorted by fare in descending order
    direct_routes = DirectRoute(start_stop, end_stop, R, P).data
    results['direct_routes'] = sorted(direct_routes, key=lambda x: x[-1], reverse=True)[:5]
    
    one_transfer_routes = Transfer1Route(start_stop, end_stop, R1, Z, R2, P).data
    results['one_transfer'] = sorted(one_transfer_routes, key=lambda x: x[-1], reverse=True)[:5]

    two_transfer_routes = Transfer2Route(start_stop, end_stop, R1, Z1, R2, Z2, R3, P).data
    results['two_transfer'] = sorted(two_transfer_routes, key=lambda x: x[-1], reverse=True)[:5]
    
    if avoid_stop:
        avoid_stop_routes = AvoidStopRoute(start_stop, end_stop, avoid_stop, R, P).data
        results['avoid_stop'] = sorted(avoid_stop_routes, key=lambda x: x[-1], reverse=True)[:5]

    return results

def main():
    # Create data mappings
    route_to_stops, fares = create_mappings()
    
    # Setup pyDatalog
    setup_datalog(route_to_stops, fares)
    
    # Define rules
    define_rules()
    
    # Example usage
    results = query_routes(146, 148, avoid_stop=233)
    
    # Print results
    print("Direct routes:", results['direct_routes'])
    print("1-transfer:", results['one_transfer'])
    print("2-transfer:", results['two_transfer'])
    print("Avoid Stop:", results['avoid_stop'])

if __name__ == "__main__":
    
    main()


#################### PUBLIC TEST CASES ###########################

# Test Case 1: query_routes(146, 148, avoid_stop=233)

# Direct routes: [(2044, 5.0), (1319, 5.0), (10595, 5.0), (1180, 5.0), (687, 5.0)]
# 1-transfer: [(2044, 488, 955, 10.0), (2044, 488, 1700, 10.0), (2044, 488, 10601, 10.0), (2044, 488, 10634, 10.0), (2044, 488, 1401, 10.0)]
# 2-transfer: [(10486, 2032, 10643, 488, 955, 15.0), (10486, 2032, 10643, 488, 1700, 15.0), (10486, 2032, 10643, 488, 10601, 15.0), (10486, 2032, 10643, 488, 10634, 15.0), (10486, 2032, 10643, 488, 1401, 15.0)]
# Avoid Stop: [(2044, 5.0), (1319, 5.0), (10595, 5.0), (1180, 5.0), (687, 5.0)]

# Test Case 2: query_routes(2161, 3569, avoid_stop=2162)

# Direct routes: [(149, 5.0), (10596, 5.0), (1249, 5.0), (456, 5.0), (10016, 5.0)]
# 1-transfer: [(149, 2162, 10006, 10.0), (149, 2162, 10643, 10.0), (149, 2162, 456, 10.0), (149, 2162, 10016, 10.0), (149, 2162, 320, 10.0)]
# 2-transfer: [(142, 2171, 674, 148, 1851, 30.0), (142, 2171, 674, 149, 1851, 30.0), (1851, 2171, 674, 149, 10006, 35.0), (1851, 2171, 674, 149, 456, 35.0), (1851, 2171, 674, 149, 10526, 35.0)]
# Avoid Stop: []

##################################################################