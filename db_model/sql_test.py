from sqlalchemy_declarative import User, Base
from sqlalchemy import create_engine
engine = create_engine('sqlite:///proxy.db', echo=True)
Base.metadata.bind = engine
from sqlalchemy.orm import sessionmaker
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()
# Make a query to find all Persons in the database
session.query(User).all()
# Return the first Person from all Persons in the database
person = session.query(User).first()
person.username
# Find all Address whose person field is pointing to the person object
#session.query(Address).filter(Address.person == person).all()
# Retrieve one Address whose person field is point to the person object
#session.query(Address).filter(Address.person == person).one()
#address = session.query(Address).filter(Address.person == person).one()
#address.post_code
