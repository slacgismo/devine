import json
import pandas as pd
from io import StringIO

f = open("../.vscode/historical-data-02-2019.json")

json_data = json.load(f)

df = pd.DataFrame(data=json_data["sessions"]).to_csv(path_or_buf="../2019-02-historical.csv", index=False)

f.close()
