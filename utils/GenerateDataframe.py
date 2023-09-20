import pandas as pd

def generate_df(header, id_list, previous_timestamp, lastest_timestamp,
                previous_id_price_dict, lastest_id_price_dict,
                pct_change_dict, score_dict):
    df = pd.DataFrame({'Data': [previous_timestamp, lastest_timestamp, '24h_Percentage_Change', 'Score']})
    i = 1
    for token_id in id_list:
        y_price = previous_id_price_dict[token_id]
        l_price = lastest_id_price_dict[token_id]
        pct_change = pct_change_dict[token_id]
        s = score_dict[token_id]
        df[header[i]] = [y_price, l_price, pct_change, s]
        i += 1
    
    return df

def generate_score_df(lastest_timestamp, major_score, major_weight, minor_score, minor_weight):
    score1 = major_score * major_weight
    score2 = minor_score * minor_weight
    df = pd.DataFrame({
        'Timestamp': [lastest_timestamp],
        'Raw Major Score': [major_score],
        'Major Weight': [major_weight],
        'Major Score': [score1],
        'Raw Minor Score': [minor_score],
        'Minor Weight': [minor_weight],
        'Minor Score': [score2],
        'Total Score': [score1 + score2]
    })
    df['Raw Major Score'] = df['Raw Major Score'].astype(float)
    df['Major Weight'] = df['Major Weight'].astype(float)
    df['Major Score'] = df['Major Score'].astype(float)
    df['Raw Minor Score'] = df['Raw Minor Score'].astype(float)
    df['Minor Weight'] = df['Minor Weight'].astype(float)
    df['Minor Score'] = df['Minor Score'].astype(float)
    df['Total Score'] = df['Total Score'].astype(float)
    return df

def generate_stats_df(header, stats_dict, lastest_timestamp):
    df = pd.DataFrame({'Timestamp': [lastest_timestamp]})
    for v in header[1:]:
        df[v] = stats_dict[int(v)]
        df[v] = df[v].astype(float)
    return df