from flask import Flask, render_template, request
import pickle
import numpy as np
from keras.models import load_model
import json
import random
from fuzzywuzzy import process
import spacy
model =load_model("chatbot_6.h5")
intents = json.loads(open('chatbot_dataset.json').read())
intents_1=json.loads(open("food_document.json").read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))
nlp=spacy.load("en_core_web_sm")
items_append=[]
price_append=[]


all_stopwords = nlp.Defaults.stop_words
sentence_2=[]
sent=[]

#tokenize each word
def fuzzy(sentence):
    str2match=sentence
    strOptions=words
    Ratios=process.extract(str2match,strOptions)
    highest=process.extractOne(str2match,strOptions)
    return highest[0]
def clean_up_sentence(sentence):
        sentence_2=[]
        sent=[]
        sentence=str(sentence)
        sentence_1=fuzzy(sentence)
        sentence_words= nlp(sentence_1)
        l=[]
        for i in sentence_words:
             i=str(i)
             l.append(i)
      
        sentence_2.extend(l)
        # lemmatizing the words
        sent=[nlp(word.lower())[0].lemma_ for word in sentence_2]
        sent=[ w  for w in sent if w not in all_stopwords]
        return sent
def bow(sentence ,words):

    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words) 
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})   
    return return_list    


def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result


def chatbot_response(text):

    fuzzy_1=fuzzy(text)
    
    ints = predict_class(fuzzy_1, model)
    res = getResponse(ints, intents)
    tag = ints[0]['intent']
    
    if tag=="order_food":
         k=print_menu()
         n=len(k)
         for i in range(n):
             res=res+" \n "+ k[i]   
    elif tag=="Non-Veg Pizza":
         q=print_nonveg()
         n=len(q)
         for i in range(n):
             res=res+" \n "+ q[i] +","

    elif tag=="Veg Pizza":
         v=print_veg()
         n=len(v)
         for i in range(n):
             res=res+" \n "+ v[i] +","
    elif tag=="Beverages":
         B=print_bever()
         n=len(B)
         for i in range(n):
             res=res+" \n "+ B[i] +","
    elif tag=="Slides":
         s=print_slides()
         n=len(s)
         for i in range(n):
             res=res+" \n "+ s[i] +"," 
    elif tag=="food_item":
         if (len(list_rem)==0):
            f=cart(fuzzy_1,tag) 
            a,b=f
            items_append.extend(b)
            price_append.extend(a)
            total_items(price_append,items_append)
            res=res + ","+"\n "+total()
         elif (len(list_rem)!=0):
              if (list_rem[-1]):
                  res =remove(fuzzy_1)
              list_rem.clear()      
            
    elif tag=="confirm_order":
         con,price_c= total_items(price_append,items_append)
         n=len(con)
         for i in range(n):
             res=res+" \n "+ con[i] +","
         res=res+"\n"+"Total amount to be paid:"+str(price_c)  
    elif tag=="add_menu":
         rem_val=0
         add=print_menu()
         n=len(add)
         for i in range(n):
             res=res+" \n "+ add[i]  
    elif tag=="remove_menu":
         rem_val=0
         rem_val=rem_val+1
         rem,k= total_items(price_append,items_append)
         n=len(rem)
         for i in range(n):
             res=res+" \n "+ rem[i]
         remove2(rem_val) 
    elif tag=="cancel_food": 
         items_append.clear()
         price_append.clear()  
 

    
    return res
def print_nonveg():
    food=[]
    for intent in intents_1['intents']:
        if intent['tag']=="Non-Veg Pizza":
          for i in intent['items']:
            food.append(i)        
    return food       

#method to print the menu
def print_menu():
  l=[]
  for intent in intents_1['intents']:
      l.append(intent['tag'])
  return l

def print_veg():
    food=[]
    for intent in intents_1['intents']:
        if intent['tag']=="Veg Pizza":
            for i in intent['items']:
                food.append(i)        
    return food     


def print_bever():
    food=[]
    for intent in intents_1['intents']:
        if intent['tag']=="Beverages":
            for i in intent['items']:
                food.append(i)        
    return food    


def print_slides():
    food=[]
    for intent in intents_1['intents']:
        if intent['tag']=="Slides":
            for i in intent['items']:
                food.append(i)        
    return food   


list_items=[]
for intent in intents['intents']:
        if intent['tag']=="food_item":
            for i in intent['patterns']:
                list_items.append(i)
                      


def cart(res,tag):
    cart_1=[]
    price=[]
    str2match=res
    strOptions=list_items
    Ratios=process.extract(str2match,strOptions)
    highest=process.extractOne(str2match,strOptions)
    item_name=highest[0]
    cart_1.append(item_name)
    for intent in intents_1['intents']:
       if intent["tag"]=="Non-Veg Pizza" and item_name in intent["items"]:
               for i in intent['price']:
                   price.append(i)
       elif intent["tag"]=="Veg Pizza" and item_name in intent["items"]:
               for i in intent['price']:
                   price.append(i)
       elif intent["tag"]=="Beverages" and item_name in intent["items"]:
               for i in intent['price']:
                   price.append(i)
       elif intent["tag"]=="Slides" and item_name in intent["items"]:
               for i in intent['price']:
                   price.append(i)                                                                
    return (price,cart_1)   


def total_price(a):
    sum=0
    for i in a:
        sum=sum+i
    total=sum    
    return total
def total():
    total_value=total_price(price_append)
    print("Total no. of items in your cart: ")
    for i in items_append:
        print(i)
    return "price:"+ str(total_value) 

def total_items(a,b):
    total_list=[]
    total_list.extend(b)
    total_value=total_price(a)
    print("Total no. of items in your cart: ")
    for i in total_list:
        print(i)
    print("Total price:")    
    print(total_value) 
    return total_list,total_value  
 
def remove(text):
   str2match=text
   strOptions=list_items
   Ratios=process.extract(str2match,strOptions)
   highest=process.extractOne(str2match,strOptions)
   item_name_1=highest[0]
   for intent in intents_1['intents']:
       if  item_name_1 in items_append and item_name_1 in intent["items"]:
               for i in intent['price']:
                  price_append.remove(i)
               items_append.remove(item_name_1) 
               k="item is removed from the cart"
               return k  
   
list_rem=[]   
 
def remove2(val):
    if (val==1):
       list_rem.append(True)
       return  list_rem
    else :
       list_rem.append(False)
       return  list_rem      



app = Flask(__name__)

@app.route("/")
def home():    
    return render_template("home.html") 
@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    final_val= chatbot_response(userText)
    return final_val
if __name__ == "__main__":    
    app.run()