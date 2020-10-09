# A class for matching one list of strings to another from: https://medium.com/tim-black/fuzzy-string-matching-at-scale-41ae6ac452c2 and https://bergvca.github.io/2017/10/14/super-fast-string-matching.html
class StringMatch():
    
    def __init__(self, source_names, target_names):
        self.source_names = source_names
        self.target_names = target_names
        self.ct_vect      = None
        self.tfidf_vect   = None
        self.vocab        = None
        self.sprse_mtx    = None
        
    def tokenize(self, analyzer='char_wb', n=3):
        '''
        Tokenizes the list of strings, based on the selected analyzer
        :param str analyzer: Type of analyzer ('char_wb', 'word'). Default is trigram
        :param str n: If using n-gram analyzer, the gram length
        '''
        # Create initial count vectorizer & fit it on both lists to get vocab
        
        self.ct_vect = CountVectorizer(analyzer=analyzer, ngram_range=(n, n))
        self.vocab   = self.ct_vect.fit(self.source_names + self.target_names).vocabulary_
        # Create tf-idf vectorizer
        self.tfidf_vect  = TfidfVectorizer(vocabulary=self.vocab, analyzer=analyzer, ngram_range=(n, n))
        
        
    def match(self, ntop=1, lower_bound=0, output_fmt='df'):
        '''
        Main match function. Default settings return only the top candidate for every source string.
        
        :param int ntop: The number of top-n candidates that should be returned
        :param float lower_bound: The lower-bound threshold for keeping a candidate, between 0-1.
                                   Default set to 0, so consider all canidates
        :param str output_fmt: The output format. Either dataframe ('df') or dict ('dict')
        '''
        self._awesome_cossim_top(ntop, lower_bound)
        
        if output_fmt == 'df':
            match_output = self._make_matchdf()
        elif output_fmt == 'dict':
            match_output = self._make_matchdict()
            
        return match_output
        
        
    def _awesome_cossim_top(self, ntop, lower_bound):
        ''' https://gist.github.com/ymwdalex/5c363ddc1af447a9ff0b58ba14828fd6#file-awesome_sparse_dot_top-py '''
        # To CSR Matrix, if needed
        A = self.tfidf_vect.fit_transform(self.source_names).tocsr()
        B = self.tfidf_vect.fit_transform(self.target_names).transpose().tocsr()
        M, _ = A.shape
        _, N = B.shape

        idx_dtype = np.int32

        nnz_max = M * ntop

        indptr = np.zeros(M+1, dtype=idx_dtype)
        indices = np.zeros(nnz_max, dtype=idx_dtype)
        data = np.zeros(nnz_max, dtype=A.dtype)

        ct.sparse_dot_topn(
            M, N, np.asarray(A.indptr, dtype=idx_dtype),
            np.asarray(A.indices, dtype=idx_dtype),
            A.data,
            np.asarray(B.indptr, dtype=idx_dtype),
            np.asarray(B.indices, dtype=idx_dtype),
            B.data,
            ntop,
            lower_bound,
            indptr, indices, data)

        self.sprse_mtx = csr_matrix((data,indices,indptr), shape=(M,N))
    
    
    def _make_matchdf(self):
        ''' Build dataframe for result return '''
        # CSR matrix -> COO matrix
        cx = self.sprse_mtx.tocoo()

        # COO matrix to list of tuples
        match_list = []
        for row,col,val in zip(cx.row, cx.col, cx.data):
            match_list.append((row, self.source_names[row], col, self.target_names[col], val))

        # List of tuples to dataframe
        colnames = ['Row Idx', 'Title', 'Candidate Idx', 'Candidate Title', 'Score']
        match_df = pd.DataFrame(match_list, columns=colnames)

        return match_df

    
    def _make_matchdict(self):
        ''' Build dictionary for result return '''
        # CSR matrix -> COO matrix
        cx = self.sprse_mtx.tocoo()

        # dict value should be tuple of values
        match_dict = {}
        for row,col,val in zip(cx.row, cx.col, cx.data):
            if match_dict.get(row):
                match_dict[row].append((col,val))
            else:
                match_dict[row] = [(col, val)]

        return match_dict  

def clean_up(df,cols=[] ,delete=False):
    if delete:
        for col in cols:
            del df[col]
    else:
        for col in df.columns:
            if col not in cols:
                del df[col]

#extract year from float date (col) and create new column if property is newer then 2016
def extract_new_props(df,col):
    df[col]= df[col].astype(str).str[-4:-2]
    df[col].replace('n',21,inplace=True)    #assume nulls are new unit proven otherwise
    df[col] = df.loc[df[col].notnull()][col].astype(int)
    df['new'] = np.where((df[col]<21)&(df[col]>16) , True, False)
    df['new'] = np.where((df[col]==21) , np.nan, df.new)

def extract_nums(df,col):
    a = df[col].str.extractall('(\d+)').astype(float)
    df = df.join(a[0].unstack()).fillna('')
    return df

def extract_num(df,col):
    return df[col].str.extract('(\d+)').astype(float)

def replace_nan(df,cols=[],val=0,reverse=False):
    if not reverse:
        for col in cols:
            df[col].replace(np.nan,val,inplace=True)
    else:
        for col in cols:
            df[col].replace(val,np.nan,inplace=True)

#maybe replace nan back
def convert_to_numeric(df, col):
    #extract first group of number in string maybe improve so it caputres all numbers
    num = extract_num(df,col)
    replace_nan(num,num.columns)
    try:
       return num.astype(int)
    except ValueError:
       print(ValueError)

#maybe replace nan back
#concatenates string columns with empty values           
def combine_string_cols(df,cols=[],out='out'):
    replace_nan(df,cols,val='',reverse=False)
    address = ''
    for col in cols:
        address += df[col].astype(str) + ' '
    df[out]=address#.apply(lambda x: pyap.parse(x, country='US'))

#extract coordinates from geopandas frame
def extract_coor(gdf,col='geometry',out=['X','Y']):
    try:
        gdf[out[0]]=gdf[col].centroid.x
        gdf[out[1]]=gdf[col].centroid.y
    except:
        gdf[out[0]]=gdf[col].x
        gdf[out[1]]=gdf[col].y

def coor_to_geometry(df,col=['X','Y'],out='geometry'):
    df[out]=geopandas.points_from_xy(df[col[0]],df[col[1]])

#merge on value (df2 + df3) + df1 (origin)
def merge_extraction(dfs=[],on='prop_id',val=['units']):
    df2_cp = dfs[1].copy()  #copy datasets so no info is lost
    df3_cp = dfs[2].copy()
    clean_up(df2_cp,[on]+val)  #cleanup all values out of datasets to extract info from
    clean_up(df3_cp,[on]+val)  #cleanup all values out of datasets to extract info from
    df3_cp = df3_cp.merge(df2_cp,on=on,how='outer')
    return dfs[0].merge(df3_cp,on=on,how='left') #keep all values from original data frame don't care about values not in org

def fill_in_locs(df):
    df2 = pd.DataFrame(columns=df.columns)
    df_add = df.groupby('address')
    for add,df in df_add:
        if df.X_x.notnull().any() and len(df.index)>1:
            df.sort_values(by='X_x',inplace=True)
            df.fillna(method='ffill',inplace=True)
            df2 = df2.append(df)
    return df2

def find_missing(df,col):
    return df.loc[df[col].isnull()]

def df_to_geojson(df, properties, lat='latitude', lon='longitude'):
    geojson = {'type':'FeatureCollection', 'features':[]}
    for _, row in df.iterrows():
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}
        feature['geometry']['coordinates'] = [float(row[lon]),float(row[lat])]
        for prop in properties:
            if row[prop] != np.nan:
                feature['properties'][prop] = row[prop]
            else:
                feature['properties'][prop] = 'Info Not Availble'
        geojson['features'].append(feature)
    return geojson

def ckdnearest(gdA, gdB, num = 1):
    gdfs = [] 
    gdA = gdA.reset_index(drop=True)
    for i in range(0,num):
        gdB = gdB.reset_index(drop=True)
        nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
        nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
        btree = cKDTree(nB)
        dist, idx = btree.query(nA, k=1)
        gdfs.append(pd.concat(
                [gdA.reset_index(drop=True), gdB.loc[idx, gdB.columns != 'geometry'].reset_index(drop=True),
                pd.Series(dist, name='dist')], axis=1))
        gdB.drop(idx,inplace=True)
    gdf = pd.concat(gdfs)
    return gdf

#Converts a string column to a consistent case (title) and strip punctuation maybe don't convert nans?
def clean_string(df,col):
    return df[col].apply(lambda x:  " ".join(w.capitalize().translate(str.maketrans('', '', string.punctuation)) for w in str(x).split())).apply(lambda x: x.strip())

#maybe fix so it returns a df instead of altering original
#Converts all string column to a consistent case (title) and strip punctuation
def clean_strings(df):
    for col in df.columns:
       if df[col].dtype=='object':
           df[col] = clean_string(df,col)

#Partial Match merge: merges two data frames on known complete matches (on) keeping all values in left df and then returns a dataframe with full partial matches from the fuzz column
#Example merging addresses where the street numbers are consistent but the street names are not 
def merge_pm(df1,df2,l_on='',r_on='',l_fuzz='',r_fuzz='',thresh = 99, mn = 'match',keep_m = True):
    df = df1.merge(df2,left_on=l_on,right_on=r_on,how='left')
    df[mn] = df.apply(lambda x: fuzz.partial_ratio(str(x[l_fuzz]),str(x[r_fuzz])),axis=1)
    if keep_m:
       return df.loc[df[mn]>thresh]
    else:
       cols = df.columns.tolist()
       cols.remove(mn)
       return df.loc[df[mn]>thresh][cols]
