from django.conf import settings
from django.utils.timezone import now

from neo4j import GraphDatabase

class Neo4jUtils:
    """ Utils class to interact with neo4j """

    def __init__(
        self, 
        uri=settings.NEO4J_URI,
        username=settings.NEO4J_USERNAME,
        password=settings.NEO4J_PASSWORD
    ):
        self._driver = GraphDatabase.driver(uri, auth=(username, password), encrypted=False)
    
    @property
    def connection(self):
        return self._driver
    
    def close(self):
        self.connection.close()
    
    def session(self):
        return self.connection.session()
    
    def run(self, query):
        with self.session() as session:
            return session.run(query)


def date_now():
    """ Return the Date object of now """
    return now().date()