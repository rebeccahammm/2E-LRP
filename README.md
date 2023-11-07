# 2E-LRP

##Instances
The sizes of the instances are the following:
| Instances |  No. Hubs  | No. Suppliers | No. New Hubs | No. Old Hubs|
|:-----|:--------:|------:|:--------:|------:|
|HaK-n10  |5 | 3|1 |1 |
| HaK-n11- v0-v3   |  5 |   3|1 | 2 |
|Hak-n72- v0 -v4  | 6 |   34 |17| 15 |
|Hak-n220- v0 -v4  | 56 |   54 |53 | 57 |
|Hak-n261- v0 -v4  |7 |   200 |6 | 48 |
|Hak-n51- v0 -v4  |6 |    20 |5 | 20 |

## simulating_data.py- 

This file is used to simulate instances of this specific Location-routing problem.
    Uses OSM data which can be found here: https://download.geofabrik.de/ and convert to a pygerc file using https://github.com/AndGem/OsmToRoadGraph. To generate instances we can use the following functions:
    
    
    
    instance_generation(seed,osm_file, sup_range,dep_range, oh_range,nh_range, pt_range,vt_range,instype,distype,key="") 
    
generates one instance with given ranges for size. Ranges are given in list format. 
- sup_range= number of supplier range
- dep_range= number of depot range
- oh_range= number of old hub range
- nh_range= number of new hub range
- pt_range= number of product type range
- vt_range= number of vehicle type range
Instype 
- if equal 1: creates instances where demands are less then supplier capacities and vehicle capcity chosen from 3 options
- if equal 2: creates instances where demands are less then supplier capacities and vehicle capcity chosen from intergers in range
- if equal 3: creates instances where supplier capacities are less then demands and vehicle capcity chosen from intergers in range

Distype 
- if equal 1: calculates distances and times using google directions api. API key needed: (https://developers.google.com/maps/documentation/directions) 
- if equal 2: calculates distances using pandana package. pandana will need to be installed first. Times estimated as factor of time with randomised speed.

Key: API key needed for distype 1. If using distype 2 can be left blank.
    
    generating_multiple(num_of,seed,sup_range,dep_range, oh_range,nh_range, pt_range,vt_range,ins_types,dist_types,osm_file,key="")
generates num_of different instances with same stated characteristics and saves them into json files.

## problem_class.py-
This file defines the Problem class. To read a instance file into a problem class you must run the following code:
   
    prob=Problem(file_name)
    prob.read_problem_instance()
