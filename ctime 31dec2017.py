# TODO
#  - add more logging, also see if it actually works - may have to flush log
#  - add exception handling

import logging
import rdflib
from rdflib import Namespace
from rdflib.namespace import RDF, OWL, RDFS
from rdflib import Literal, BNode, URIRef

# ------------------TAC------------------------------------------------------
#
def TAC(g, todo = set()) :

	logging.info('Starting TAC')

	TAC_inconsistentNodes = set()	# keeps track of inconsistent needs for this run
	
	# if no intervals are designated, retrieve all of them
	if len(todo) = 0 : for s in g.subjects(RDF.type, cot.CDateTimeInterval) : todo.add(s)
	
	# cycle through all todo and execute TAC for each temporal relation
	for cint1 in todo :
		logging.debug('TAC: Processing [%s %s]', str(g), str(dtd))
		del todo[cint1]
		for pred in [time.intervalBefore, time.intervalAfter, time.intervalOverlaps,
					 time.intervalOverlappedBy] :
			for cint2 in g.objects(cint1, pred) :
				if pred == time.intervalBefore and TAC_intervalBefore(g, cint1, g, cint2) : todo.add(cint2)
				if pred == time.intervalAfter and TAC_intervalAfter(g, cint1, g, cint2) : todo.add(cint2)
				if pred == time.intervalOverlaps and TAC_intervalOverlaps(g, cint1, g, cint2) : todo.add(cint2)
				if pred == time.intervalOverlappedBy and TAC_intervalOverlappedBy(g, cint1, g, cint2) : todo.add(cint2)
		
		# propagate any change within the interval using TAC_CInterval (before between beginning and end)
		(changed, inconsistent) = TAC_CInterval(g, cint1)
		if inconsistent : TAC_incosistentNodes.add(cint1)
		else : if changed : todo.add(cint1)	# don't redo the interval if it is inconsistent
		
	
		
# ------------------retrieve_DTD_object------------------------------------------------------
#
# if object has already been created then return it
# if object has not already been created, then create and transfer data from RDF
# if RDF does not exist, then return None

def retrieve_DTD_Object(g, dtd) :
	if (g, dtd) in DateTimeDescription.dtd_dtdc_map : return(DateTimeDescription.dtd_dtdc_map[(g, dtd)])
	if dtdo = DateTimeDescription(g, dtd) : return(dtdo)
	logging.debug('DTDC.retrieve_DTD_Object: No DTD_O for [%s %s]', str(g), str(dtd))
	return(None)
	
# ------------------TAC_CInterval------------------------------------------------------
#
# TAC_CInterval performs arc consistency within an Constrained Interval
#	If no duration, then set dur = 0
#	If PBmin + Dur > PEmin then PEmin = PBmin + Dur
#	If PBmax + Dur > PEmax, then PBmax = PEmax – Dur
#
# returns True if change made, False if not


def TAC_Cinterval(g. cInt) :
	changed = False
	inconsistent = False
	
	dur = g.value(cInt, time.hasDurationDescription, any=False)
	if dur : dtdc_dur = retrieve_DTD_Object(g, dur)
	else : dtdc_dur = DateTimeDescription()		# set duration to zero
	
	pb = g.value(cInt, time.hasBeginning, any=False)
	pbmin = g.value(pb, cot.hasMin, any=False)
	dtdc_pbmin = retrieve_DTD_Object(g, pbmin)	# get object that pbmin RDF maps into
	pbmax = g.value(pb, cot.hasMax, any=False)
	dtdc_pbmax = retrieve_DTD_Object(g, pbmax)	# get object that pbmax RDF maps into
	
	pe = g.value(cInt, time.hasEnd, any=False)
	pemin = g.value(pe, cot.hasMin, any=False)
	dtdc_pemin = retrieve_DTD_Object(g, pemin)	# get object that pemin RDF maps into
	pemax = g.value(pe, cot.hasMax, any=False)
	dtdc_pemax = retrieve_DTD_Object(g, pemax)	# get object that pemax RDF maps into
	
	dtdc_pbmin_plus_dur = dtdc_pbmin.add(dtdc_dur)
	if dtdc_pbmin_plus_dur.greaterthan(dtdc_pemin) : 
		dtdc_pbmin_plus_dur.copy_into(dtdc_pemin)
		dtdc_pbmin_plus_dur.remove()	# delete the temporary dtdc
		changed = True
	
	dtdc_pbmax_plus_dur = dtdc_pbmax.add(dtdc_dur)
	if dtdc_pbmax_plus_dur.greaterthan(dtdc_pemax) :
		dtdc_pemax_minus_dur = dtdc_pemax.minus(dtdc_dur) 
		dtdc_pemax_minus_dur.copy_into(dtdc_pemax)
		dtdc_pemax_minus_dur.remove()	# delete the temporary dtdc
		dtdc_pbmax_plus_dur.remove()
		changed = True
	
	if dtdc_pbmin.greaterthan(dtdc_pbmax) : inconsistent = True
	if dtdc_pemin.greaterthan(dtdc_pemax) : inconsistent = True
	if dtdc_pbmin.greaterthan(dtdc_pemin) : inconsistent = True
	
	if not dur : dtdc_dur.remove)()		# delete the temporary dtdc
	return((changed, inconsistent))
	

# -----------------------DateTimeDescription_check----------------------------------------
#
# check whether a DateTimeDescription is complete, wrt its unitType
# parameters:
#	g: the graph to be searched
#	dtd: the DateTimeDescription individual to be chequed
#	create: if the dtd does not exist, then create it
#		or if the dtd exists, add in missing values as specified
#	ut: unitType (from time ontology). Values of time.unitYear, time.unitMonth, etc.
#	yr, mo, da, hr, mi, se are year, month, day, hour, minute and second, all
#		non negative numbers. Defaults to 0
#	
# returns (status, unitType, year, month, day, hour, minute, second)
# where status = 0 if create is false and dtd does not exists; =1 if it already existed; 
#	=2 if it did not exist but was created; =3 if dtd exists but missing unitType


		
def DateTimeDescription_check(g, dtd, create=1, ut=time.unitYear, yr=Literal(0), 
	mo=Literal(0), da=Literal(0), hr=Literal(0), mi=Literal(0), se=Literal(0)) :
	
	dtd_exists = (dtd, RDF.type, time.DateTimeDescription) in g
	
	# if dtd does not exist, and create is not requested, then return False
	if not dtd_exists and not create :
		return((0, None, None, None, None, None, None, None))
		
	# if dtd does not exist then create it using values specified by parameters, or defaults
	if not dtd_exists :
		g.add((dtd, RDF.type, time.DateTimeDescription))
		g.add((dtd, time.year, yr))
		g.add((dtd, time.month, mo))
		g.add((dtd, time.day, da))
		g.add((dtd, time.hour, hr))
		g.add((dtd, time.minute, mi))
		g.add((dtd, time.second, se))
		return((2, ut, yr, mo, da, hr, mi, se))
		
	utype = g.value(dtd, time.unitType, any=False)
	
	if not utype and not create :
		return((3, None, None, None, None, None, None, None))
	
	if not utype :		# if the unitType does not exist, then create one using parameter or default
		g.add((dtd, time.unitType, ut))
		
	match = g.value(dtd, time.year, any=False)
	if not match :
		g.add((dtd, time.year, yr))
	else :
		yr = match
			
	if ut == time.unitYear :
		return((4, ut, yr, None, None, None, None, None))
		
	match = g.value(dtd, time.month, any=False)
	if not match :
		g.add((dtd, time.month, mo))
	else :
		mo = match
			
	if ut == time.unitMonth :
		return((5, ut, yr, mo, None, None, None, None))
		
	match = g.value(dtd, time.day, any=False)
	if not match :
		g.add((dtd, time.day, da))
	else :
		da = match
			
	if ut == time.unitDay :
		return((6, ut, yr, mo, da, None, None, None))
		
	match = g.value(dtd, time.hour, any=False)
	if not match :
		g.add((dtd, time.hour, hr))
	else :
		hr = match
			
	if ut == time.unitHour :
		return((7, ut, yr, mo, da, hr, None, None))
		
	match = g.value(dtd, time.minute, any=False)
	if not match :
		g.add((dtd, time.minute, mi))
	else :
		mi = match
			
	if ut == time.unitMinute :
		return((8, ut, yr, mo, da, hr, mi, None))
		
	match = g.value(dtd, time.second, any=False)
	if not match :
		g.add((dtd, time.second, se))
		return((9, ut, yr, mo, da, hr, mi, se))
	else :
		se = match

	return((1, ut, yr, mo, da, hr, mi, se))

# ----------------------------DTD_lessthan--------------------------------------------	
#
# DTD_lessthan tests if a DateTimeDescription is less than a second
# the first dtd determines the unitType

def DTD_lessthan(g1, dtd1, g2, dtd2) :
	preds = {time.year : time.unitYear, time.month : time.unitMonth, time.day : time.unitDay, 
		time.hour : time.unitHour, time.minute : time.unitMinute, time.second : time.unitSecond }
		
	# get the unitType for each dtd
	ut1 = g1.value(dtd1, time.unitType, any=False)
	ut2 = g2.value(dtd2, time.unitType, any=False)
	
	# cycle through each unit until a less than or greater than is found
	# if neither is found and the unitType has been reached, then exit as False as they are equal
	# for the unitType specified for the first dtd
	for p, pu in preds.items() :
		t1 = g1.value(dtd1, p, any=False)
		t2 = g2.value(dtd2, p, any=False)
		if t1 < t2 : return(True)
		if t1 > t2 : return(False)
		if ut1 == pu : return(False)	# stop here as the unitType has been reached and they are equal
	
	return(False)	# they are equal
	
# -------------------------TAC_intervalBefore--------------------------------------------------
#
#	Given two Constrained Intervals, resets int2 beginning min time to be =
#	int1 end min time if it is less than
#
#	g1:	graph for the first Constrained Date Time Interval
#	cDTI1:	first constrained date time interval
#	g2:	graph for the second Constrained Date Time Interval
#	cDTI2:	second constrained date time interval

def TAC_intervalBefore(g1, cDTI1, g2, cDTI2) :

	# If P1Emin > P2Bmin then set P2Bmin to P1Emin
	
	p1e = g1.value(cDTI1, time.hasEnd, any=False)
	p1emin = g1.value(p1e, cot.hasMin, any=False)
	dtdc_p1emin = retrieve_DTD_Object(g1, p1emin)	# get object that p1emin RDF maps into
	
	p2b = g2.value(cDTI2, time.hasBeginning, any=False)
	p2bmin = g2.value(p2b, cot.hasMin, any=False)
	dtdc_p2bmin = retrieve_DTD_Object(g2, p2bmin)	# get object that p2bmin RDF maps into
	
	if dtdc_p1emin.greaterThan(dtdc_p2bmin) :
		dtdc_p1emin.copy_into(dtdc_p2bmin)
		return(True)		# signifies that a change was made
	
	return(False)			# signifies that no change was made
	
def TAC_intervalAfter(g1, cDTI1, g2, cDTI2) :
	return(TAC_intervalBefore(g2, cDTI2, g1, cDTI1))
	
def TAC_intervalOverlaps(g1, cDTI1, g2, cDTI2) :

	# If P1Emin < P2Bmin then set P1Emin to P2Bmin
	
	p1e = g1.value(cDTI1, time.hasEnd, any=False)
	p1emin = g1.value(p1e, cot.hasMin, any=False)
	dtdc_p1emin = retrieve_DTD_Object(g1, p1emin)	# get object that p1emin RDF maps into
	
	p2b = g2.value(cDTI2, time.hasBeginning, any=False)
	p2bmin = g2.value(p2b, cot.hasMin, any=False)
	dtdc_p2bmin = retrieve_DTD_Object(g2, p2bmin)	# get object that p2bmin RDF maps into
	
	if dtdc_p1emin.lessThan(dtdc_p2bmin) :
		dtdc_p2bmin.copy_into(dtdc_p1emin)
		return(True)		# signifies that a change was made
	
	return(False)			# signifies that no change was made

def TAC_intervalOverlappedBy(g1, cDTI1, g2, cDTI2) :
	return(TAC_intervalOverlaps(g2, cDTI2, g1, cDTI1))	

