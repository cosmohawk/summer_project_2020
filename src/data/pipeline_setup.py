import os

def build_data_dir(fp):
    '''
    Function to which checks for standard-format data directory at the location specified.
    If directory or any of its sub-folders do not exist, this creates them.
    
    Parameters
    ----------
    fp : str
        The filepath (preferably absolute) to the parent location of the data directory.
    '''
    dirs = [os.path.join(fp, 'data/'),] # Initialise list of directories with the root of the data directory structure
    dirs.append(os.path.join(dirs[0], 'raw/')) # append data directory sub-folders to list of dirs to check/create
    dirs.append(os.path.join(dirs[0], 'raw/users_tweets'))
    dirs.append(os.path.join(dirs[0], 'processed/')) 
    dirs.append(os.path.join(dirs[0], 'outputs/'))
    
    exists = [os.path.isdir(folder) for folder in dirs] # create list of checks whether directories exist
    
    if all(exists):
        print('Data directory & sub-directories already exist, skipping.')
    else:
        for folder, present in zip(dirs, exists):
            if not present:
                print('Creating directory '+folder)
                os.mkdir(folder)

def install_nltk_data():
    '''
    Download and install/update corpora from nltk which are used in the project.
    '''
    import nltk

    corpus_list = ['stopwords', 'punkt', 'wordnet']

    for corpus in corpus_list:
        nltk.download(corpus)

