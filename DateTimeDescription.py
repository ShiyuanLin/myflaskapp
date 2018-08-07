import logging
import rdflib
from rdflib import Namespace
from rdflib.namespace import OWL, RDFS
from rdflib import Literal, BNode, URIRef, Graph

time = rdflib.Namespace('http://www.w3.org/2006/time#')	# specify the time namespace
cot = rdflib.Namespace('http://ontology.eil.utoronto.ca/TOVE2/ctime.rdf#')
test = rdflib.Namespace('http://ontology.eil.utoronto.ca/TOVE2/test.owl#')
rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

# ---------------------DateTimeDescription-------------------------------------------------------------
#
# DateTimeDescripton is a class used to represent a corredponding DateTimeDescription 
# concept in the time ontology, so that we do not have to
# manipulate RDF directly. If g and dtd are defined
# it loads the DateTimeDescriptoin properties from the RDF store into the object.


class DateTimeDescription:
	
	dtd_dtdc_map = dict()	# this maintains a mapping from a dtd URI and the corresponding object
	dtdc_changed = dict()	# True if dtdc changed but not stored
	
	# if the DTD already exists do not create a new one
	def __new__(cls, *args, **kwargs) :
		g = args[0]
		dtd = args[1]
		if dtd :
			d = DateTimeDescription.dtd_dtdc_map.get((g, dtd), None)
			if d :
				logging.info('DateTimeDescription init: DTD already exists [%s %s %s] ', str(g), str(dtd), str(d))
				return(d)
		return(super(DateTimeDescription, cls).__new__(cls))
			
	def __init__(self, g = None, dtd = None, yr=0, mo=0, da=0, hr=0, min=0, sec=0, ut=time.unitSecond) :
		#	g: the graph in which the triple resides
		#	dtd: the DateTimeDescription individual from which values are to be retrieved
		#	
		# if g and dtd are not defined, then the DTDC is initialized to the values
		# passed as parameters or their default
			
		self.graph = g
		self.dtd = dtd
		self.year = yr
		self.month = mo
		self.day = da
		self.hour = hr
		self.minute = min
		self.second = sec
		self.unitType = ut
		DateTimeDescription.dtdc_changed[self] = True
		if g and dtd : 
			if not self.objectify(g, dtd) : logging.debug('DateTimeDescription Init: No dtd in graph [%s %s]', str(g), str(dtd))

	# transform dtd from RDF store into DTD object
	def objectify(self, g, dtd) :
		if not (dtd, rdf.type, time.DateTimeDescription) in g : return(False)
		self.graph = g
		self.dtd = dtd
		self.year = g.value(dtd, time.year, any=False)
		self.month = g.value(dtd, time.month, any=False)
		self.day = g.value(dtd, time.day, any=False)
		self.hour = g.value(dtd, time.hour, any=False)
		self.minute = g.value(dtd, time.minute, any=False)
		self.second = g.value(dtd, time.second, any=False)
		self.unitType = g.value(dtd, time.unitType, any=False)
		DateTimeDescription.dtd_dtdc_map[(g, dtd)] = self
		DateTimeDescription.dtdc_changed[self] = False
		return(True)
	
	# copies values from self into the target DTDC
	def copy_into(self, dtdc2) :
		# note that the graph and dtd remain the same
		dtdc2.year = self.year
		dtdc2.month = self.month
		dtdc2.day = self.day
		dtdc2.hour = self.hour
		dtdc2.minute = self.minute
		dtdc2.second = self.second
		dtdc2.unitType = self.unitType
		DateTimeDescription.dtdc_changed[dtdc2] = True		# so that it can be written out

	# creates a new DTD which is the result of adding self and dtdc2
	def add(self, dtdc2) :
		new_dtdc = DTDC()
		new_dtdc.year = self.year + dtdc2.year
		new_dtdc.month = self.month + dtdc2.month
		new_dtdc.day = self.day + dtdc2.day
		new_dtdc.hour = self.hour + dtdc2.hour
		new_dtdc.minute = self.minute + dtdc2.minute
		new_dtdc.second = self.second + dtdc2.second
		new_dtdc.unitType = self.unitType
		new_dtdc.g = None
		new_dtdc.dtd = None
		
	def subtract(self, dtdc2) :
		new_dtdc = DTDC()
		new_dtdc.year = self.year - dtdc2.year
		new_dtdc.month = self.month - dtdc2.month
		new_dtdc.day = self.day - dtdc2.day
		new_dtdc.hour = self.hour - dtdc2.hour
		new_dtdc.minute = self.minute - dtdc2.minute
		new_dtdc.second = self.second - dtdc2.second
		new_dtdc.unitType = self.unitType
		new_dtdc.g = None
		new_dtdc.dtd = None
		
	# store the DTD object into the RDF store
	def update(self) :
		if  self.graph and self.dtd :
			self.pprint()
			set_delete(self.graph, self.dtd, time.year, Literal(self.year))
			set_delete(self.graph, self.dtd, time.month, Literal(self.month))
			set_delete(self.graph, self.dtd, time.day, Literal(self.day))
			set_delete(self.graph, self.dtd, time.hour, Literal(self.hour))
			set_delete(self.graph, self.dtd, time.minute, Literal(self.minute))
			set_delete(self.graph, self.dtd, time.second, Literal(self.second))
			set_delete(self.graph, self.dtd, time.unitType, self.unitType)
			DateTimeDescription.dtdc_changed[self] = False
			return(True)
		logging.debug('DTDC.update: No graph or dtd [%s %s]', str(g), str(dtd))
		return(False)	# fail if no g and dtd known

	# remove a DTD from both the object store and the RDF triple store
	def remove(self) :
		del DateTimeDescription.dtd_dtdc_map[(self.graph, self.dtd)]	# remove from map
		del DateTimeDescription.dtdc_changed[self]						# remove from change tracker
		self.graph.remove((self.dtd, None, None))	# remove all occurrences in RDF
				
	# determines if self is less than another DTDC object
	def lessthan(self, dtdc2) :
		if self.year < dtdc2.year : return(True)		
		if (self.year > dtdc2.year) or ((self.year == dtdc2.year) and (self.unitType == time.unitYear)) : return(False)
		if self.month < dtdc2.month : return(True)
		if (self.month > dtdc2.month) or ((self.month == dtdc2.month) and (self.unitType == time.unitMonth)) : return(False)
		if self.day < dtdc2.day : return(True)
		if (self.day > dtdc2.day) or ((self.day == dtdc2.day) and (self.unitType == time.unitDay)) : return(False)
		if self.hour < dtdc2.hour : return(True)
		if (self.hour > dtdc2.hour) or ((self.hour == dtdc2.hour) and (self.unitType == time.unitHour)) : return(False)
		if self.minute < dtdc2.minute : return(True)
		if (self.minute > dtdc2.minute) or ((self.minute == dtdc2.minute) and (self.unitType == time.unitMinute)) : return(False)
		if self.second < dtdc2.second : return(True)
		if (self.second > dtdc2.second) or ((self.second == dtdc2.second) and (self.unitType == time.unitSecond)) : return(False)
		return(False)	# they are equal
		
	def greaterthan(self, dtdc2) :
		if self.year > dtdc2.year : return(True)		
		if (self.year < dtdc2.year) or ((self.year == dtdc2.year) and (self.unitType == time.unitYear)) : return(False)
		if self.month > dtdc2.month : return(True)
		if (self.month < dtdc2.month) or ((self.month == dtdc2.month) and (self.unitType == time.unitMonth)) : return(False)
		if self.day > dtdc2.day : return(True)
		if (self.day < dtdc2.day) or ((self.day == dtdc2.day) and (self.unitType == time.unitDay)) : return(False)
		if self.hour > dtdc2.hour : return(True)
		if (self.hour < dtdc2.hour) or ((self.hour == dtdc2.hour) and (self.unitType == time.unitHour)) : return(False)
		if self.minute > dtdc2.minute : return(True)
		if (self.minute < dtdc2.minute) or ((self.minute == dtdc2.minute) and (self.unitType == time.unitMinute)) : return(False)
		if self.second > dtdc2.second : return(True)
		if (self.second < dtdc2.second) or ((self.second == dtdc2.second) and (self.unitType == time.unitSecond)) : return(False)
		return(False)	# they are equal
		
	def pprint(self) :
		print("Graph = ", str(self.graph))
		print("DTD = ", str(self.dtd))
		print("UnitType = ", str(self.unitType))
		print("Year = ", self.year)
		print("Month = ", self.month)
		print("Day = ", self.day)
		print("Hour = ", self.hour)
		print("Minute = ", self.minute)
		print("Second = ", self.second)	

def set_delete(g, s, p, o) :
	if o :
		g.set((s,p,o))
	else :
		g.remove((s, p, None))
