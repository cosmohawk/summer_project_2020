import re

def vec_for_learning(model, tagged_docs):
    '''
    Building the final vector feature for the classifier

    Parameters
    ----------
    model : the model
        (either: model_dbow, model_dmm, model_new)
    tagged_docs : tagged documents
        
    Returns
    -------
    tokens : targets, regressors
        
    '''
       
    sents = tagged_docs.values
    targets, regressors = zip(*[(doc.tags[0], model.infer_vector(doc.words, steps=20)) for doc in sents])
    return targets, regressors


def get_vectors(model, tagged_docs):
    '''
    Building feature vectors

    Parameters
    ----------
    model : the model
        (either: model_dbow, model_dmm, model_new)
        
    tagged_docs : tagged documents
        
    Returns
    -------
    tokens : targets, regressors
        
    '''
    
    sents = tagged_docs.values
    targets, regressors = zip(*[(doc.tags[0], model.infer_vector(doc.words, steps=20)) for doc in sents])
    return targets, regressors




def get_vectors_apply(model, docs_to_classify):
    '''
    

    Parameters
    ----------
    model : the model
        (either: model_dbow, model_dmm, model_new)
    docs_to_classify : documents to classify
        
    Returns
    -------
    tokens : regressors
        
    '''
    
    
    
    sents = docs_to_classify.values
    regressors = [model.infer_vector(doc.words, steps=20) for doc in sents]
    return regressors


def clean_text(text):
    '''
    

    Parameters
    ----------
    text : str
        test to clean
            
    Returns
    -------
    text : srt
        cleaned text
        
    '''
    
    text = re.sub(r"http\S+", "", str(text)) #remove urls
    text = re.sub(r'\S+\.com\S+','',str(text)) #remove urls
    text = re.sub(r'\@\w+','',str(text)) #remove mentions
    text =re.sub(r'\#','',str(text)) #remove hashtags
    text = re.findall(r'[A-Za-z]+',str(text))
    text = ' '.join(text) 
    return text