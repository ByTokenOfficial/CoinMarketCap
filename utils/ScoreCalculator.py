def cal_pct_change(prev_price_dict, lastest_price_dict):
    result_dict = {}
    for token_id, lastest_price in lastest_price_dict.items():
        previous_price = prev_price_dict[token_id]
        pct_change = (lastest_price - previous_price) / lastest_price
        result_dict[token_id] = pct_change

    return result_dict

def score(price):
    p = abs(price)
    s = 0
    if p <= 0.015:
        pass
    elif p <= 0.03:
        s = 2
    elif p <= 0.05:
        s = 3
    else:
        s = 4

    if p == price:
        return s
    else:
        return -1 * s

def cal_score(pct_change_dict):
    score_dict = {}
    for token_id, pct_change in pct_change_dict.items():
        score_dict[token_id] = score(pct_change)

    return score_dict

def generate_score_dict(score_dict, token_id_list):
    total = 0
    s_dict = {-4:0, -3:0, -2:0, -1:0, 0:0, 1:0, 2:0, 3:0, 4:0}
    for token_id in token_id_list:
        s = score_dict[token_id]
        total += s
        s_dict[s] += 1
    return s_dict

def cal_total_score(s_dict):
    total_score = 0
    for k, v in s_dict.items():
        total_score += k * v
    return total_score

if __name__ == '__main__':
    pass