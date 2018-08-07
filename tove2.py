import logging
import rdflib
from rdflib.namespace import RDF, OWL, RDFS, FOAF
from rdflib import Literal, BNode, URIRef, Graph, Namespace

import DateTimeDescription
import ctime


cot = rdflib.Namespace('http://ontology.eil.utoronto.ca/TOVE2/ctime.rdf#')
time = rdflib.Namespace('http://www.w3.org/2006/time#')
rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

# namespace for predicate
hasBeginning = rdflib.URIRef('http://www.w3.org/2006/time#hasBeginning')
hasEnd = rdflib.URIRef('http://www.w3.org/2006/time#hasEnd')
hasMin = rdflib.URIRef(
	'http://ontology.eil.utoronto.ca/TOVE2/ctime.owl#hasMin')
hasMax = rdflib.URIRef(
	'http://ontology.eil.utoronto.ca/TOVE2/ctime.owl#hasMax')
hasDepartment = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#has_Department')
hasDuration = rdflib.URIRef('http://www.w3.org/2006/time#hasDuration')

# all the departments
Water = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Water')
Sewage = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Sewage')
Power = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Power')
Permits = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Permits')
Police = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Police')
Transportation = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Transportation')
Business = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Business')




# create the Instant with min and max given.
def create_CDTInstant(g, ins, min, max, min_ins, max_ins) :
	g.add((ins, RDF.type, cot.CDateTimeInstant))
	hasMin = rdflib.URIRef('http://ontology.eil.utoronto.ca/TOVE2/ctime.owl#hasMin')

	# min_ins = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Contractor_start_min')
	g.add((ins, hasMin, min_ins))
	g.add((min_ins, RDF.type, time.DateTimeDescription))
	g.add((min_ins,time.year, Literal(min[0])))
	g.add((min_ins, time.month, Literal(min[1])))
	g.add((min_ins, time.day, Literal(min[2])))


	# max_ins = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Contractor_start_max')
	g.add((ins, hasMax, max_ins))
	g.add((max_ins, RDF.type, time.DateTimeDescription))
	g.add((max_ins, time.year, Literal(max[0])))
	g.add((max_ins, time.month, Literal(max[1])))
	g.add((max_ins, time.day, Literal(max[2])))





def add_contractor_timeInterval(g,bmin,bmax,emin,emax):
	# fisrt add the contractor time interval as a CDateTimeInterval instance.
	Contractor_TimeInterval = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Contractor_TimeInterval')
	# CDateTimeInterval = rdflib.URIRef('http://ontology.eil.utoronto.ca/TOVE2/ctime.owl#CDateTimeInterval')
	g.add((Contractor_TimeInterval, RDF.type, time.CDateTimeInterval))

	# contractor time interval has start and min, which are CdateTimeInstant type.
	contractor_start = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Contractor_start')
	contractor_end = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Contractor_end')
	g.add((Contractor_TimeInterval, time.hasBeginning, contractor_start))
	g.add((Contractor_TimeInterval, time.hasEnd, contractor_end))

	# each instant has a min and max, which are DateTimeDescription type.
	start_min_ins = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Contractor_start_min')
	start_max_ins = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Contractor_start_max')
	end_min_ins = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Contractor_end_min')
	end_max_ins = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Contractor_end_max')

	create_CDTInstant(g,contractor_start,bmin,bmax, start_min_ins, start_max_ins)
	create_CDTInstant(g,contractor_end,emin,emax, end_min_ins, end_max_ins)




"""
get all the activities in the schedule and its time interval, save in a dictionary and return.
"""
def get_all_activity(g):
	# use predicate has_TimeInterval to get all the activities and their corresponding time interval.
    has_TimeInterval = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#has_TimeInterval')

    # loop over the graph to get all the activities and their time interval, and save in a dictionary.
    i = 0
    activity_schedule = {}
    for activity, timeInterval in g.subject_objects(predicate=has_TimeInterval):
        activity_schedule[activity] = timeInterval
        # print("%s has time interval %s" % (activity, timeInterval))
        i+=1
    print("Step 1: Get all activities in our schedule, total %d activities" %i)

    print activity_schedule
    return activity_schedule





"""
check if Interval I1 is contained in Interval I2,
i.e., return true if I1_beginning_min > I2_beginning_max
and I1_end_max < I2_end_max.
note: all the inputs are type DatetimeDescription.
"""

def IntervalContatins(g,I1_beginning_min,I1_end_max,
					  I2_beginning_min,I2_end_max):
    day = rdflib.URIRef('http://www.w3.org/2006/time#day')
    month = rdflib.URIRef('http://www.w3.org/2006/time#month')
    year = rdflib.URIRef('http://www.w3.org/2006/time#year')


    # If I1_beginning_min > I2_beginning_min and I1_end_max <  I2_end_max, then interval I2 contains interval I1
    I1_bmin_day = g.value(subject=I1_beginning_min, predicate=time.day)
    I1_bmin_month = g.value(subject=I1_beginning_min, predicate=time.month)
    I1_bmin_year = g.value(subject=I1_beginning_min, predicate=time.year)
    I1_emax_day = g.value(subject=I1_end_max, predicate=time.day)
    I1_emax_month = g.value(subject=I1_end_max, predicate=time.month)
    I1_emax_year = g.value(subject=I1_end_max, predicate=time.year)
    # print I1_bmin_day, I1_bmin_month, I1_bmin_year

    I2_bmin_day = g.value(subject=I2_beginning_min, predicate=time.day)
    I2_bmin_month = g.value(subject=I2_beginning_min, predicate=time.month)
    I2_bmin_year = g.value(subject=I2_beginning_min, predicate=time.year)
    I2_emax_day = g.value(subject=I2_end_max, predicate=time.day)
    I2_emax_month = g.value(subject=I2_end_max, predicate=time.month)
    I2_emax_year = g.value(subject=I2_end_max, predicate=time.year)
    # print I2_bmin_day, I2_bmin_month, I2_bmin_year

    if (I1_bmin_year >= I2_bmin_year and I1_bmin_month >= I2_bmin_month and I1_bmin_day >= I2_bmin_day) and (I1_emax_year <= I2_emax_year and I1_emax_month <= I2_emax_month and I1_emax_day <= I2_emax_day):
        # print "I1 is contained in I2"
        return True
    # print "I1 is not contained in I2"
    return False


# check is that all the departments have satisfied schedule
def check_include_all_departments(g,activities_in_timeInterval):
    deparments = [Water, Sewage, Power, Permits, Police, Transportation, Business]
    for act in activities_in_timeInterval:
        dep = g.value(subject=act, predicate=hasDepartment)
        if dep in deparments:
            deparments.remove(dep)
        if len(deparments) == 0:
            print "These activities include all the departments.\n"
            return True
    print "These activities do not include all the departments.\n"
    return False

# check if interval I1 is before interval I2.
# if I1_end_min < I2_start_min, then I1 is before I2.
def intervalBefore(g,I1,I2):
    I1_end = g.value(subject= I1, predicate= hasEnd)
    I1_end_min =g.value(subject= I1_end, predicate= hasMin)
    I2_start = g.value(subject= I2, predicate= hasBeginning)
    I2_start_min = g.value(subject = I2_start, predicate=hasMin)

    I1_end_min_year = g.value(subject=I1_end_min, predicate=time.year)
    I1_end_min_month = g.value(subject=I1_end_min, predicate=time.month)
    I1_end_min_day = g.value(subject=I1_end_min, predicate=time.day)

    I2_start_min_year = g.value(subject=I2_start_min, predicate=time.year)
    I2_start_min_month = g.value(subject=I2_start_min, predicate=time.month)
    I2_start_min_day = g.value(subject=I2_start_min, predicate=time.day)

    if(I1_end_min_year <= I2_start_min_year and
			I1_end_min_month <= I2_start_min_month and
			I1_end_min_day <= I2_start_min_day):
        # print "Interval I1 is before I2"
        return True

    # print "Interval I1 is not before I2"
    return False


# from the given activities' schedule, get start_max time instant of each activity,
# find the minimum of among these activities' start_max instant,
# and this is the exact start time for the contractor we find.
def TAC_find_contractor_start(g,activities):
    act_dic={}
    for act in activities:
        act_start =g.value(subject=activities[act],predicate=hasBeginning)
        act_start_max = g.value(subject=act_start,predicate=hasMax)
        dtdc_act_start_max = DateTimeDescription.DateTimeDescription(g, act_start_max)
        act_dic[dtdc_act_start_max] = act_start_max

    act_lst= list(act_dic)
    min_date = act_lst[0]
    for j in range(1,len(act_lst)-1):
        if min_date.greaterthan(act_lst[j]):
            min_date = act_lst[j]
    print "the contractor strat is:", act_dic[min_date]
    return act_dic[min_date]




# from the given activities' schedule, get end_min time instant of each activity,
# find the maximum of among these activities' end_min instant,
# and this is the exact end time for the contractor we find.
def TAC_find_contractor_end(g,activities):
    act_dic={}
    for act in activities:
        act_end =g.value(subject=activities[act],predicate=hasEnd)
        act_end_min = g.value(subject=act_end,predicate=hasMin)
        dtdc_act_end_min = DateTimeDescription.DateTimeDescription(g, act_end_min)
        act_dic[dtdc_act_end_min] = act_end_min

    act_lst= list(act_dic)
    max_date = act_lst[0]
    for j in range(1,len(act_lst)-1):
        if act_lst[j].greaterthan(max_date):
            max_date = act_lst[j]
    print "the contractor end is:", act_dic[max_date]
    return act_dic[max_date]














def main():
    print('Starting main')

    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logging.info(' ctime Started')

    g = Graph()
    # load tove2 examples
    test2 = rdflib.Namespace('example.ttl#')
    g.parse('example.ttl#', format="turtle")

    print 'the length of ttl file is:',len(g)

    logging.info('ctime Finished')

    # namespace for predicate
    hasBeginning = rdflib.URIRef('http://www.w3.org/2006/time#hasBeginning')
    hasEnd = rdflib.URIRef('http://www.w3.org/2006/time#hasEnd')
    hasMin = rdflib.URIRef(
		'http://ontology.eil.utoronto.ca/TOVE2/ctime.owl#hasMin')
    hasMax = rdflib.URIRef(
		'http://ontology.eil.utoronto.ca/TOVE2/ctime.owl#hasMax')

    #============input the contractor's time interval here======================
    # here we input the contract time interval starts between:(2018,2,1)-(2018,2,5), ends between:(2018,2,20)-(2018,2,25)
    add_contractor_timeInterval(g, [2018,2,1,time.unitDay], [2018,2,5,time.unitDay], [2018,2,20,time.unitDay], [2018,2,25,time.unitDay])
    # add_contractor_timeInterval(g, [2018, 8, 1, time.unitDay],[2018, 8, 5, time.unitDay],[2018, 8, 20, time.unitDay],[2018, 8, 25, time.unitDay])

    print "after adding the contractor time interval, the length is", len(g)
    contractor_start = g.value(subject=rdflib.URIRef(
		'http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Contractor_TimeInterval'),predicate=hasBeginning)
    contractor_start_min = g.value(contractor_start,predicate=hasMin)
    contractor_start_max = g.value(subject=rdflib.URIRef(
        'http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Contractor_start'),predicate=hasMax)

    syear_min = g.value(subject=contractor_start_min,predicate=time.year)
    smonth_min = g.value(subject=contractor_start_min, predicate=time.month)
    sday_min = g.value(subject=contractor_start_min, predicate=time.day)
    syear_max = g.value(subject=contractor_start_max,predicate=time.year)
    smonth_max = g.value(subject=contractor_start_max, predicate=time.month)
    sday_max = g.value(subject=contractor_start_max, predicate=time.day)
    print ("contractor start time interval:({},{},{})-({},{},{})".format(syear_min, smonth_min, sday_min, syear_max, smonth_max,sday_max))

    contractor_end = g.value(subject=rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Contractor_TimeInterval'),predicate=hasEnd)
    contractor_end_min = g.value(subject=contractor_end,predicate=hasMin)
    contractor_end_max = g.value(subject=rdflib.URIRef(
		'http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Contractor_end'),predicate=hasMax)

    eyear_min = g.value(subject=contractor_end_min,predicate=time.year)
    emonth_min = g.value(subject=contractor_end_min, predicate=time.month)
    eday_min = g.value(subject=contractor_end_min, predicate=time.day)
    eyear_max = g.value(subject=contractor_end_max,predicate=time.year)
    emonth_max = g.value(subject=contractor_end_max, predicate=time.month)
    eday_max = g.value(subject=contractor_end_max, predicate=time.day)
    print ("contractor end time interval:({},{},{})-({},{},{})".format(eyear_min, emonth_min, eday_min, eyear_max, emonth_max,eday_max))


    # get all the activities schedule
    activities = get_all_activity(g)

    # for each activity, we have timeinterval for begining and end
	# get the min and max(i.e. instant) for both beginning and end interval
	# use a dictionary to save the activities whose shcedule is contained in the contractor time interval
    activities_in_timeInterval = {}
    for act in activities:
        beginning = g.value(subject=activities[act], predicate=hasBeginning)
        beginning_min = g.value(subject=beginning, predicate=hasMin)
        beginning_max = g.value(subject=beginning, predicate=hasMax)
        # print ("%s has beginning between %s and %s \n" %(act, beginning_min, beginning_max))

        end = g.value(subject=activities[act], predicate=hasEnd)
        end_min = g.value(subject=end, predicate=hasMin)
        end_max = g.value(subject=end, predicate=hasMax)
        # print ("%s has end between %s and %s \n" %(act, end_min, end_max))


		# check if this activity is contained in the contractor time interval
        if IntervalContatins(g,beginning_min, end_max, contractor_start_min, contractor_end_max):
            # if the activity time interval is contained in the contractor time interval, save it
            activities_in_timeInterval[act] = activities[act]

    print "Step 2: Activities whose timeinterval is contained in contractor's timeinterval, save them in a dictionary where the key is the activitiy and corresponding value is the activity's timeInterval: \n",activities_in_timeInterval

    if len(activities_in_timeInterval) != 0:

        # check if these activities include all the departments
        print "Step 3: Check if thses activities include all the deparment."
        if (check_include_all_departments(g, activities_in_timeInterval)):
            # print "These activities include all the departments."

            # check if sewage activity is before water, i.e. sewage's duration is before water's duration
            print "Step 4: Check if sewage activity is before water activity."
            for act in activities_in_timeInterval:
                if (g.value(subject=act, predicate=hasDepartment) == Sewage):
                    sewage_interval = activities_in_timeInterval[act]
                if (g.value(subject=act, predicate=hasDepartment) == Water):
                    water_interval = activities_in_timeInterval[act]

            if intervalBefore(g,sewage_interval,water_interval):
                print "Sewage is before Water.\n"

                print "Step 5: Find the exact start and end date for contractor accroding the activities' schedule."
                # finally, we need to get restrain the start and end of the contractor' time interval into a specific date, and also as short as possible.
                res_start = TAC_find_contractor_start(g, activities_in_timeInterval)
                res_end = TAC_find_contractor_end(g, activities_in_timeInterval)
                g.serialize(destination='output1.ttl',format='turtle')
                print "finish serializing"
                return (res_start,res_end)

    print "Thses is no feasible interval for the contractor."
    g.serialize(destination='example.ttl', format='turtle')
    print "finish serializing"
    return None




    g.close()
    print('Ending main')


if __name__ == '__main__':
    logging.basicConfig(filename='ctime.log', filemode='w',
                    format='%(levelname)s %(asctime)s: %(message)s',
                    level=logging.INFO)
    main()





