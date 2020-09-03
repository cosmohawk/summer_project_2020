def vec_for_learning(model, tagged_docs):
    '''
    

    Parameters
    ----------
    model :
        
    tagged_docs : 
        
    Returns
    -------
    tokens : targets, regressors
        
    '''
    
    
    sents = tagged_docs.values
    targets, regressors = zip(*[(doc.tags[0], model.infer_vector(doc.words, steps=20)) for doc in sents])
    return targets, regressors


def get_vectors(model, tagged_docs):
    '''
    

    Parameters
    ----------
    model :
        
    tagged_docs : 
        
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
    model :
        
    docs_to_classify : 
        
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
    model :
        
    tagged_docs : 
        
    Returns
    -------
    tokens : tergets, regressors
        
    '''
    
    text = re.sub(r"http\S+", "", str(text)) #remove urls
    text = re.sub(r'\S+\.com\S+','',str(text)) #remove urls
    text = re.sub(r'\@\w+','',str(text)) #remove mentions
    text =re.sub(r'\#','',str(text)) #remove hashtags
    text = re.findall(r'[A-Za-z]+',str(text))
    text = ' '.join(text) 
    return text