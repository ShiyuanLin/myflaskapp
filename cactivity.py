

import logging
import rdflib
from rdflib import Namespace
from rdflib.namespace import RDF, OWL, RDFS
from rdflib import Literal, BNode, URIRef
import DateTimeDescription

time = rdflib.Namespace('http://www.w3.org/2006/time#')	# specify the time namespace
cot = rdflib.Namespace('http://ontology.eil.utoronto.ca/TOVE2/ctime.rdf#')
test = rdflib.Namespace('http://ontology.eil.utoronto.ca/TOVE2/test.owl#')
rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

changed_CDTIntervals = set()	# list of changed Cintervals that have to be TAC'd
changed_DCTInstants = set()		# list of changed Cinstants that have to be TAC'd

time_intervals = [time.intervalBefore, time.intervalAfter, time.intervalOverlaps,
					 time.intervalOverlappedBy, time.intervalContains, time.intervalDuring]
					 
TAC_inconsistentNodes = set()	# keeps track of inconsistent needs for this run

# ------------------AAC------------------------------------------------------
#
# AAC performs activity arc consistency. 
#
#	g: graph
#	todo_cint: list of Cintervals to be TAC'd
#	todo_cins: list of Cinstants to be TAC'd

def AAC(g, todo_cint = set(), todo_cins = set()) :

	logging.info('Starting Activity AC')
	
	# first check Cintervals whose Cinstants have changed
	for cins in todo_cins : 
		if cint == (get_subject(g, time.hasBeginning, cins) or get_subject(g, time.hasEnd, cins)):
			(changed, inconsistent) = TAC_CInterval(g, cint)
			if inconsistent : 
				TAC_incosistentNodes.add(cint)
			else : 
				if changed : todo_cint.add(cint)	# don't redo the interval if it is inconsistent
	
	# if no Cintervals are designated, retrieve all of them
	if len(todo_cint) == 0 : 
		for s in g.subjects(RDF.type, cot.CDateTimeInterval) : todo_cint.add(s)
	
	# cycle through all todo and execute TAC for each temporal relation
	for cint1 in todo_cint :
		logging.debug('TAC: Processing [%s %s]', str(g), str(cint1))
		del todo_cint[cint1]
		for pred in ctime.time_intervals :
			for cint2 in g.objects(cint1, pred) :
				changed_cint = None
				if pred == time.intervalBefore: changed_cint = TAC_intervalBefore(g, cint1, g, cint2)
				if pred == time.intervalAfter: changed_cint = TAC_intervalAfter(g, cint1, g, cint2)
				if pred == time.intervalOverlaps: changed_cint = TAC_intervalOverlaps(g, cint1, g, cint2)
				if pred == time.intervalOverlappedBy: changed_cint = TAC_intervalOverlappedBy(g, cint1, g, cint2)
				for cint in changed_cint: 
					todo.add(cint)
					# propagate any change within the interval using TAC_CInterval (before between beginning and end)
					(changed, inconsistent) = TAC_CInterval(g, cint)
					if inconsistent : TAC_inconsistentNodes.add(cint)

		
def get_subject(g, pred, obj) :
	subj = None
	for s in g.subjects(pred, obj) :
		subj = s
		break
	return(subj)

	
# ------------------TAC_CInterval------------------------------------------------------
#
# TAC_CInterval performs arc consistency WITHIN an Constrained Interval
#	If no duration, then set dur = 0
#	If PBmin + Dur > PEmin then PEmin = PBmin + Dur
#	If PBmax + Dur > PEmax, then PBmax = PEmax – Dur
#
# returns True if change made, False if not


def TAC_Cinterval(g, cInt) :
	logging.debug('TAC_Cinterval: Processing [%s %s]', str(g), str(cInt))
	changed = False
	inconsistent = False
	
	dur = g.value(cInt, time.hasDurationDescription, any=False)
	if dur : dtdc_dur = DateTimeDescription.DateTimeDescription(g, dur)
	else : dtdc_dur = DateTimeDescription()		# set duration to zero
	
	pb = g.value(cInt, time.hasBeginning, any=False)
	pbmin_i = g.value(pb, cot.hasMin, any=False)
	pbmin = g.value(pbmin_i,time.inDateTime, any=False)
	dtdc_pbmin = DateTimeDescription.DateTimeDescription(g, pbmin)	# get object that pbmin RDF maps into
	pbmax_i = g.value(pb, cot.hasMax, any=False)
	pbmax = g.value(pbmax_i,time.inDateTime, any=False)
	dtdc_pbmax = DateTimeDescription.DateTimeDescription(g, pbmax)	# get object that pbmax RDF maps into
	
	pe = g.value(cInt, time.hasEnd, any=False)
	pemin_i = g.value(pe, cot.hasMin, any=False)
	pemin = g.value(pemin_i,time.inDateTime, any=False)
	dtdc_pemin = DateTimeDescription.DateTimeDescription(g, pemin)	# get object that pemin RDF maps into
	pemax_i = g.value(pe, cot.hasMax, any=False)
	pemax = g.value(pemax_i,time.inDateTime, any=False)
	dtdc_pemax = DateTimeDescription.DateTimeDescription(g, pemax)	# get object that pemax RDF maps into
	
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
	
	if changed: logging.debug('TAC_Cinterval: Changed [%s]', str(cInt))
	if inconsistent: logging.warning('TAC_Cinterval: Inconsistent [%s]', str(g), str(dtd))
	
	if not dur : dtdc_dur.remove()		# delete the temporary dtdc
	return((changed, inconsistent))
	
	
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
	
	logging.debug('TAC_intervalBefore: Processing [%s %s]', str(cDIT1), str(cDIT2))
	p1e = g1.value(cDTI1, time.hasEnd, any=False)
	p1emin_i = g1.value(p1e, cot.hasMin, any=False)
	p1emin = g1.value(p1emin_i, time.inDateTime, any=False)
	dtdc_p1emin = DateTimeDescription.DateTimeDescription(g1, p1emin)	# get object that p1emin RDF maps into
	
	p2b = g2.value(cDTI2, time.hasBeginning, any=False)
	p2bmin_i = g2.value(p2b, cot.hasMin, any=False)
	p2bmin = g1.value(b2bmin_i, time.inDateTime, any=False)
	dtdc_p2bmin = DateTimeDescription.DateTimeDescription(g2, p2bmin)	# get object that p2bmin RDF maps into
	
	if dtdc_p1emin.greaterThan(dtdc_p2bmin) :
		dtdc_p1emin.copy_into(dtdc_p2bmin)
		return((cDTI2))		# change was made CDTI2
	
	return(None)			# no change was made
	
def TAC_intervalAfter(g1, cDTI1, g2, cDTI2) :
	return(TAC_intervalBefore(g2, cDTI2, g1, cDTI1))
	
def TAC_intervalOverlaps(g1, cDTI1, g2, cDTI2) :

	# If P1Emin < P2Bmin then set P1Emin to P2Bmin
	
	logging.debug('TAC_intervalOverlaps: Processing [%s %s]', str(cDIT1), str(cDIT2))
	p1e = g1.value(cDTI1, time.hasEnd, any=False)
	p1emin_i = g1.value(p1e, cot.hasMin, any=False)
	p1emin = g1.value(p1emin_i, time.inDateTime, any=False)
	dtdc_p1emin = DateTimeDescription.DateTimeDescription(g1, p1emin)	# get object that p1emin RDF maps into
	
	p2b = g2.value(cDTI2, time.hasBeginning, any=False)
	p2bmin_i = g2.value(p2b, cot.hasMin, any=False)
	p2bmin = g2.value(p2bmin_i, time.inDateTime, any=False)
	dtdc_p2bmin = DateTimeDescription.DateTimeDescription(g2, p2bmin)	# get object that p2bmin RDF maps into
	
	if dtdc_p1emin.lessThan(dtdc_p2bmin) :
		dtdc_p2bmin.copy_into(dtdc_p1emin)
		return((cDTI1))		# signifies that a change was made
	
	return(None)			# signifies that no change was made

def TAC_intervalOverlappedBy(g1, cDTI1, g2, cDTI2) :
	return(TAC_intervalOverlaps(g2, cDTI2, g1, cDTI1))	
	
def TAC_intervalContains(g1, cDTI1, g2, cDTI2) :
	change1 = False
	change2 = False
	
	# If P2Bmin < P1Bmin then set P2Bmin to P1Bmin

	logging.debug('TAC_intervalContains: Processing [%s %s]', str(cDIT1), str(cDIT2))
	p1b = g1.value(cDTI1, time.hasBeginning, any=False)
	p1bmin_i = g1.value(p1e, cot.hasMin, any=False)
	p1bmin = g1.value(p1bmin_i, time.inDateTime, any=False)
	dtdc_p1bmin = DateTimeDescription.DateTimeDescription(g1, p1bmin)	# get object that p1bmin RDF maps into
	
	p2b = g2.value(cDTI2, time.hasBeginning, any=False)
	p2bmin_i = g2.value(p2b, cot.hasMin, any=False)
	p2bmin = g2.value(p2bmin_i, time.inDateTime, any=False)
	dtdc_p2bmin = DateTimeDescription.DateTimeDescription(g2, p2bmin)	# get object that p2bmin RDF maps into
	
	if dtdc_p2bmin.lessThan(dtdc_p1bmin) :
		dtdc_p1bmin.copy_into(dtdc_p2bmin)
		change2 = True
	
	# If P2Emax > P1Emax then set P2Emax to P1Emax
	
	p1e = g1.value(cDTI1, time.hasEnd, any=False)
	p1emax_i = g1.value(p1e, cot.hasMax, any=False)
	p1emax = g1.value(p1emax_i, time.inDateTime, any=False)
	dtdc_p1emax = DateTimeDescription.DateTimeDescription(g1, p1emax)	# get object that p1bmin RDF maps into
	
	p2e = g2.value(cDTI2, time.hasEnd, any=False)
	p2emax_i = g2.value(p2e, cot.hasMax, any=False)
	p2emax = g2.value(p2emax_i, time.inDateTime, any=False)
	dtdc_p2emax = DateTimeDescription.DateTimeDescription(g2, p2emax)	# get object that p2bmin RDF maps into
	
	if dtdc_p2emax.greaterThan(dtdc_p1emax) :
		dtdc_p1emax.copy_into(dtdc_p2emax)
		change2 = True

	if change2: return((cDTI2))
	else: return(None)

# -------------------------add_CDTInterval--------------------------------------------------
#
# Adds a new Constrained DateTimeInterval to graph g.  CDTInterval is composed of a beginning 
# and end constrained DateTimeInstant, each having a min and a max
#
#	g: graph in which the interval is to be created
#	int: URI for the interval
#	bmin: for the min of the beginning time instant, a list of [year, month, day, hour, second, minute, unitType]
#	bmax: same for the max of the beginning time instant
#	emin: same for the min of the ending time instant
#	emax: same for the max of the ending time instant


def add_CDTInterval(g, int, bmin, bmax, emin, emax) :
	logging.debug('add_CDTInterval: Processing [%s]', str(int))
	
	g.add((int, RDF.type, cot.CDateTimeInterval))
	
	b = BNode()
	g.add((int, time.hasBeginning, b))
	g.add((b, RDF.type, cot.CDateTimeInstant))
	create_CDTInstant(b, bmin, bmax)
	
	e = BNode()
	g.add((int, time.hasEnd, e))
	g.add((e, RDF.type, cot.CDateTimeInstant))
	create_CDTInstant(e, emin, emax)

	changed_CDTIntervals.add(int)
	
def create_CDTInstant(g, ins, min, max) :
	g.add((ins, RDF.type, cot.CDateTimeInstant))
	
	min_ins = BNode()
	g.add((ins, cot.hasMin, min_ins))
	g.add((min_ins, RDF.type, time.Instant))
	min_dtd = BNode()
	g.add((min_ins, time.inDateTime, min_dtd))
	g.add((min_dtd, RDF.type, time.DateTimeDescription))
	g.add((min_dtd, time.year, Literal(min[0])))
	g.add((min_dtd, time.month, Literal(min[1])))
	g.add((min_dtd, time.day, Literal(min[2])))
	g.add((min_dtd, time.hour, Literal(min[3])))
	g.add((min_dtd, time.minute, Literal(min[4])))
	g.add((min_dtd, time.second, Literal(min[5])))
	g.add((min_dtd, time.unitType, min[6]))
	
	max_ins = BNode()
	g.add((ins, cot.hasMax, max_ins))
	g.add((max_ins, RDF.type, time.Instant))
	max_dtd = BNode()
	g.add((max_ins, time.inDateTime, max_dtd))
	g.add((max_dtd, RDF.type, time.DateTimeDescription))
	g.add((max_dtd, time.year, Literal(max[0])))
	g.add((max_dtd, time.month, Literal(max[1])))
	g.add((max_dtd, time.day, Literal(max[2])))
	g.add((max_dtd, time.hour, Literal(max[3])))
	g.add((max_dtd, time.minute, Literal(max[4])))
	g.add((max_dtd, time.second, Literal(max[5])))
	g.add((max_dtd, time.unitType, max[6]))
	
# -------------------------add_TProperty--------------------------------------------------
#
# Adds a new  temporal property between two intervals in the same graph g.
#
#	g: graph in which the interval is to be created
#	int1: URI for the interval1
#	prop: URI of the temporal property
#	int2: URI for interval2

def add_TProperty(g, int1, prop, int2) :
	logging.debug('Tadd_TProperty: Processing [%s %s %s]', str(int1), str,(prop), str(int2))
	if not (int1, RDF.type, cot.CDateTimeInterval) in g : logging.warning('Add_TProperty: int1 %s not a CDateTimeInterval]', str(int1))
	if not (int2, RDF.type, cot.CDateTimeInterval) in g : logging.warning('Add_TProperty: int2 %s not a CDateTimeInterval]', str(int2))
	if not prop in time_intervals : logging.warning('Add_TProperty: prop %s not a time interval]', str(prop))
	g.add((int1, prop, int2))
	changed_CDTIntervals.add(int1)
	
# -------------------------assert_CDTInstant_value--------------------------------------------------
#
# Asserts a single value for a CDTInstant, i.e., sets both the min and max to the same value
# and sets flag to asserted so that it cannot be undone
#
#	g: graph of Cinstant
#	cdtinst: URI of CInstant
#	yr, mo, da, hr, min, sec, ut are the values to be set and default to zero
#		except ut which defaults to time.unitYear

def assert_CDTInstant_value(g, cdtinst, yr=0, mo=0, da=0, hr=0, min=0, sec=0, ut=time.unitYear) :
	# if not a CDInstant then return
	if not (cdtinst, RDF.type, cot.CDateTimeInstant) in g :
		logging.warning('assert_CDTInstant_value: Not a CDTInstant [%s %s] ', str(g), str(cdtinst))
		return(False)
	
	# create temporary DTD for asserted value
	new_dtd = DateTimeDescription.DateTimeDescription(g, None, yr, mo, da, hr, min, sec, ut)
	
	# reset min but check if new value is less than it
	cdtimin_i = g.value(cdtinst, cot.hasMin, any=False)
	if not cdtimin_i :
		cdtimin_i = BNode()
		g.add((cdtimin_i, RDF.type, time.Instant))
		g.add((cdtinst, cot.hasMin, cdtimin_i))
	cdtimin = g.value(cdtimin_i, time.inDateTime, any=False)
	
	if not cdtimin:
		logging.warning('assert_CDTInstant_value: No hasMin cdti [%s %s] ', str(g), str(cdtinst))
		cdtimin = BNode()
		g.add((cdtimin_i, time.inDateTime, cdtimin))
		g.add((cdtimin, RDF.type, time.DateTimeDescription))
		g.add((cdtimin, time.year, Literal(yr)))
		g.add((cdtimin, time.month, Literal(mo)))
		g.add((cdtimin, time.day, Literal(da)))
		g.add((cdtimin, time.hour, Literal(hr)))
		g.add((cdtimin, time.minute, Literal(min)))
		g.add((cdtimin, time.second, Literal(sec)))
		g.add((cdtimin, time.unitType, ut))
	else :
		# if DTD exists, check its bound
		dtd = DateTimeDescription.DateTimeDescription.dtd_dtdc_map.get((g, cdtimin), None)
		if dtd :
			if dtd.greaterthan(new_dtd) :
				logging.warning('assert_CDTInstant_value: new dtd less than hasMin [%s %s] ', str(g), str(cdtinst))
		else :
			# if DTD does not exist, create it
			dtd = DateTimeDescription.DateTimeDescription(g, cdtimin)
		new_dtd.copy_into(dtd)
		dtd.update()
		
	# reset max but check if new value is greater than it
	cdtimax_i = g.value(cdtinst, cot.hasMax, any=False)
	if not cdtimax_i :
		cdtimax_i = BNode()
		g.add((cdtimax_i, RDF.type, time.Instant))
		g.add((cdtinst, cot.hasMax, cdtimax_i))
	cdtimax = g.value(cdtimax_i, time.inDateTime, any=False)
	if not cdtimax :
		logging.warning('assert_CDTInstant_value: No hasMax cdti [%s %s] ', str(g), str(cdtinst))
		cdtimax = BNode()
		g.add((cdtimax_i, time.inDateTime, cdtimax))
		g.add((cdtimax, RDF.type, time.DateTimeDescription))
		g.add((cdtimax, time.year, Literal(yr)))
		g.add((cdtimax, time.month, Literal(mo)))
		g.add((cdtimax, time.day, Literal(da)))
		g.add((cdtimax, time.hour, Literal(hr)))
		g.add((cdtimax, time.minute, Literal(min)))
		g.add((cdtimax, time.second, Literal(sec)))
		g.add((cdtimax, time.unitType, ut))
	else :		
		# if DTD exists, check its bound
		dtd = DateTimeDescription.DateTimeDescription.dtd_dtdc_map.get((g, cdtimax), None)
		if dtd :
			if dtd.lessthan(new_dtd) :
				logging.warning('assert_CDTInstant_value: new dtd greater than hasMax [%s %s] ', str(g), str(cdtinst))
		else :
			# if DTD does not exist, create it
			dtd = DateTimeDescription.DateTimeDescription(g, cdtimax)
		new_dtd.copy_into(dtd)
		dtd.update()
		
	ctime.changed_DCTInstants.add(cdtinst)
	
#---------------------------------print utilities ---------------------------------------
	
def print_subject(g, sub):
	for s,p,o in g.triples( (sub, None, None) ):
		print("predicate= " + str(p).rjust(70) + "     Value= " + str(o).rjust(70))
		
def print_CDTInterval(g, cdti) :
	if not (cdti, RDF.type, cot.CDateTimeInterval) in g :
		logging.warning('print_CDTInterval: CDT Interval does not exist [%s %s] ', str(g), str(cdti))
		return
		
	print("Constrained Date Time Interval: ", str(cdti))
	
	# print hasBeginning data
	cdt_instant = g.value(cdti, time.hasBeginning, any = False)
	if not cdt_instant :
		print("    Beginning CDT Instant: None")
	else :
		m = g.value(cdt_instant, cot.hasMin, any=False)
		if not m :
			print("        Beginning hasMin: None")
		else :
			dtd = g.value(m, time.inDateTime, any=False)
			if not dtd :
				print("    Beginning hasMin DTD: None")
			else :
				print("    Beginning hasMin DTD: ", str(dtd))
				val = get_dtd_val(g, dtd)
				print("            [", val, "]")
		
		m = g.value(cdt_instant, cot.hasMax, any=False)
		if not m :
			print("        Beginning hasMax: None")
		else :
			dtd = g.value(m, time.inDateTime, any=False)
			if not dtd :
				print("    Beginning hasMax DTD: None")
			else :
				print("    Beginning hasMax DTD: ", str(dtd))
				val = get_dtd_val(g, dtd)
				print("            [", val, "]")

	
	# print hasEnd data
	cdt_instant = g.value(cdti, time.hasEnd, any = False)
	if not cdt_instant :
		print("    End Instant: None")
	else :
		m = g.value(cdt_instant, cot.hasMin, any=False)
		if not m :
			print("        End hasMin: None")
		else :
			dtd = g.value(m, time.inDateTime, any=False)
			if not dtd :
				print("    End hasMin DTD: None")
			else :
				print("    End hasMin DTD: ", str(dtd))
				val = get_dtd_val(g, dtd)
				print("            [", val, "]")
		
		m = g.value(cdt_instant, cot.hasMax, any=False)
		if not m :
			print("        End hasMax: None")
		else :
			dtd = g.value(m, time.inDateTime, any=False)
			if not dtd :
				print("    End hasMax DTD: None")
			else :
				print("    End hasMax DTD: ", str(dtd))
				val = get_dtd_val(g, dtd)
				print("            [", val, "]")
				
def get_dtd_val(g, dtd) :
	ret = str(g.value(dtd, time.year, any=False))
	ret = ret + ", " + str(g.value(dtd, time.month, any=False))
	ret = ret + ", " + str(g.value(dtd, time.day, any=False))
	ret = ret + ", " + str(g.value(dtd, time.hour, any=False))
	ret = ret + ", " + str(g.value(dtd, time.minute, any=False))
	ret = ret + ", " + str(g.value(dtd, time.second, any=False))
	ret = ret + ", " + str(g.value(dtd, time.unitType, any=False))
	return(ret)