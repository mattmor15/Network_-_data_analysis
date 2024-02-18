import uuid
import os
import urllib.parse
from bs4 import BeautifulSoup, Comment
import pandas as pd
import networkx as nx

def read_tsv(graphs_path, file_name, names=None):
    ''' 
    Read a TSV file
    
    Parameters
    ==============
    graphs_path: path to the directory containing the data
    file_name: name of the file to read
    names: optional columns names for the dataframe
    
    Outputs
    ==============
    panda dataframe containing the data from the TSV file
    
    '''
    
    file_path = os.path.join(graphs_path, f'{file_name}.tsv')
    
    # Extract column name from the file
    if not names:
        with open(file_path, 'r') as file:
            for line in file:
                if 'FORMAT' in line:
                    format_line = line
                    break
        names = format_line.split()[2:]
    
    return pd.read_csv(file_path,
                      delimiter='\t', comment='#', header=0, names=names)

def article_length(article_path, article_name):
    ''' 
    Compute the length of an article, i.e. the number of words
    
    Parameter
    ==============
    article_name: name of the Wikipedia article
    
    Output: 
    ==============
    nb_words: number of words found in the article
    
    '''
    
    article = article_path + article_name + '.txt'
    
    nb_words = 0
    with open(article, encoding="utf8") as f:
        for line in f:
            nb_words += len(line.split())
    return nb_words


def gen_uniq_str(str_):
    ''' 
    Generate a unique string with the same length from a given input string
    '''
    return uuid.uuid4().hex[:len(str_) + 1]

def find_html_position(source, targets):
    '''
    Find the HTML position of a list of link targets in a source article
    
    Parameters
    ==============
    source: name of the source article
    targets: list of the target articles
    
    Output
    ==============
    pos: positions of the links 
    '''
   
    article_quote = source
    file_path = os.path.join('data/wpcd/wp/', article_quote[0].lower(), f'{article_quote}.htm')
    
    try:
        with open(file_path) as f:
            art_html = f.read()
    except Exception as e:
        print(f"Error reading HTML file for source: {source}")
        return -1

    soup = BeautifulSoup(art_html, features="html.parser")
    
    # Remove unnecessary elements from the HTML
    for element in soup(["script", "style", "head"]):
        element.extract()

    comments = soup.findAll(string=lambda string: isinstance(string, Comment))
    for comment in comments:
        comment.extract()  # Remove HTML comments

    locators = []
    
    for tgt in targets:
        try:
            locator = gen_uniq_str(urllib.parse.unquote_plus(tgt))
            locators.append(locator)
            # Replace the anchor tag with the locator
            soup.select_one(f'a[href*="/{urllib.parse.quote_plus(tgt)}.htm"]').replace_with(locator)
        except Exception as e:
            k = f'a[href*="{urllib.parse.quote_plus(tgt)}.htm"]'
            #print(k)
            #print(source, tgt)
            pass
    
    # Clean and concatenate the text from the HTML
    text = " ".join(soup.text.split())
    
    # Calculate the relative positions of targets in the text
    pos = {}
    for iloc, loc in enumerate(locators):
        pos[targets[iloc]] = text.find(loc) / len(text)
        
    return pos

def calculate_positions(arts):
    '''
    Compute the average positions of links along a path
    
    Parameter
    ==============
    arts: list of articles in a path
    
    Output
    ==============
    average positions of links in a path
    '''
    
    if '<' in arts: return [float('nan')]
    articles = arts.split(';')
    
    if len(articles) < 2: return [float('nan')]
    
    positions = []
    
    art_idx = 0
    
    for idx, art in enumerate(articles[1:]):
        art0 = articles[art_idx]
        try:          
            positions.append(link_network_pos[(link_network_pos['source'] == art0)
                            & (link_network_pos['target'] == art)]['position'].values[0])
            art_idx = idx+1
        except:
            print(art0, art, arts)
            return [float('nan')]
    
    return positions


def filter_rows_by_values(df, col, values):
    '''
    Filter rows of a dataframe by values
    
    Parameters
    ==============
    df: dataframe
    col: column name
    values: values to discriminate
    
    Output
    ==============
    filtered dataframe
    '''
    return df[~df[col].isin(values)]


# Functions for Degree Centrality, betweenness centrality, closeness centrality and eingenvector centrality
def get_degree_centrality(G):
    return nx.degree_centrality(G)

def get_betweenness_centrality(G):
    return nx.betweenness_centrality(G)

def get_closeness_centrality(G):
    return nx.closeness_centrality(G)

def get_eigenvector_centrality(G):
    return nx.eigenvector_centrality(G)

def normalize(data, column_name):
    ''' 
    Normalize a column in a dataframe 
    
    Parameters
    ==============
    data: dataframe
    column_name: name of the column to normalize
    
    Output
    ==============
    normalized column of the dataframe
    '''
    return (data[column_name] - data[column_name].mean())/data[column_name].std()


# Define functions to extract the source and target from the path
def extract_source(path):
    '''
    Extract the source from a path
    
    Parameter
    ==============
    path: list of articles browsed by a player
    
    Output
    ==============
    source article
    '''
    return path.split(';')[0] if pd.notnull(path) else None

def extract_target(path):
    '''
    Extract the target article from a path
    
    Parameter
    ==============
    path: list of articles browsed by a player
    
    Output
    ==============
    target article
    '''
    return path.split(';')[-1] if pd.notnull(path) else None

def count_hubs(path, hubs_set):
    '''
    Count the number of hubs in a path
    
    Parameters
    ==============
    path: list of articles browsed by a player
    hubs_set: list of hubs
    
    Output
    ==============
    Number of hubs in a path
    '''
    # Split the path into individual nodes
    nodes = path.split(';')
    # Count the number of nodes in the path that are in the set of hubs
    hub_count = sum(node in hubs_set for node in nodes)
    return hub_count

def calculate_shortest_path_length(row, graph):
    '''
    Calculate the shortest path length
    
    Parameters
    ==============
    row: row of a dataframe
    graph: nx graph
    
    Output
    ==============
    length of the shortest path
    '''
    try:
        # Compute the shortest path length between source and target
        path_length = nx.shortest_path_length(graph, source=row['source'], target=row['target'])
        return path_length
    except nx.NetworkXNoPath:
        # If there is no path between source and target, return None or some indicator like -1
        return None
    except nx.NodeNotFound:
        # If the source or target node does not exist in the graph, return None or some indicator like -1
        return None

def count_unique_categories(path, node_to_category):
    '''
    Count unique categories in a path
    
    Parameter
    ==============
    path: list of articles browsed by a player
    
    Output
    ==============
    number of unique categories encountered
    '''
    if pd.isna(path):
        return 0
    # Split the path into nodes.
    nodes = path.split(';')
    # Find the category for each node, count unique categories.
    categories = [node_to_category.get(node) for node in nodes if node in node_to_category]
    return len(set(categories))

def have_common_category(start, target, article_to_categories):
    '''
    Estimate if two articles (start and target) belongs to the same category
    
    Parameter
    ==============
    start: source article
    target: final article to reach
    article_to_categories: dictionnary of category per article
    
    Output
    ==============
    list of binary variable to indicate if the two articles have the same category (1) or not (0)
    '''
    start_categories = set(article_to_categories.get(start, []))
    target_categories = set(article_to_categories.get(target, []))
    return int(len(start_categories.intersection(target_categories)) > 0)

