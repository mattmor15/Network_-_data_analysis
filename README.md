Wiki-Wandering: A tale of luck or skill?
================================================================
Datastory
-----------
Please visit our datastory here: [Wiki-Wandering: A tale of luck or skill?](https://sdhina.github.io/epfldatadynamos/)


About
-----------
Through Wikispeedia, a game which tracks user paths from a source to a target article through a abridged Wikipedia dataset,  West and Leskovec (2012) explore how humans navigate information networks on platforms like Wikipedia. Most notably, they note that compared to algorithmic shortest path methods, humans tend to use "hub" nodes and leverage content cues to guide their navigation. As such, using this same dataset, we proposed to (1) rank the performance of players in order to assess (2) how their success is tied to the content of articles as well as (3) how the interconnections between articles determine the outcome of their attempts relative to category connections proposed by wikipedia. Thus, we wanted to study these effects both to gain insight into how Wikipedia's structure shapes player navigation in the context of human search preferences, and to propose potential optimizations for its articles’ organization with regards to Wikispeedia.

From analysis of the network properties of the (abridged) Wikipedia as well as the performance of the players,
our data exploration highlights the nuanced nature of Wikispeedia navigation. While elements such as article length and network centrality do exert influence, much of the players' performance cannot be explained in simple manner, as Wikispeedia reflects the diversity and unpredictability of how individuals engage with the vast online encyclopedia.

Research questions
-----------------------
Within the Wikispeedia gameplay,  what potential optimizations can we suggest to both Wikipedia articles’ inner organization and linkage, given how they affect player navigation performance?

- Do the existing categories in this abridged Wikipedia reflect optimal shortest paths and/or the path effectively taken by players?
- What content features of Wikipedia articles (e.g., number of links, length of article, etc…) may influence the efficiency of player navigation in Wikispeedia?
- How do different network centrality and clustering measures affect player paths and can it give us insight into the way humans perceive and utilize hubs in an information network?
- How do the hub and content cue characteristics humans may be optimizing for compare with the organizational structure of Wikipedia's categories?


Methods
-----------


### Phase 1: Data Acquisition and Preprocessing

#### Step 1: Data Collection and Preprocessing
- We import the dataset built from a condensed version of Wikipedia (4604 articles), which includes data on article categories, linking relations, and player paths (both completed and uncompleted). The article names are URL-encoded, however, at this stage, we do not decode them since it is easier to load articles and find links with URL-encoded strings.

After preliminary visualization of our data, we go to Phase 2.

### Phase 2: Exploratory Data Analysis

#### Step 2: Initial Metrics For Articles and Players 
(note: not all variables are named as such in the current notebook, this is just for readability of the project proposal)

- Article Metrics: 
    - `ratio_I/O_links`: the ratio between the number of incoming/outgoing links for each article,
    - `article_length`: length of articles from the plain text size of each article,
    - `link_position`: identify the positions of links within the articles by parsing HTML,
    - `category_level`: identify main categories and two sublevels of categories.
- Player path specific metrics:
    - `completion`: binary indicator of whether a player completed a path,
    - `duration`: continuous variable representing the time taken to finish a path,
    - `average_duration_per_step`: total duration of attempt divided by the number of steps in the path,
    - `average_length_of_articles`: Get average length of articles in a player path,
    - `position_of_links_per_step`: we exclude paths with back clicks,
    - `average_position_per_step`: average positions of links for each path.
- Player specific information
    - `number_of_attempts_per_player`: note that this will be the number of attempts up to that attempt,
    - `win_rates`: number of games finished divided by the `number_of_attempts_per_player`.

We look at the distributions of some of these measures for articles and players to get an idea of the structure and what may influence player performance, before proceeding to more detailed analysis.

 
### Phase 3: Hub Identification and Path Analysis

#### Step 3: Building the Wikipedia Graph and Identifying Hubs

- Generate an unweighted graph using Networkx where articles are nodes and links are edges,
- We will characterize wikipedia article using NetworkX's centrality algorithms (`degree_centrality`, `betweenness_centrality`, `closeness_centrality`, `eigenvector_centrality_numpy`) on our wikipedia graph,
- We use NetworkX's clustering algorithm to determine `clustering_coefficients` of nodes.
- We compare the distribution of the graph properties for the articles actually used by players. We further compare the distribution of centrality distributions between all articles used by players vs. those most frequented in all games played.

#### Step 4: Pathway Analysis
- `shortest_path`: shortest paths computed by Dijkstra's algorithm (via NetworkX's shortest_path function) will be compared using the scipy.spatial.distance module. We will use this measure later as a confound, as the shortest possible path necessarily limits the player’s shortest path.
- Hub prioritization metric: For each path we calculate the number of hubs per path:
    - `nb_hubs_degree`
    - `nb_hubs_betweennes`
    - `nb_hubs_closeness`
    - `nb_hubs_eigenvector`
    - `nb_hubs_clustering`
- These values are divided by the number of steps in each path to normalize the metrics. (`*_hubs_percentage`)
- Category metric: We define the category metric based on wehther the starting and goal article is in the same main cateogry 
    - `same_category`: 1 if the same, 0 otherwise
 

### Phase 4: Comparative Analysis and Statistical Modeling

#### Step 5: Feature Impact Assessment
- Regression models from statsmodels library will be utilized to evaluate the effect of article features (`article_length`, `link_position`, `ratio_I/O_links`) on navigation performance, with pandas facilitating data manipulation for model inputs, all ultimately helping to quantify the features that differentiate difficulty of article navigation. Note, the model will be similar to the one presented below but we will use the three article features of interest as predictors in the same model, and as we have two dependent variables (completion and speed), we will build two models, one determining if our features affect the success of the attempt and the second assessing if our features affect the speed of completion of the attempt.

#### Step 6: Hub & Category Impact Assessment
- We look at the effects of (1) hub centrality measurements and (2) categories on player performance metrics (i.e., `completion` and total `duration`) using a simple linear regression model. We include the confounding variable `shortest_path` in the analysis.
- We implement multivariate models to determine the significance and extent of the influence of hubs, categories, and the optimal (shortest) possible path length on the player performance.

-----------------------


#### Model Variables

##### Dependent Variables:
- `completion`
- `duration`

##### Independent Variables (Predictors):
- **Feature Impact Assessment**: We fit all three variables in the same model:
  - `article_length`, `link_position`, `ratio_I/O_links`
- **Hub Prioritization**: A metric indicating how often players select hub nodes during navigation. We make six models per dependent vairable:
  - `nb_hubs_degree`
  - `nb_hubs_betweennes`
  - `nb_hubs_closeness`
  - `nb_hubs_eignevector`
  - `nb_hubs_clustering`
  - `*_hubs_percentage`
  - `same_category`

##### Covariates (Potential Confounds):
- `shortest_path`: accounting for inherent path difficulty.
  
---

Conclusions
============

Although our various analyses cannot give a definitive answer, we have gained insights on the player's behaviours and Wikipedia's organization.

- Do the existing categories in this abridged Wikipedia reflect optimal shortest paths and/or the path effectively taken by players?

**Answer**: Since the existing categories reduce the average shortest path lengths within themselves, and have a statistically significant influence on player behaviour, we can say that they do reflect the optimal paths and the ones taken by players. However, the extent of their influence is very small overall on player's performance given the small r-squared values from our tests.

- What content features of Wikipedia articles (e.g., number of links, length of article, etc…) may influence the efficiency of player navigation in Wikispeedia?

**Answer**: According to our model, the article’s length, its average input output link ratio and the position of hyperlinks within
them seem to affect how fast a player completes a game.
However, we note very low r-squared values, and the tests are rather
inconclusive since it is very likely that there are other variables at play here.

- How do different network centrality and clustering measures affect player paths and can it give us insight into the way humans perceive and utilize hubs in an information network?

**Answer**: Human players who choose to use more hubs are more likely to finish the game in a shorter time, although the number or proportion of hubs they use in their paths has less influence than their "luck" (the length of the optimal path between the source and target article in their run).

- How do the hub and content cue characteristics humans may be optimizing for compare with the organizational structure of Wikipedia's categories?

**Answer**:  From analyzing the distribution of centrality measures in articles used by players, it seems that many players favour hubs with a higher closeness centrality measure. At the same time, the shortest path inherent to the Wikipedia network still plays a larger role on whether or not a player finishes a game successfully as well as how fast they are. As a result, from our current analyses, it is hard to say whether Wikipedia's structure is optimized for efficiency navigation or not, or whether players' performance in the game is limited by the current structure. Further analyses, and possibly additional data gathering (e.g. via surveys) would be necessary to gain more insights on how and why players behave in a certain way, and if optimization can be achieved.

Contributions
=============
- Matthew: Data analysis (feature extraction, network centrality, hubs), data narrative,
- Marie-Lou: Data analysis (feature extraction, univariate models, feature impact assessment),
consolidating notebook
- Sara: Preliminary data analysis, interactive plotting, website building
- Enes: Data analysis (exploratory, categories, hubs), notebook
- Tong: Interactive plotting, data analysis (feature extraction, categories, multivariate models)

-----------------------

Robert West, Jure Leskovec. "Human Wayfinding in Information Networks". In: *Proceedings of the 21st international conference on World Wide Web* (WWW '12), April 2012, pp. 619–628. DOI: [10.1145/2187836.2187920](https://doi.org/10.1145/2187836.2187920).


