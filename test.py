import pandas as pd
import numpy as np
csvReader = pd.read_csv('../Spotify Analyzer/Data/CSV/grouped.csv', index_col=0)
        # opens the CSV file and uses column 0 as index (track names)

csName = "Barricades"



if csName not in csvReader.index:
    print("Not in index")
if csName in csvReader.index:
    print("Yes, in index")
    
    # result = df.loc[track_name, column_name]
    
    # If multiple rows match, result will be a Series
    # If one row matches, result will be a scalar
    # if isinstance(result, pd.Series):
    #    return result.sum()
    # else:
    #    return result



# if csvReader.loc[csName]

# if csName in csvReader["Playcount"].values:
    # print("yeah it is")

"""
if csvReader[csName].any():
    print("Song is there")
else:
    print("Song not found")
"""
# test = csvReader.loc[csName, "Playcount"]
# print(test)
# print(type(test))

# if isinstance(csvReader.loc[csName, "Total Time"], pd.Series)
#     None
#    # print("yes")
# if isinstance(csvReader.loc[csName, "Playcount"], np.int64):
#     None
#   print("int")