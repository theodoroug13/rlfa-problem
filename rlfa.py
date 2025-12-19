
#Για διορθωτές: έχω βάλει σε comments "[αριθμός screenshot]"" σε σημεία του κώδικα για να εξηγήσω
#που βασίστηκα για τη λογική πίσω από κάποια κομμάτια κώδικα. Τα screenshots βρίσκονται σε αντίστοιχο README της άσκησης

import sys
import time
from csp import CSP,backtracking_search,forward_checking,mac,mrv, min_conflicts


class TimeoutException(Exception):
    pass

class RLFA(CSP):
    def __init__(self,variables,neighbors, domain, constraints,time_limit=60):
        self.constraints_map=constraints
        self.checks=0
        #[1]
        self.constraint_weights={}
        for(var1,var2) in constraints:
            self.constraint_weights[(var1,var2)]=1

        self.time_limit = time_limit
        self.start_time = None # Θα τεθεί όταν ξεκινήσει η αναζήτηση
        
        super().__init__(variables, domain,neighbors,self.valid)
    
    #constraint function όπως το περιγράφει στο CSP class
    def valid(self,var1, value1, var2, value2):
        self.checks+=1
        if self.checks % 1000 == 0 and self.start_time is not None:
            if time.time() - self.start_time > self.time_limit:
                raise TimeoutException() 
        diff =abs(value1-value2)

        if (var1,var2) in self.constraints_map:
            operator,k= self.constraints_map[(var1, var2)]
        elif(var2,var1) in self.constraints_map:
            operator,k= self.constraints_map[(var2,var1)]
        else:
            return True
        
        if operator== '>':
            return diff > k
        elif operator== '=':
            return diff== k
        elif operator== '<':
            return diff<k
        
        return True

    def get_constraint_weight(self, var1, var2):
        if(var1, var2)in self.constraint_weights:
            return self.constraint_weights[(var1, var2)]
        elif (var2, var1) in self.constraint_weights:
            return self.constraint_weights[(var2, var1)] 

    def increase_weight(self, var1, var2):
        if(var1, var2 )in self.constraint_weights:
            self.constraint_weights[(var1, var2)]+=1
        elif( var2, var1)in self.constraint_weights:
            self.constraint_weights[(var2, var1)]+=1


def parse_files( var_file, dom_file, ctr_file):    

        domain_values={}
        with open(dom_file,'r') as file:
            lines= file.readlines()
            for line in lines[1:]:
                parts=list(map(int, line.split()))
                dom_id=parts[0]
                values=parts[2:]
                domain_values[dom_id]=values




        variables=[]
        domains={}
        with open(var_file,'r') as file:
            lines= file.readlines()
            for line in lines[1:]:
                parts= list(map(int,line.split()))
                var_id=parts[0]
                dom_id=parts[1]
                variables.append(var_id)

                if dom_id in domain_values:
                    domains[var_id]=domain_values[dom_id]
                else:
                    print("domain id not found")
        
        neighbors={v:[]for v in variables}
        constraints={}


        with open(ctr_file,'r') as file:
            lines=file.readlines()
            #αγνοώ τη πρώτη γραμμή
            for line in lines[1:]:
                parts=line.split() 
                var1=int(parts[0])
                var2= int(parts[1])
                operator=parts[2]
                k=int (parts[3])

                constraints[(var1,var2)]= (operator,k)
                if var2 not in neighbors[var1]: 
                    neighbors[var1].append(var2)
                if var1 not in neighbors[var2]:
                    neighbors[var2].append(var1)
        return variables, domains, neighbors,constraints
    

def wdeg_heuristic(assignment, csp: RLFA):      #βάζω το :RLFA απλά για να μου βγάζει τα πεδία την κλασης RLFA όταν πατάω csp. * για συντομία
    min_var= None
    min_ratio=float('inf')

    unassigned_vars= [v for v in csp.variables if v not in assignment]
    for var in unassigned_vars:
        if (csp.curr_domains is not None and var in csp.curr_domains):
            dom_size=len(csp.curr_domains[var])
        else:
            dom_size=len(csp.domains[var])

        var_weight_degree=0
        #[4]
        for neighbor in csp.neighbors[var]:
            #[2] 
            if neighbor not in assignment:
                var_weight_degree+=csp.get_constraint_weight(var,neighbor)
        if var_weight_degree==0:
            var_weight_degree=0.001 # αν η μεταβλητή είναι μονη της(τελευταια, χωρις γείτονες unassigned) να μην γίνει δαίρεση με 0
    
        ratio= dom_size/var_weight_degree
        #[3]
        if ratio<min_ratio:
            min_ratio=ratio
            min_var=var
    return min_var

#προσαρμοσμένη πάνω στην revise του aima
def wdeg_revise(csp:RLFA, Xi, Xj, removals):
    revised= False
    
    for x in csp.curr_domains[Xi][:]:
        # If Xi=x conflicts with Xj=y for every possible y, eliminate Xi=x
        # if all(not csp.constraints(Xi, x, Xj, y) for y in csp.curr_domains[Xj]):
        conflict = True
        for y in csp.curr_domains[Xj]:
            if csp.constraints(Xi, x, Xj, y):
                conflict = False
            if not conflict:
                break
        if conflict:
            csp.prune(Xi, x, removals)
            revised = True

    #[5]
    if not csp.curr_domains[Xi]:
        csp.increase_weight(Xi,Xj)

    return revised


def wdeg_AC3(csp:RLFA, queue= None,removals=None):
    if queue is None:
        queue = {(Xi, Xk) for Xi in csp.variables for Xk in csp.neighbors[Xi]}
    csp.support_pruning()
    queue=list(queue)
    while queue:
        (Xi, Xj) = queue.pop()
        revised=wdeg_revise(csp, Xi, Xj, removals)
        if revised:
            #[5], [6]
            if not csp.curr_domains[Xi]:
                return False 
            for Xk in csp.neighbors[Xi]:
                if Xk != Xj:
                    queue.append((Xk, Xi))
    return True
def wdeg_mac(csp, var, value, assignment, removals):
    """Maintain arc consistency."""
    return wdeg_AC3(csp, {(X, var) for X in csp.neighbors[var]}, removals)


def fc_cbj(csp:RLFA):
    conf_set={v:set() for v in csp.variables}
    if csp.curr_domains is None:
        csp.curr_domains= {v: list(csp.domains[v]) for v in csp.variables}
    return recursive_fc_cbj(csp,{}, conf_set)


def recursive_fc_cbj(csp:RLFA,assignment, conf_set):
    if len(assignment) == len(csp.variables):
        return assignment, None

    var = wdeg_heuristic(assignment, csp) 
    ass_keys = list(assignment.keys())

    ## το πήρα σχεδόν ίδιο απο backtracking search
    for value in csp.curr_domains[var]:
        if csp.nconflicts(var, value, assignment) == 0:
            csp.assign(var, value, assignment)
            removals = []
            dwo_var = None 
            
            for neighbor in csp.neighbors[var]:
                if neighbor not in assignment:
                    for n_val in csp.curr_domains[neighbor][:]:
                        if not csp.constraints(var,value, neighbor , n_val):
                            csp.prune(neighbor, n_val,removals)
                    
                    if not csp.curr_domains[neighbor]:
                        dwo_var =neighbor
                        csp.increase_weight(var, neighbor)
                        break
            if dwo_var:
                conflict_causes={v for v in csp.neighbors[dwo_var] if v in assignment}
                conflict_causes.add(var)
                conf_set[var].update(conflict_causes)
                
                csp.restore(removals)
                csp.unassign(var, assignment)
                continue       

            result, jump_target=recursive_fc_cbj(csp,assignment,conf_set)
            if result is not None:
                return result,None
            
            if jump_target is not None and jump_target != var:
                csp.restore(removals)
                csp.unassign(var, assignment)
                return None, jump_target
            csp.restore(removals)
            csp.unassign(var, assignment)
    if not conf_set[var]: 
        return  None, None
    candidates=[v for v in conf_set[var] if v in assignment]
    if not candidates:
        return None, None
    target=max(candidates, key=lambda x: ass_keys.index(x))

    conf_set[target].update(conf_set[var])
    if target in conf_set[target]:
        conf_set[target].remove(target)
    conf_set[var].clear()
    return None, target

if __name__ == "__main__":
    var_file = 'rlfap/var2-f25.txt'
    dom_file = 'rlfap/dom2-f25.txt'
    ctr_file = 'rlfap/ctr2-f25.txt'
    vars_list, doms_dict, neighs_dict, ctr_map= parse_files(var_file, dom_file, ctr_file)    
    results = []
    
    LIMIT = 60

    print("1. Εκτέλεση FC + MRV...")
    p1 = RLFA(vars_list, neighs_dict, doms_dict, ctr_map, time_limit=LIMIT)
    p1.start_time = time.time() # <--- Ξεκινάμε το χρονόμετρο
    t0 = time.time()
    
    try:
        sol1 =backtracking_search(p1, select_unassigned_variable=mrv, inference=forward_checking)
        solved_str =bool(sol1)
        time_taken= time.time() - t0
    except TimeoutException:
        print("TIMEOUT")
        sol1 = None
        solved_str = "TIMEOUT"
        time_taken = LIMIT
        
    results.append({"Alg": "FC + MRV", "Time": time_taken, "Assigns": p1.nassigns,"Checks": p1.checks, "Solved": solved_str})



    print("2. Εκτέλεση MAC + dom/wdeg...")
    p2= RLFA(vars_list, neighs_dict, doms_dict, ctr_map, time_limit=LIMIT)
    p2.start_time = time.time()
    t0 = time.time()
    
    try:
        sol2= backtracking_search(p2, select_unassigned_variable=wdeg_heuristic, inference=wdeg_mac)
        solved_str =bool(sol2)
        time_taken =time.time() - t0
    except TimeoutException:
        print("TIMEOUT!")
        sol2 =None
        solved_str= "TIMEOUT"
        time_taken= LIMIT

    results.append({"Alg": "MAC + dom/wdeg", "Time": time_taken, "Assigns": p2.nassigns, "Checks": p2.checks, "Solved": solved_str})


   
    print("3. Εκτέλεση FC-CBJ + dom/wdeg...")
    p3 = RLFA(vars_list, neighs_dict, doms_dict, ctr_map, time_limit=LIMIT)
    p3.start_time = time.time()
    t0 = time.time()

    try:
        sol3, _ = fc_cbj(p3)
        solved_str = bool(sol3)
        time_taken = time.time() - t0
    except TimeoutException:
        print("   -> TIMEOUT!")
        sol3 = None
        solved_str = "TIMEOUT"
        time_taken = LIMIT
        
    results.append({"Alg": "FC-CBJ + dom/wdeg", "Time": time_taken, "Assigns": p3.nassigns, "Checks": p3.checks, "Solved": solved_str})


   
    print("4. Εκτέλεση Min-Conflicts...")
    p4=RLFA(vars_list, neighs_dict, doms_dict, ctr_map, time_limit=LIMIT)
    p4.start_time=time.time()
    t0=time.time()

    try:
        sol4= min_conflicts(p4, max_steps=10000)
        solved_str = bool(sol4)
        time_taken = time.time() - t0
    except TimeoutException: 
        print("   -> TIMEOUT!")
        sol4 = None
        solved_str = "TIMEOUT"
        time_taken = LIMIT
    
    results.append({"Alg": "Min-Conflicts", "Time": time_taken, "Assigns": "-", "Checks": p4.checks, "Solved": solved_str})

    # --- ΕΚΤΥΠΩΣΗ ---
    print("\n" + "="*90)
    print(f"{'ALGORITHM':<22} | {'TIME (s)':<10} | {'ASSIGNS':<10} | {'CHECKS':<12} | {'SOLVED'}")
    print("-" * 90)
    for r in results:
        assigns_str = str(r['Assigns'])
        time_str = f"{r['Time']:.4f}"
        print(f"{r['Alg']:<22} | {time_str:<10} | {assigns_str:<10} | {r['Checks']:<12} | {r['Solved']}")
    print("="*90)