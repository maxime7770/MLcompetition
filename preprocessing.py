from xgboost import XGBClassifier, cv
import geopandas as gpd
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np
from sklearn import model_selection
from sklearn.metrics import roc_auc_score
from sklearn import preprocessing
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score
import xgboost
from joblib import dump, load
from datetime import datetime
from scipy.stats import boxcox


change_type_map = {
    "Demolition": 0,
    "Road": 1,
    "Residential": 2,
    "Commercial": 3,
    "Industrial": 4,
    "Mega Projects": 5,
}
# to delete last classes

change_type_map = {
    "Demolition": 0,
    "Road": 1,
    "Residential": 2,
    "Commercial": 3,
    "Industrial": 4
}

train_df = gpd.read_file("train.geojson", index_col=0)
test_df = gpd.read_file("test.geojson", index_col=0)


# trying to delete last classes


train_df = train_df.drop(
    train_df[(train_df["change_type"] == "Mega Projects")].index)


# and thus drop if status_sate=excavation because it is essentially in the 5th class

# train_df = train_df.drop(
#     train_df[
#         (train_df["change_status_date1"] == "Excavation")
#         | (train_df["change_status_date2"] == "Excavation")
#         | (train_df["change_status_date3"] == "Excavation")
#         | (train_df["change_status_date4"] == "Excavation")
#         | (train_df["change_status_date5"] == "Excavation")
#     ].index
# )

# test_df = test_df.drop(
#     test_df[
#         (test_df["change_status_date1"] == "Excavation")
#         | (test_df["change_status_date2"] == "Excavation")
#         | (test_df["change_status_date3"] == "Excavation")
#         | (test_df["change_status_date4"] == "Excavation")
#         | (test_df["change_status_date5"] == "Excavation")
#     ].index
# )

# dropping rows if "Na" values in change_status_datei

# train_df = train_df.drop(
#     train_df[
#         (train_df["change_status_date1"] == "Na")
#         | (train_df["change_status_date2"] == "Na")
#         | (train_df["change_status_date3"] == "Na")
#         | (train_df["change_status_date4"] == "Na")
#         | (train_df["change_status_date5"] == "Na")
#     ].index
# )
# test_df = test_df.drop(
#     test_df[
#         (test_df["change_status_date1"] == "Na")
#         | (test_df["change_status_date2"] == "Na")
#         | (test_df["change_status_date3"] == "Na")
#         | (test_df["change_status_date4"] == "Na")
#         | (test_df["change_status_date5"] == "Na")
#     ].index
# )


# creating vectors of 0 or 1 if the construction finished before the 5 days or not:
# t_train = train_df[
#     [
#         "change_status_date1",
#         "change_status_date2",
#         "change_status_date3",
#         "change_status_date4",
#         "change_status_date5",
#     ]
# ].values

# finished_train = []
# for i in range(t_train.shape[0]):
#     if "Construction Done" not in t_train[i, :]:
#         finished_train.append(1)
#     else:
#         finished_train.append(0)
# train_df["finished"] = np.array(finished_train)

# t_test = test_df[
#     [
#         "change_status_date1",
#         "change_status_date2",
#         "change_status_date3",
#         "change_status_date4",
#         "change_status_date5",
#     ]
# ].values

# finished_test = []
# for i in range(t_test.shape[0]):
#     if "Construction Done" not in t_test[i, :]:
#         finished_test.append(1)
#     else:
#         finished_test.append(0)
# test_df["finished"] = np.array(finished_test)


# adding time differences

train_df["diff1"] = (
    train_df["date2"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
    - train_df["date1"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
).apply(lambda x: x.days)
train_df["diff2"] = (
    train_df["date3"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
    - train_df["date2"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
).apply(lambda x: x.days)
train_df["diff3"] = (
    train_df["date4"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
    - train_df["date3"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
).apply(lambda x: x.days)
train_df["diff4"] = (
    train_df["date5"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
    - train_df["date4"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
).apply(lambda x: x.days)


test_df["diff1"] = (
    test_df["date2"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
    - test_df["date1"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
).apply(lambda x: x.days)
test_df["diff2"] = (
    test_df["date3"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
    - test_df["date2"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
).apply(lambda x: x.days)
test_df["diff3"] = (
    test_df["date4"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
    - test_df["date3"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
).apply(lambda x: x.days)
test_df["diff4"] = (
    test_df["date5"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
    - test_df["date4"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y"))
).apply(lambda x: x.days)

# Utils


# def moy(L):
#     if len(L) == 0:
#         return 0
#     return sum(L)/len(L)


# def most_freq(lst):
#     if len(lst) == 0:
#         return 13
#     return max(set(lst), key=lst.count)


# steps_tuple = [('Greenland', 'Land Cleared'),
#                ('Prior Construction',),
#                ('Materials Dumped',),
#                ('Construction Started', 'Excavation'),
#                ('Construction Midway',),
#                ('Construction Done', 'Operational'),
#                ]
# format_date = "%d-%m-%Y"
# N_a = len(steps_tuple)-1
# steps = ()
# for step_tuple in steps_tuple:
#     steps += step_tuple


# # Step (string) to avancement (int)
# def step2av(step):
#     '''
#     Input: step is a string
#     Output: av is an int representing avancement
#     '''
#     for i, steps in enumerate(steps_tuple):
#         if step in steps:
#             return i
#     if step != 'NA':
#         print(step)
#     return 'NA'


# def extract_features_date(df):
#     global n_na_found, n_na_only_found
#     n_na_found = 0
#     n_na_only_found = 0
#     verbose = False

#     # Step are strings. Steps in the same tuple are considered similar enough. The order of steps_tuple defines the order of steps in reality.

#     int_adv_to_D = [list() for _ in range(N_a)]
#     int_adv_to_M = [list() for _ in range(N_a)]

#     # Extract duration and month where each advancement was made.

#     def augment_date(row):

#         # Feature for describing if construction is done at date5
#         is_constructed = int(row['change_status_date5'] == 'Construction Done')

#         # List [duration_for_reaching_avancement_A for A in Avancements]
#         duration_for_reaching = ['ToCompute' for _ in range(N_a)]
#         # List [int_representing_month_where_advancementA_was_made for A in Avancements]
#         month_where_was = ['ToCompute' for _ in range(N_a)]
#         # [0,0,1,3,5]
#         L_int_steps = [step2av(row[status]) for status in (
#             'change_status_date1', 'change_status_date2', 'change_status_date3', 'change_status_date4', 'change_status_date5')]

#         # If some steps are NA return list of unknown
#         if 'NA' in L_int_steps:
#             # + ["Unknown" for _ in range(N_a)]   #MONTHS
#             return [is_constructed] + ["Unknown" for _ in range(N_a)]

#         # Each time we do an advancement (ie step changes), we fill the list duration_for_reaching with the diff time.
#         # If severals advancements are made we divise the duration by the number of advancements.
#         # To implement: instead of divising by the duration, for each advancement A, we do duration(A) = D(A) / Sum_A(D(A)) where D(A) is the mean duration of the advancement, computed on data where advancement was reached in one step
#         for k in range(len(L_int_steps)-1):
#             int_step = L_int_steps[k]
#             int_step_next = L_int_steps[k+1]
#             if verbose:
#                 print("STEP", k, int_step, int_step_next)

#             if int_step_next > int_step:
#                 if verbose:
#                     print(
#                         f"step {int_step} to step {int_step_next} happened at time {k}")
#                 for u in range(int_step, int_step_next):
#                     # If severals advancement are made between only two dates, the duration of each advancement is the duration divided by the number of dates-1.
#                     duration_for_reaching[u] = (
#                         row['diff' + str(k+1)] // (int_step_next-int_step)) / (3600 * 24 * 30.5)

#                     # The month where EVERY (Implement: not every advancements happend at the same time...) advancements are made is the month of the date between two dates
#                     t1 = datetime.timestamp(datetime.strptime(
#                         row["date" + str(k+1)], format_date))
#                     t2 = datetime.timestamp(datetime.strptime(
#                         row["date" + str(k+2)], format_date))
#                     month_where_was[u] = datetime.fromtimestamp(
#                         t1 + (t2-t1)/2).month
#                 if int_step_next - int_step == 1:
#                     # Save the duration and the mean in list
#                     int_adv_to_D[int_step].append(duration_for_reaching[u])
#                     int_adv_to_M[int_step].append(month_where_was[u])

#         if 'ToCompute' in duration_for_reaching:
#             # print(duration_for_reaching)
#             pass

#         L = [is_constructed, ] + duration_for_reaching
#         # L += month_where_was                               #MONTHS
#         # sys.exit()
#         return L

#     # Nom des features
#     columns_names = ['is_constructed'] + ['duration_to_reach' +
#                                           str(step2av(step[0])) for step in steps_tuple[1:]]
#     # columns_names += ['month_of_advancement' + str(step2av(step[0])) for step in steps_tuple[1:]]                      #MONTHS

#     # Features augmentées
#     df_augment = df.apply(lambda row: pd.Series(
#         augment_date(row), index=columns_names), axis=1)

#     # Fill
#     # Features avec des NA remplacés par durées moyennes
#     int_adv_to_D = [moy(L) for L in int_adv_to_D]
#     int_adv_to_M = [most_freq(L) for L in int_adv_to_M]

#     def fill_NA(row):
#         global n_na_found
#         R = row.copy()

#         # The last ToCompute values (meaning it was not computed ie advancement hasnt been reached) are given the values None
#         for col in ['duration_to_reach' + str(step2av(step[0])) for step in steps_tuple[1:]][::-1]:
#             if row[col] == "ToCompute":
#                 R[col] = "Unreached"
#             else:
#                 break
#         # The first ToCompute values (meaning for advancement i->i+1, step i hasnt been seen because photos were made after this step) are given the mean values
#         for i, col in enumerate(['duration_to_reach' + str(step2av(step[0])) for step in steps_tuple[1:]]):
#             if row[col] == "ToCompute":
#                 R[col] = int_adv_to_D[i]

#         # for i, col in enumerate(['month_of_advancement' + str(step2av(step[0])) for step in steps_tuple[1:]]):
#         #     if row[col] == "Unknown":
#         #         R[col] = int_adv_to_M[i]
#         # If one column is unknown, which means build is constructed but we have not any time data on it, we fill with mean values.
#         return R

#     df_augment = df_augment.apply(lambda row: pd.Series(
#         fill_NA(row), index=columns_names), axis=1)

#     print(f"NA :{n_na_found}")
#     return df_augment


# df_aug = extract_features_date(train_df)
# train_df = pd.merge(
#     left=train_df,
#     right=df_aug,
#     left_index=True,
#     right_index=True,
# )

# df_aug2 = extract_features_date(test_df)
# test_df = pd.merge(
#     left=test_df,
#     right=df_aug2,
#     left_index=True,
#     right_index=True,
# )


for x in ["date1", "date2", "date3", "date4", "date5"]:
    # weekday
    train_df["weekday" + "_" + x] = train_df[x].apply(
        lambda x: datetime.strptime(x, "%d-%m-%Y").weekday()
    )
    test_df["weekday" + "_" + x] = test_df[x].apply(
        lambda x: datetime.strptime(x, "%d-%m-%Y").weekday()
    )

    # month
    train_df["month" + "_" + x] = train_df[x].apply(
        lambda x: datetime.strptime(x, "%d-%m-%Y").month
    )
    test_df["month" + "_" + x] = test_df[x].apply(
        lambda x: datetime.strptime(x, "%d-%m-%Y").month
    )

    # year
    train_df["year" + "_" + x] = train_df[x].apply(
        lambda x: datetime.strptime(x, "%d-%m-%Y").year
    )
    test_df["year" + "_" + x] = test_df[x].apply(
        lambda x: datetime.strptime(x, "%d-%m-%Y").year
    )


# adding perimters and areas of polygons

train_df["area"] = train_df["geometry"].area
train_df["length"] = train_df["geometry"].length


# a = train_df["area"]
# b = train_df["length"]

# train_df["area"] = (a - a.min()) / (a.max() - a.min())
# train_df["length"] = (b - b.min()) / (b.max() - b.min())

test_df["area"] = test_df["geometry"].area
test_df["length"] = test_df["geometry"].length


# a = test_df["area"]
# b = test_df["length"]

# test_df["area"] = (a - a.min()) / (a.max() - a.min())
# test_df["length"] = (b - b.min()) / (b.max() - b.min())

train_df = train_df.drop(train_df[train_df["area"] == 0].index)
test_df = test_df.drop(test_df[test_df["area"] == 0].index)


# 1 over area or length:

train_df["1/area"] = 1/train_df["area"]
test_df["1/area"] = 1/test_df["area"]

train_df["1/length"] = 1/train_df["length"]
test_df["1/length"] = 1/test_df["length"]

# boxcox transformation

train_df["boxcox_area"], par = boxcox(train_df["area"])
test_df["boxcox_area"], par = boxcox(test_df["area"])

train_df["boxcox_length"], par = boxcox(train_df["length"])
test_df["boxcox_length"], par = boxcox(test_df["length"])

# square root transformation

train_df["sqrt_area"] = np.sqrt(train_df["area"])
test_df["sqrt_area"] = np.sqrt(test_df["area"])


# length squared

train_df["squared_length"] = train_df["length"]**2
test_df["squared_length"] = test_df["length"]**2


# area over length squared

train_df["area/length**2"] = train_df["area"]/(train_df["length"]**2)
test_df["area/length**2"] = test_df["area"]/(test_df["length"]**2)

# elongation

borders_train = train_df["geometry"].boundary
borders_test = train_df["geometry"].boundary

n = borders_train.shape[0]
p = borders_train.shape[0]


def elong(u):
    pt = list(u.coords)
    pt1 = max(pt, key=lambda x: x[1])   # point with maximal ordinate
    pt2 = min(pt, key=lambda x: x[1])   # point with minimal ordinate
    pt3 = max(pt, key=lambda x: x[0])   # point with maximal abscissa
    pt4 = min(pt, key=lambda x: x[0])   # point with minimal abscissa
    return max(pt1[1]-pt2[1], pt3[0]-pt4[0])


dic_train = {}
dic_test = {}

dic_train['elongation'] = [elong(borders_train.iloc[i]) for i in range(n)]
dic_test['elongation'] = [elong(borders_test.iloc[i]) for i in range(p)]

df_train_elong = pd.DataFrame.from_dict(dic_train)
df_test_elong = pd.DataFrame.from_dict(dic_test)


train_df = pd.merge(
    left=train_df,
    right=df_train_elong,
    left_index=True,
    right_index=True,
)

test_df = pd.merge(
    left=test_df,
    right=df_test_elong,
    left_index=True,
    right_index=True,
)

train_df = train_df.drop("geometry", axis=1)
test_df = test_df.drop("geometry", axis=1)

dates = ["date1", "date2", "date3", "date4", "date5"]
for d in dates:
    train_df = train_df.drop(d, axis=1)
    test_df = test_df.drop(d, axis=1)

col_str = [
    "change_status_date1",
    "change_status_date2",
    "change_status_date3",
    "change_status_date4",
    "change_status_date5",
]
le = LabelEncoder()
train_df[col_str] = train_df[col_str].apply(le.fit_transform)
test_df[col_str] = test_df[col_str].apply(le.fit_transform)


train_df["urban_types"] = train_df["urban_types"].apply(
    lambda x: x.split(","))
test_df["urban_types"] = test_df["urban_types"].apply(
    lambda x: x.split(","))


train_df = pd.concat(
    [train_df, train_df["urban_types"].str.join("|").str.get_dummies()], axis=1
)
test_df = pd.concat(
    [test_df, test_df["urban_types"].str.join("|").str.get_dummies()], axis=1
)

train_df = train_df.drop("urban_types", axis=1)
test_df = test_df.drop("urban_types", axis=1)


train_df["geography_types"] = train_df["geography_types"].apply(
    lambda x: x.split(","))
test_df["geography_types"] = test_df["geography_types"].apply(
    lambda x: x.split(","))


train_df = pd.concat(
    [train_df, train_df["geography_types"].str.join("|").str.get_dummies()], axis=1
)
test_df = pd.concat(
    [test_df, test_df["geography_types"].str.join("|").str.get_dummies()], axis=1
)

train_df = train_df.drop("geography_types", axis=1)
test_df = test_df.drop("geography_types", axis=1)


train_df["change_type"] = train_df["change_type"].apply(
    lambda x: change_type_map[x])


train_df.to_csv("train_df.csv")
test_df.to_csv("test_df.csv")
