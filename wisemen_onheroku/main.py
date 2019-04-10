from flask import Flask, Response
from flask_restful import reqparse, abort, Api, Resource
import numpy as np
import json
import qrs  # My quotes recommendation software.

app = Flask(__name__)
api = Api(app)

# argument parsing
parser = reqparse.RequestParser()
parser.add_argument('query')
parser.add_argument('num')

class RecommendQuotes(Resource):
    def get(self):
        # use parser and find the user's query
        args = parser.parse_args()
        
        #-------------------------
        # Do validation of user's query request
        #
        # ... and handle exceptions.
        #-----------------------------------------
        
        # CASE 1: KEYS ARE ABSENT
        if not 'query' in args.keys() or not 'num' in args.keys(): 
          # Excep.1: No arg passed.
          if not args.keys():
            query_string = 'What is time?'
            num_quotes = 1
          # Excep.2: No 'query'.
          if not 'query' in args.keys():
            query_string = 'What is time?'
          # Excep.3: No 'num'.
          if not 'num' in args.keys():
            num_quotes = 1
            
        # CASE 2: KEYS ARE PRESENT. Both 'query' and 'num'.
        else:          
          # Excep.4: 'query' set to null
          if not args['query']:
            query_string = 'What is time?'
          # Excep.5: 'num' set to null
          if not args['num']:
            num_quotes = 1
          # Else: Good Case. Both 'query' and 'num' defined to something.
          if args['query']:
            query_string = args['query']
          if args['num']:
            try:
              num_quotes = int(args['num'])
            except ValueError: # if someone gives a string instead of num.
              num_quotes = 1
        #---------------Valid. Ends.------------------------------
        
        
        #DEBUG: print(query_string, num_quotes)
        
        # use quotation recommendation system to get quotes
        quotes_list = qrs.seek_advice(query_string, num_quotes)
        
        #DEBUG: quotes_list = [{'quote': query_string, 'author': num_quotes}]
        
        # create JSON object
        output = {'quotes': quotes_list}
        
        return output


# Setup the Api resource routing here
# Route the URL to the resource
api.add_resource(RecommendQuotes, '/quotes')



# Home page.
@app.route("/")
def hello():
    
    # For a Work around the heroku 30 second timeout, can refer to:
    # https://librenepal.com/article/flask-and-heroku-timeout/
    
    msg = """<html><head><title>Wise Men - RESTful web service for quotations.</title></head><body>
            <pre>
            <br>
            Wise Men <br>
            ---------- <br><br>
            Bask in the accidental Wisdom. <br>
            
            
            Examples:<br> 
            
            https://wisemen.herokuapp.com/<span style="color:blue">quotes</span>?<span style="color:grey">query</span>=<span style="color:red">time</span>&<span style="color:grey">num</span>=<span style="color:red">3</span>
            
            <a href="https://wisemen.herokuapp.com/quotes?query=time&num=3"><span style="color:purple">click to try</span></a><br>            
            
            https://wisemen.herokuapp.com/<span style="color:blue">quotes</span>?<span style="color:grey">query</span>=<span style="color:red">how to find happiness</span>&<span style="color:grey">num</span>=<span style="color:red">4</span>
            
            <a href="https://wisemen.herokuapp.com/quotes?query=how to find happiness&num=4"><span style="color:purple">click to try</span></a><br>
            
            
            <span style="color:#eeeeee">Manan Singh</span>   
            
            <hr>
            
            This web service lets you find top quotations matching any search string.
            It's an AI system which intelligently matches your query string 
            against 1000s of quotations of eminent personalities in its database
            and returns the top 'k' most similar ones.<br>
            
            Internally, it uses GloVe (similar to Word2Vec) word embeddings to
            turn your query into a 50-dimensional vector, and also turn all the
            quotations into vectors. Then, using K-nearest neighbor, with 
            distance metric being cosine-similarity, it returns top 'k' quotes 
            which are most similar to your query vector.
            
            Developed in python using gunicorn, Flask, Flask-RESTful, numpy, 
            gensim, and scikit-learn.
            
            <span style="color:#eeeeee">There's "accidental" in its tagline. Why?
            If you use it many times you will understand why :)
            </span>
            
            <!--
            Our gang includes:
            
            'Benjamin Franklin',
            ['Leonardo da Vinci','Abraham Lincoln', 'Jesus Christ', 'Isaac Newton', \n",
"             'Albert Einstein', 'Aristotle', 'Galileo Galilei', 'Alexander the Great', \n",
"            'Plato', 'William Shakespeare', 'Socrates', 'Martin Luther', 'Martin Luther King, Jr.',\n",
"            'Mahatma Gandhi', 'Charles Darwin', 'George Washington', 'Nikola Tesla', \n",
"            'Buddha', 'Julius Caesar', 'Napoleon Bonaparte', 'Thomas A. Edison', \n",
"            'Wolfgang Amadeus Mozart', 'Ludwig van Beethoven', 'Thomas Jefferson',\n",
"            'Marie Curie', 'Nelson Mandela', 'Henry Ford', 'Michelangelo', 'Homer',\n",
"            'Bill Gates', 'Confucius', 'Pythagoras', 'Louis Pasteur', 'Nicolaus Copernicus',\n",
"            'Walt Disney', 'Alan Turing' , 'Sun Tzu', 'Steve Jobs', 'Voltaire',\n",
"            'Charlie Chaplin', 'Charles Dickens', 'Mark Twain', 'Anne Frank', \n",
"            'Robert Frost', 'Winston Churchill']
            
             -->
            </pre> 
            </body></html>    
    """
                 
    return Response(msg, mimetype='text/html')



if __name__ == '__main__':
  app.run(debug=True)
  
