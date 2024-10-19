from speakeasypy import Speakeasy, Chatroom
from typing import List
import time
from rdflib.namespace import Namespace, RDF, RDFS, XSD
from rdflib.term import URIRef, Literal
import csv
import json
import networkx as nx
import pandas as pd
import rdflib
from collections import defaultdict, Counter


DEFAULT_HOST_URL = 'https://speakeasy.ifi.uzh.ch'
listen_freq = 2
WD = Namespace('http://www.wikidata.org/entity/')
WDT = Namespace('http://www.wikidata.org/prop/direct/')
SCHEMA = Namespace('http://schema.org/')
DDIS = Namespace('http://ddis.ch/atai/')



class KGGraph:
    def __init__(self):
        self.graph = rdflib.Graph()
        self.graph.parse('DataSet/ddis-movie-graph.nt/14_graph.nt', format='turtle')
        print("Parse is done")

    def validate_and_clean_query(self, query):
        """ Strip unnecessary triple quotes and whitespace. """
        # Strip triple quotes if they are found at the start and end of the query string
        query = query.strip().strip("'''").strip()
        # Remove new lines and redundant spaces
        query = ' '.join(query.split())
        return query
    
    def graph_query(self, query):
        try:
            # Validate and clean the query
            query = self.validate_and_clean_query(query)
            print("Executing query:", query)  # Debug print to check the final query

            # Execute the query
            results = self.graph.query(query)

            # Print each result
            result_list = [', '.join(str(item) for item in row) for row in results]
            for result in result_list:
             print(result)
       

            return result_list
        except Exception as e:
            print(f"Failed to execute query due to an error: {e}")
            return None
        
class Agent:
    def __init__(self, username, password, demoKG):
        self.username = username
        self.speakeasy = Speakeasy(host=DEFAULT_HOST_URL, username=username, password=password)
        self.speakeasy.login()  # This framework will help you log out automatically when the program terminates.
        self.demoKG = demoKG

    def listen(self):
        while True:
            rooms: List[Chatroom] = self.speakeasy.get_rooms(active=True)
            for room in rooms:
                if not room.initiated:
                    room.initiated = True
                    #room.post_messages(f'Hello! This is a welcome message from {room.my_alias}.')
                     # Retrieve messages from this chat room.
                # If only_partner=True, it filters out messages sent by the current bot.
                # If only_new=True, it filters out messages that have already been marked as processed.
                
                for message in room.get_messages(only_partner=True, only_new=True):
                    
                    #print("1st,",len(room.get_messages(only_partner=False, only_new=True)))
                   # print(f"\t- Chatroom {room.room_id} - new message #{message.ordinal}: '{message.message}' - {self.get_time()}")
                    #print("Message is",{message.author_alias})
                    result = self.demoKG.graph_query(message.message)
                    print("Result is", result)
                   
                        
                        
                    
                   # Send a message to the corresponding chat room using the post_messages method of the room object.
                    
                    #print("2nd",len(room.get_messages(only_partner=False, only_new=True)))
                    
                    room.post_messages(f"The answer is: '{result}' ")
                    #print("3rd",len(room.get_messages(only_partner=False, only_new=True)))
                    room.mark_as_processed(message)
                   
                   

                for reaction in room.get_reactions(only_new=True):
                    print(f"\t- Chatroom {room.room_id} - new reaction #{reaction.message_ordinal}: '{reaction.type}' - {self.get_time()}")
                    room.post_messages(f"Received your reaction: '{reaction.type}' ")
                    room.mark_as_processed(reaction)

            time.sleep(listen_freq)

    @staticmethod
    def get_time():
        return time.strftime("%H:%M:%S, %d-%m-%Y", time.localtime())

# Execution setup
if __name__ == '__main__':
    demoKG = KGGraph()
    result = demoKG.graph_query("""
    SELECT ?subject ?label WHERE {
        ?subject rdfs:label ?label .
    }
""")
    #demo_bot = Agent("mehmetemir.hocaoglu", "M.emir2001", demoKG)
    #demo_bot.listen()
