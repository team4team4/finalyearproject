import spacy

# Load the model
nlp = spacy.load("en_core_web_sm")

# Test the model
doc = nlp("This is a test sentence.")
for token in doc:
    print(token.text, token.pos_, token.dep_)

