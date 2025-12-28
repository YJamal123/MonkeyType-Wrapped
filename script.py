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
head = df.head(int(len(df)*.2))
tail = df.tail(int(len(df)*.2))
head_wpm = round(head["wpm"].mean(), 2)
tail_wpm = round(tail["wpm"].mean(), 2)
change_wpm = tail_wpm - head_wpm
if change_wpm > 0: 
    print(f"You started the year averaging {head_wpm} wpm and ended the year averaging {tail_wpm} wpm! Thats a growth of {change_wpm} wpm!")
else: 
    print(f"You started the year averaging {head_wpm} wpm and ended averaging {tail_wpm} wpm!")
