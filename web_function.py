import logging
import rdflib
from rdflib.namespace import RDF, OWL, RDFS, FOAF
from rdflib import Literal, BNode, URIRef, Graph, Namespace

import DateTimeDescription
import ctime
import tove2

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
hasTimeInterval = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#has_TimeInterval')

# all the departments
Water = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Water')
Sewage = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Sewage')
Power = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Power')
Permits = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Permits')
Police = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Police')
Transportation = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Transportation')
Business = rdflib.URIRef('http://www.semanticweb.org/luolixuan/ontologies/tove2/test#Business')

tove2_prefix = 'http://www.semanticweb.org/luolixuan/ontologies/tove2/test#'
activity_prefix = 'http://ontology.eil.utoronto.ca/activity.owl#Activity'

# add a new activity into schedule
# return true if success, false if not successful.
# date input int.
def add_activity(name,department,start_min_year,start_min_month,start_min_day,start_max_year,start_max_month,start_max_day,end_min_year,end_min_month,end_min_day,end_max_year,end_max_month,end_max_day,duration_min_year,duration_min_month,duration_min_day,duration_max_year,duration_max_month,duration_max_day):
    bmin = [start_min_year,start_min_month,start_min_day]
    bmax = [start_max_year,start_max_month,start_max_day]
    emin = [end_min_year,end_min_month,end_min_day]
    emax = [end_max_year,end_max_month,end_max_day]
    durmin = [duration_min_year,duration_min_month,duration_min_day]
    durmax = [duration_max_year,duration_max_month,duration_max_day]

    if department == 'Water':
        department = Water
    elif department == 'Sewage':
        department = Sewage
    elif department == 'Power':
        department = Power
    elif department == 'Permits':
        department = Permits
    elif department == 'Police':
        department = Police
    elif department == 'Transportation':
        department = Transportation
    else:
        department = Business


    g = Graph()
    test2 = rdflib.Namespace('output1.ttl#')
    g.parse('output1.ttl#', format="turtle")

    # if there is alredy activity with same name in the schedule, just return false
    if check_activity_name(g,name):
        return False

    #add the activity
    act_name = tove2_prefix + name
    g.add((rdflib.URIRef(act_name),RDF.type,rdflib.URIRef(activity_prefix)))

    #add its department
    g.add((rdflib.URIRef(act_name),hasDepartment, department))

    #add timeInterval
    act_timeInterval = rdflib.URIRef(act_name + '_timeInterval')
    g.add((act_timeInterval, RDF.type, time.CDateTimeInterval))
    g.add((rdflib.URIRef(act_name),hasTimeInterval,act_timeInterval))

    #add start
    start = rdflib.URIRef(act_name + '_start')
    start_min_ins = rdflib.URIRef(act_name + '_start_min')
    start_max_ins = rdflib.URIRef(act_name + '_start_max')
    tove2.create_CDTInstant(g, start, bmin, bmax, start_min_ins, start_max_ins)
    g.add((act_timeInterval, hasBeginning, start))

    #add end
    end = rdflib.URIRef(act_name + '_end')
    end_min_ins = rdflib.URIRef(act_name + '_end_min')
    end_max_ins = rdflib.URIRef(act_name + '_end_max')
    tove2.create_CDTInstant(g,end,emin,emax, end_min_ins, end_max_ins)
    g.add((act_timeInterval, hasEnd, end))

    # add duration
    dur = rdflib.URIRef(act_name + '_duration')
    dur_min_ins = rdflib.URIRef(act_name + '_duration_min')
    dur_max_ins = rdflib.URIRef(act_name + '_duration_max')
    tove2.create_CDTInstant(g, dur, durmin, durmax, dur_min_ins, dur_max_ins)
    g.add((act_timeInterval, hasDuration, dur))

    g.close()
    g.serialize(destination='output1.ttl', format='turtle')

    return True


# delete an activity with the given name
def delete_activity(name):
    g = Graph()
    g.parse('output1.ttl#', format="turtle")

    act_name = tove2_prefix + name
    print act_name
    act_timeInterval = g.value(subject=rdflib.URIRef(act_name),predicate=hasTimeInterval)
    print act_timeInterval
    act_start = g.value(subject=rdflib.URIRef(act_timeInterval), predicate=hasBeginning)
    act_start_min = g.value(subject=rdflib.URIRef(act_start), predicate=hasMin)
    act_start_max = g.value(subject=rdflib.URIRef(act_start), predicate=hasMax)
    act_end = g.value(subject=rdflib.URIRef(act_timeInterval), predicate=hasEnd)
    act_end_min = g.value(subject=rdflib.URIRef(act_end), predicate=hasMin)
    act_end_max = g.value(subject=rdflib.URIRef(act_end), predicate=hasMax)
    act_dur = g.value(subject=rdflib.URIRef(act_timeInterval), predicate=hasDuration)
    act_dur_min = g.value(subject=rdflib.URIRef(act_dur), predicate=hasMin)
    act_dur_max = g.value(subject=rdflib.URIRef(act_dur), predicate=hasMax)

    g.remove((rdflib.URIRef(act_dur),None,None))
    g.remove((rdflib.URIRef(act_dur_min),None,None))
    g.remove((rdflib.URIRef(act_dur_max),None,None))

    g.remove((rdflib.URIRef(act_start),None,None))
    g.remove((rdflib.URIRef(act_start_min),None,None))
    g.remove((rdflib.URIRef(act_start_max),None,None))

    g.remove((rdflib.URIRef(act_end),None,None))
    g.remove((rdflib.URIRef(act_end_min),None,None))
    g.remove((rdflib.URIRef(act_end_max),None,None))

    g.remove((rdflib.URIRef(act_timeInterval),None,None))
    g.remove((rdflib.URIRef(act_name),None,None))



    g.close()
    g.serialize(destination='output1.ttl', format='turtle')



# get all the activities and its departments
def get_activity_dic():
    g = Graph()
    g.parse('output1.ttl#', format="turtle")

    i=0
    act_dic = {}
    for act, dep in g.subject_objects(predicate=hasDepartment):
        act_name = act.split("#")[-1]
        dep_name = dep.split("#")[-1]
        act_dic[act_name] = dep_name

    # print act_lst
    return act_dic

    g.close()
    g.serialize(destination='output1.ttl', format='turtle')




# edit the activity
def edit_activity(old_name,new_name,department,start_min_year,start_min_month,start_min_day,start_max_year,start_max_month,start_max_day,end_min_year,end_min_month,end_min_day,end_max_year,end_max_month,end_max_day,duration_min_year,duration_min_month,duration_min_day,duration_max_year,duration_max_month,duration_max_day):
    # g = Graph()
    # test2 = rdflib.Namespace('output1.ttl#')
    # g.parse('example.ttl#', format="turtle")

    delete_activity(old_name)
    add_activity(new_name,department,start_min_year,start_min_month,start_min_day,start_max_year,start_max_month,start_max_day,end_min_year,end_min_month,end_min_day,end_max_year,end_max_month,end_max_day,duration_min_year,duration_min_month,duration_min_day,duration_max_year,duration_max_month,duration_max_day)


    # g.close()
    # g.serialize(destination='output1.ttl', format='turtle')


# find the activity's detail with its name
def get_activity_detail(name):
    g = Graph()
    test2 = rdflib.Namespace('output1.ttl#')
    g.parse('output1.ttl#', format="turtle")

    act_name = tove2_prefix + name


    #timeInterval
    interval = g.value(subject=rdflib.URIRef(act_name),predicate=hasTimeInterval)

    start = g.value(subject=rdflib.URIRef(interval),predicate=hasBeginning)
    start_min = g.value(subject=rdflib.URIRef(start), predicate=hasMin)
    start_min_year= g.value(subject=rdflib.URIRef(start_min),predicate=time.year)
    start_min_month = g.value(subject=rdflib.URIRef(start_min),predicate=time.month)
    start_min_day = g.value(subject=rdflib.URIRef(start_min),predicate=time.day)

    start_max = g.value(subject=rdflib.URIRef(start), predicate=hasMax)
    start_max_year= g.value(subject=rdflib.URIRef(start_max),predicate=time.year)
    start_max_month = g.value(subject=rdflib.URIRef(start_max),predicate=time.month)
    start_max_day = g.value(subject=rdflib.URIRef(start_max),predicate=time.day)



    end = g.value(subject=rdflib.URIRef(interval),predicate=hasEnd)
    end_min = g.value(subject=rdflib.URIRef(end), predicate=hasMin)
    end_min_year= g.value(subject=rdflib.URIRef(end_min),predicate=time.year)
    end_min_month = g.value(subject=rdflib.URIRef(end_min),predicate=time.month)
    end_min_day = g.value(subject=rdflib.URIRef(end_min),predicate=time.day)

    end_max = g.value(subject=rdflib.URIRef(end),predicate=hasMax)
    end_max_year= g.value(subject=rdflib.URIRef(end_max),predicate=time.year)
    end_max_month = g.value(subject=rdflib.URIRef(end_max),predicate=time.month)
    end_max_day = g.value(subject=rdflib.URIRef(end_max),predicate=time.day)


    dur = g.value(subject=rdflib.URIRef(interval),predicate=hasDuration)
    dur_min = g.value(subject=rdflib.URIRef(dur),predicate=hasMin)
    dur_min_year= g.value(subject=rdflib.URIRef(dur_min),predicate=time.year)
    dur_min_month = g.value(subject=rdflib.URIRef(dur_min),predicate=time.month)
    dur_min_day = g.value(subject=rdflib.URIRef(dur_min),predicate=time.day)

    dur_max = g.value(subject=rdflib.URIRef(dur),predicate=hasMax)
    dur_max_year= g.value(subject=rdflib.URIRef(dur_max),predicate=time.year)
    dur_max_month = g.value(subject=rdflib.URIRef(dur_max),predicate=time.month)
    dur_max_day = g.value(subject=rdflib.URIRef(dur_max),predicate=time.day)

    return [start_min_year,start_min_month,start_min_day,start_max_year,start_max_month,start_max_day,end_min_year,end_min_month,end_min_day,end_max_year,end_max_month,end_max_day,dur_min_year,dur_min_month,dur_min_day,dur_max_year,dur_max_month,dur_max_day]


    g.close()
    g.serialize(destination='output1.ttl', format='turtle')















# check if the given name activity is already in the schedule.
# return True if yes, False otherwise.
def check_activity_name(g,name):
    act = tove2_prefix+name
    print act
    res = g.value(subject=rdflib.URIRef(act),predicate=RDF.type)

    if res:
        print "the activity "+name+ " is in schedule"
    else:
        print "the activity "+name+ " is not in schedule"
    # print res
    return res




def main():
    print('Starting main')

    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logging.info(' ctime Started')

    g = Graph()
    # load tove2 examples
    test2 = rdflib.Namespace('output1.ttl#')
    g.parse('output1.ttl#', format="turtle")

    print 'the length of ttl file is:', len(g)


    # act = "water_act"
    act = tove2.get_all_activity(g)
    for a in act.keys():
        print a

    c = 'Water_Oct_Activity'
    d = tove2_prefix+c
    print d

    print g.value(subject=rdflib.URIRef(d), predicate=RDF.type)
    print (g.value(subject=rdflib.URIRef(d), predicate=RDF.type) is not None)

    # print check_activity_name(g,c)

    check_activity_name(g,'test_activity')

    # res = add_activity('test_activity', Water, 2017,1,1, 2017,1,5, 2017,2,1, 2017,2,5, 2017,1,5, 2017,2,1)












    logging.info('ctime Finished')

    g.serialize(destination='output1.ttl', format='turtle')







# if __name__ == '__main__':
#     logging.basicConfig(filename='ctime.log', filemode='w',
#                     format='%(levelname)s %(asctime)s: %(message)s',
#                     level=logging.INFO)
#     main()

    # add_activity('test_activity', 'Water', 2017,1,1, 2017,1,5, 2017,2,1, 2017,2,5, 2017,1,5, 2017,2,1)

    # add_activity('test_activity3', 'Water', 2017,1,1, 2017,1,5, 2017,2,1, 2017,2,5, 2017,1,5, 2017,2,1)

# delete_activity('test_activity')

# a = get_activity_detail('Sewage_Apr_Activity')
# for i in a:
#     print i


    # edit_activity('test_activity', 'test_activity2', Water, 2017,1,1, 2017,1,5, 2017,2,1, 2017,2,5, 2017,1,5, 2017,2,1)

# delete_activity('test_activity2')
# delete_activity('test_activity3')



