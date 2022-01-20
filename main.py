from datetime import datetime
from numpy import array, power
import pandas as pd
import plotly.express as px
import json
import io

idToPlayer = {
    365469050794672128: "Lancer",
    237495183934095361: "Pilbågsskytten",
    377018183623901184: "StolBord"
}

start_date = datetime.fromisoformat("2021-12-16 01:00:00.000000")

def makeGraph(json_data, field):

    powerData = json_data[field]

    def parse():
        power = []
        day = []
        player = []
        for field in powerData:
            power.append(field["value"])
            player.append(idToPlayer[field["id"]])
            date = datetime.fromisoformat(field["date"])
            diff = date - start_date
            hours_diff = float(diff.seconds) / float(60*60)
            day.append(hours_diff / 24 + diff.days)
        
        return pd.DataFrame(
            dict(power=power, day=day, player=player)
        )

    df_json = parse()
    df_json = df_json.sort_values(by="day")

    fig_json = px.line(df_json, x="day", y="power", color="player")
    filename = "{f}-{d}.png".format(d=datetime.now().strftime("%Y-%m-%d-%I-%M-%S"), f=field) 
    fig_json.write_image("graphs/" + filename, scale=2)

    return filename


def makeResourceGraph(json):
    return makeGraph(json, "resource_gathered")

def makePowerGraph(json):
    return makeGraph(json, "power")
    

if __name__ == "__main__":
    with open('data.json') as json_file:
        data_json = json.load(json_file)
    makeGraph(data_json)