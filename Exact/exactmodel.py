import problem_class as pc
import solution_class
from gurobipy import *
import matplotlib.pyplot as plt
import numpy as np
import json

def ReadInFile(filename="instance.json"):
    p=pc.Problem(filename)
    p.read_problem_instance()
    return p

def GetFacilities():
    noclients=p.getNODepot()-1
    facilities=[]
    for i in range(p.getNOsuppliers()):
        facilities.append(p.getSupplier(i))
    for i in range(p.getNOHubs()):
        facilities.append(p.getHub(i))
    for i in range(p.getNODepot()):
        facilities.append(p.getDepot(i))
    return facilities

def laats():
    lats=[]
    longs=[]
    for i in range(len(facilities)):
        lats.append(facilities[i].getLATITUDE())
        longs.append(facilities[i].getLONGITUDE())
    return lats,longs

def GetDistance():
    distance=[]
    for i in facilities:
        distancei=[]
        for j in facilities[:p.getNOsuppliers()]:
            distancei.append(p.getDistance(i.getID(), j.getID()))
        for j in facilities[p.getNOsuppliers():p.getNOsuppliers()+p.getNOHubs()]:
            if i in facilities[p.getNOsuppliers():p.getNOsuppliers()+p.getNOHubs()]:
                distancei.append(10000000000)
            else:
                distancei.append(p.getDistance(i.getID(), j.getID()))
        for j in facilities[p.getNOsuppliers()+p.getNOHubs():]:
            distancei.append(p.getDistance(i.getID(), j.getID()))
        distance.append(distancei)
    d=np.array(distance)
    return d

def GetTime():
    time=[]
    for i in facilities:
        timei=[]
        for j in facilities[:p.getNOsuppliers()]:
            timei.append(p.getTime(i.getID(), j.getID()))
        for j in facilities[p.getNOsuppliers():p.getNOsuppliers()+p.getNOHubs()]:
            if i in facilities[p.getNOsuppliers():p.getNOsuppliers()+p.getNOHubs()]:
                timei.append(10000000000)
            else:
                timei.append(p.getTime(i.getID(), j.getID()))
        for j in facilities[p.getNOsuppliers()+p.getNOHubs():]:
            timei.append(p.getTime(i.getID(), j.getID()))
        time.append(timei)
    t=np.array(time)
    return t

def GetDemand():
    demand=[]
    for i in range(0,p.getNODemand(),p.getNOProductTypes()): 
        if p.getDemand(i).getQUANTITY()>0:
            demand.append(p.getDemand(i).getQUANTITY())
        else:
            demand.append(0)
    return demand

def GetSupply():
    supply=[]
    for i in range(0,p.getNOSupplierCapacities(),p.getNOProductTypes()): 
        supply.append(p.getSupplierCapacity(i).getQUANTITY())
    return supply

def GetVehicles():    
    vehicles=[]
    for i in range(p.getNOVehicles()):
        for j in range(1000):
            vehicles.append(p.getVehicle(i).getCAPACITY())
    return vehicles

def GetNewHubIndices():    
    newhubindices=[]
    for i in range(p.getNOsuppliers(),p.getNOsuppliers()+p.getNOHubs()):
        if facilities[i].getExisting()==False:
            newhubindices.append(i)
    return newhubindices

def ConstructModel():
    m=Model()
    X=m.addVars(len(facilities),len(facilities),len(vehicles),vtype="B")
    Z=m.addVars(p.getNOHubs(),vtype="b")
    f=m.addVars(len(facilities),len(facilities),len(vehicles),vtype="I")
    r=m.addVars(p.getNOsuppliers(),len(vehicles),vtype="I")
    q=m.addVars(p.getNODepot(),len(vehicles),vtype="I")
    XD=m.addVars(len(vehicles),vtype="b")
    XH=m.addVars(len(vehicles),vtype="b")
    XS=m.addVars(len(vehicles),vtype="b")
    m.addConstrs((quicksum(r[i,k] for k in range(len(vehicles)))<=supply[i] for i in range(p.getNOsuppliers())),name="c-1")
    m.addConstrs((quicksum(quicksum(X[i,j,k] for i in range(p.getNOsuppliers(),p.getNOHubs()+p.getNOsuppliers()))for j in range(len(facilities)))<=1  for k in range(len(vehicles))),name="C0")
    m.addConstrs((Z[i-p.getNOsuppliers()]*MC-quicksum(quicksum(f[i,j,k] for j in range(p.getNOHubs()+p.getNOsuppliers(),len(facilities)))for k in range(len(vehicles)))<=0 for i in newhubindices),name="C1")
    m.addConstr(quicksum(Z[i-p.getNOsuppliers()] for i in newhubindices)<=MH,name="C2")
    m.addConstrs((f[i,j,k]<=vehicles[k]*X[i,j,k] for i in range(len(facilities)) for j in range(len(facilities)) for k in range(len(vehicles))),name="C3")
    m.addConstrs((quicksum(q[i,k] for k in range(len(vehicles)))==demand[i] for i in range(p.getNODepot())),name="C4")
    m.addConstrs((quicksum(f[i,j,k] for j in range(len(facilities)))==quicksum(f[l,i,k] for l in range(len(facilities)))-q[i-p.getNOHubs()-p.getNOsuppliers(),k] for i in range(p.getNOHubs()+p.getNOsuppliers(),len(facilities)) for k in range(len(vehicles))),name="C5")
    m.addConstrs((quicksum(f[i,j,k] for j in range(len(facilities)))==quicksum(f[l,i,k] for l in range(len(facilities)))+r[i,k] for i in range(p.getNOsuppliers()) for k in range(len(vehicles))),name="C6")
    m.addConstrs((quicksum(quicksum(f[j,i,k] for k in range(len(vehicles)))for j in range(len(facilities)))==quicksum(quicksum(f[i,j,k] for k in range(len(vehicles)))for j in range(len(facilities)))for i in range(p.getNOsuppliers(),p.getNOHubs()+p.getNOsuppliers())),name="C7")
    m.addConstrs((quicksum(quicksum(t[i,j]*X[i,j,k] for i in range(len(facilities)))for j in range(len(facilities)))<=MD for k in range(len(vehicles))),name="C8")
    m.addConstrs((quicksum(X[i,j,k] for i in range(len(facilities)))-quicksum(X[j,i,k] for i in range(len(facilities)))==0 for j in range(len(facilities)) for k in range(len(vehicles))),name="C9")
    m.addConstr(quicksum(quicksum(r[i,k]for i in range(p.getNOsuppliers()))for k in range(len(vehicles)))==quicksum(demand[i]for i in range(p.getNODepot())),name="C10")
    m.addConstrs((quicksum(X[i,j,k] for i in range(p.getNOsuppliers()))<=B*Z[j-p.getNOsuppliers()] for j in newhubindices for k in range(len(vehicles))),name="C11")
    m.addConstrs((quicksum(X[i,j,k] for i in range(len(facilities)))<=1 for j in range(len(facilities)) for k in range(len(vehicles))),name="C12")
    m.addConstrs((quicksum(quicksum(X[i,j,k] for i in range(p.getNOHubs()+p.getNOsuppliers(),len(facilities)))for j in range(len(facilities)))<=B*XD[k] for k in range(len(vehicles))),name="C12")    
    m.addConstrs((quicksum(quicksum(X[i,j,k] for i in range(p.getNOsuppliers(),p.getNOHubs()+p.getNOsuppliers()))for j in range(len(facilities)))<=B*XH[k] for k in range(len(vehicles))),name="C13")
    m.addConstrs((quicksum(quicksum(X[i,j,k] for i in range(p.getNOsuppliers()))for j in range(len(facilities)))<=B*XS[k] for k in range(len(vehicles))),name="C14")    
    m.addConstrs((XD[k]+XH[k]+XS[k]==2 for k in range(len(vehicles))),name="C15")
    m.addConstrs((X[i,i,k]==0 for i in range(len(facilities)) for k in range(len(vehicles))),name="C16")
    m.addConstrs((f[i,j,k]>=0 for i in range(len(facilities)) for j in range(len(facilities)) for k in range(len(vehicles))),name="C17")
    m.addConstrs((q[i,k]>=0 for i in range(p.getNODepot()) for k in range(len(vehicles))),name="C18")
    m.addConstrs((r[i,k]>=0 for i in range(p.getNOsuppliers()) for k in range(len(vehicles))),name="C19") 
    m.setObjective(quicksum(quicksum(quicksum(d[i,j]*X[i,j,k]for i in range(len(facilities))) for j in range(len(facilities)))for k in range(len(vehicles))), GRB.MINIMIZE)
    return m,X,f,Z

def SolveModel(m,X,f,Z,pasttime):
    m.Params.timelimit=3*3600.0-pasttime
    m.optimize()
    if m.Status == GRB.INFEASIBLE:
        m.computeIIS()
        m.write("iismodel.ilp")
    x_vals=m.getAttr("X",X)
    f_vals=m.getAttr("X",f)
    Z_vals=m.getAttr("X",Z)
    obj=m.getObjective().getValue()
    runtime=m.Runtime
    return x_vals,f_vals,Z_vals,obj,runtime

def plot():
    name=file.split(".")[0]
    plt.scatter(lats[:p.getNOsuppliers()],longs[:p.getNOsuppliers()],c="#9bddff",marker="d")
    plt.scatter(lats[p.getNOsuppliers():p.getNOsuppliers()+p.getNOHubs()],longs[p.getNOsuppliers():p.getNOsuppliers()+p.getNOHubs()],c="#967bb6")
    for i in newhubindices:
        plt.scatter(lats[i],longs[i],c="#993366")
    plt.scatter(lats[p.getNOsuppliers()+p.getNOHubs():],longs[p.getNOsuppliers()+p.getNOHubs():],c="#ffb7c5",marker="s")
    vehiclesused=[]
    for i in f_vals:
        if f_vals[i]>=1:
            if i[2] not in vehiclesused:
                vehiclesused.append(i[2])
    for i in x_vals:
        if x_vals[i]>0:
            print(i)
            plt.plot([lats[i[0]],lats[i[1]]],[longs[i[0]],longs[i[1]]])
    plt.title(name+str(obj))
    plt.savefig(name+".png")
    
def find_subtour(edges):
    vertices=[]
    for i in edges:
        if i[0] not in vertices:
            vertices.append(i[0])
        if i[1] not in vertices:
            vertices.append(i[1])  
    n=len(vertices)
    unvisited = vertices
    cycle = vertices+[-10]  # initial length has 1 more city
    while unvisited:  # true if list is non-empty
        thiscycle = []
        current = unvisited[0]
        prev=-1
        while True:
            print(current)
            unvisited.remove(current)
            for i,j,k in edges:
                if (i == current) and (j != prev):
                    _next = j
                    thiscycle.append((i,j,k))
                    break
                elif (j == current) and (i != prev):
                    _next = i
                    thiscycle.append((i,j,k))
                    break
                elif (i == current) and (j == prev):
                    _next = i
                    thiscycle.append((i,j,k))
                    break
            if _next in unvisited:
                print(i,j)
                prev = current
                current = _next
            else:
                break
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    if len(cycle)<n:
        return cycle
    else:
        return []
    
def run(files=[],MC=8,MHs=[2 for i in range(len(files))],MDs=[28800 for i in range(len(files))]):
    B=1000000000000000
    obj_vals={}
    for file in range(len(files)):
        p=ReadInFile(files[file])
        MH=MHs[file]
        MD=MDs[file]
        facilities=GetFacilities()
        d=GetDistance()
        t=GetTime()
        demand=GetDemand()
        supply=GetSupply()
        lats,longs=laats()
        vehicles=GetVehicles()
        newhubindices=GetNewHubIndices()
        m,X,f,Z=ConstructModel()
        pasttime=0
    
        while 3*3600-pasttime>0:
            x_vals,f_vals,Z_vals,obj,runtime=SolveModel(m,X,f,Z,pasttime)
            pasttime+=runtime
            vehicles={}
            for i in x_vals:
                if x_vals[i]>0:
                if x_vals[i]>0.5:
                    
                    if i[2] in vehicles:
                        vehicles[i[2]].append(i)
                    else:
                        vehicles[i[2]]=[i] 
            constraints_added=0
            for i in vehicles:
                st=find_subtour(vehicles[i])
                if len(st) > 0:
                    constraints_added+=1
                    m.addConstr(quicksum(X[e] for e in st) <= len(st) - 1)
            if constraints_added==0:
                break
        if m.Status==17:
            obj_vals[[files[file]]]={"end":"memory issue","runtime":runtime}
        elif m.Status==9:
            try:
                bound=m.ObjBound
            except:
                bound="na"
            try:
                gap=m.MIPGap
            except:
                gap="na"
            try:
                ob=obj
            except:
                ob="na"
            obj_vals[files[file]]={"obj":ob,"bound":bound,"gap":gap,"runtime":runtime}
            
                
        else:
            obj_vals[files[file]]={"obj":obj,"runtime":runtime}
    return obj_vals


	
