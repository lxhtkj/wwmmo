'''
Created on 27/02/2012

@author: dean@codeka.com.au
'''

from datetime import datetime
from google.appengine.ext import db
#import logging
import sector


class Empire(db.Model):
  '''Represents an empire, display name and whatnot.'''
  displayName = db.StringProperty()
  user = db.UserProperty()
  state = db.IntegerProperty()

  class State:
    INITIAL = 1
    REGISTERED = 2
    BANNED = 3

  @staticmethod
  def getForUser(user):
    result = Empire.all().filter("user", user).fetch(1, 0)
    if len(result) != 1:
      return None
    return result[0]

  def colonize(self, planet):
    '''Colonizes the given planet with a new colony.'''
    colony = Colony()
    colony.empire = self.key()
    colony.planet = planet.key()
    colony.sector = planet.star.sector.key()
    colony.star = planet.star.key()
    colony.population = 100.0
    colony.lastSimulation = datetime.now()
    colony.focusPopulation = 0.25
    colony.focusFarming = 0.25
    colony.focusMining = 0.25
    colony.focusConstruction = 0.25
    colony.put()

    def inc_colony_count():
      sector = planet.star.sector
      if sector.numColonies is None:
        sector.numColonies = 1
      else:
        sector.numColonies += 1
      sector.put()

    db.run_in_transaction(inc_colony_count)
    return colony

class Colony(db.Model):
  '''Represents a colony on a planet. A colony is owned by a single Empire.

  The colony is only "simulated" when a value actually changes. Normally, when we go to display
  a colony's data to the player, we take the value of lastSimulation, then run the simulation
  for all the time between lastSimulation and "now". (it's usually really basic stuff like
  "population = populationRate * (now - lastSimulation)" sort of thing). If you change a property
  on your colony, though, that'll change the various rates. So we need to run a simulation for
  eveything up to the point where the property changes, and save the new value.'''
  planet = db.ReferenceProperty(sector.Planet)
  star = db.ReferenceProperty(sector.Star)
  sector = db.ReferenceProperty(sector.Sector)
  empire = db.ReferenceProperty(Empire)
  population = db.FloatProperty()
  lastSimulation = db.DateTimeProperty()
  focusPopulation = db.FloatProperty()
  focusFarming = db.FloatProperty()
  focusMining = db.FloatProperty()
  focusConstruction = db.FloatProperty()

  @staticmethod
  def getForEmpire(empire_key):
    query = Colony.all().filter("empire", empire_key)
    return Colony._getForQuery(query)

  @staticmethod
  def getForSector(sector_model):
    query = Colony.all().filter("sector", sector_model)
    return Colony._getForQuery(query)

  @staticmethod
  def getForStar(star_model):
    query = Colony.all().filter("star", star_model)
    return Colony._getForQuery(query)

  @staticmethod
  def _getForQuery(query):
    colonies = []
    for colony in query:
      colonies.append(colony)
    return colonies


class BuildOperation(db.Model):
  '''Request a build operation that is currently in-progress.'''
  colony = db.ReferenceProperty(Colony)
  empire = db.ReferenceProperty(Empire)
  star = db.ReferenceProperty(sector.Star)
  designName = db.StringProperty()
  designKind = db.IntegerProperty()
  startTime = db.DateTimeProperty()
  endTime = db.DateTimeProperty()

  @staticmethod
  def getForStar(star_model):
    query = BuildOperation.all().filter("star", star_model)
    return BuildOperation._getForQuery(query)

  @staticmethod
  def getForEmpire(empire):
    query = BuildOperation.all().filter("empire", empire)
    return BuildOperation._getForQuery(query)

  @staticmethod
  def _getForQuery(query):
    buildops = []
    for buildop in query:
      buildops.append(buildop)
    return buildops


class Building(db.Model):
  '''A building represents a structure on a colony that gives it certain bonuses and abilities.'''
  colony = db.ReferenceProperty(Colony)
  empire = db.ReferenceProperty(Empire)
  star = db.ReferenceProperty(sector.Star)
  designName = db.StringProperty()
  buildTime = db.DateTimeProperty()

  @staticmethod
  def getForStar(star_model):
    query = Building.all().filter("star", star_model)
    return Building._getForQuery(query)

  @staticmethod
  def _getForQuery(query):
    buildings = []
    for building in query:
      buildings.append(building)
    return buildings


class EmpirePresence(db.Model):
  '''Represents the 'precense' of an empire in a star system.'''
  empire = db.ReferenceProperty(Empire)
  star = db.ReferenceProperty(sector.Star)
  totalGoods = db.FloatProperty()
  totalMinerals = db.FloatProperty()

  @staticmethod
  def getForStar(star_model):
    query = EmpirePresence.all().filter("star", star_model)
    return EmpirePresence._getForQuery(query)

  @staticmethod
  def _getForQuery(query):
    presences = []
    for presence in query:
      presences.append(presence)
    return presences


class Fleet(db.Model):
  '''Represents a fleet of ships.'''
  empire = db.ReferenceProperty(Empire)
  designName = db.StringProperty()
  numShips = db.IntegerProperty()
  state = db.IntegerProperty()
  stateStartTime = db.DateTimeProperty()
  star = db.ReferenceProperty(sector.Star)
  destinationStar = db.ReferenceProperty(sector.Star, collection_name='incoming_fleet_set')
  targetFleet = db.SelfReferenceProperty()
  targetColony = db.ReferenceProperty(Colony)

  @staticmethod
  def getForStar(star):
    query = Fleet.all().filter("star", star)
    return Fleet._getForQuery(query)

  @staticmethod
  def _getForQuery(query):
    fleets = []
    for fleet in query:
      fleets.append(fleet)
    return fleets