import numpy as np
import pandas as pd
df = pd.read_csv('results.csv')
#Group the tests by languages(E,E5k,E10k,etc.)
stats = df.groupby("language")["wpm"].agg(["count", "mean", "max"])
#Restart rate
restart = df["restartCount"].sum()
num_tests = df["wpm"].shape
p_restart = round(float(restart)/(num_tests[0]-1) * 100, 2)
print(f"Your restart rate was only {p_restart}%")
#Typing growth
df = df.sort_values("timestamp")
early = df.head(int(len(df)*.2))
late = df.tail(int(len(df)*.2))
early_wpm = round(early["wpm"].mean(), 2)
late_wpm = round(late["wpm"].mean(), 2)
change_wpm = late_wpm - early_wpm
if change_wpm > 0: 
    print(f"You started the year averaging {early_wpm} wpm and ended the year averaging {late_wpm} wpm! Thats a growth of {change_wpm} wpm!")
else: 
    print(f"You started the year averaging {early_wpm} wpm and ended averaging {late_wpm} wpm!")

#Accuracy
early_acc = round(early["acc"].mean(),2)
late_acc = round(late["acc"].mean(),2)
change_acc = round(late_acc - early_acc, 2)
if change_acc > 0: 
    print(f"You started the year averaging an accuracy of {early_acc}% and ended the year averaging an accuracy of {late_acc}%! Thats a growth of {change_acc}%!")
else: 
    print(f"You started the year averaging an accuracy of {early_acc}% and ended averaging {late_acc}% accuracy!")

#Consistency
early_cons = round(early["consistency"].std(), 2)
late_cons = round(late["consistency"].std(), 2)
change_cons = late_cons - early_cons

if change_cons > 0 : 
    print(f"Your consistency improved by {change_cons} throughout the year!")
else: 
    print(f"Faster isn't always better, your consistency dropped by {change_cons} this past year.")

