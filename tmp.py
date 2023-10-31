### FundingRate < -0.3%

obj={
        "StatistcTimeUTC+8": "2023-10-20_14-00",
        "Symbol": "BOND",
        "MarkPrice": 3.666,
        "IndexPrice": 3.7085,
        "30minAvgPrice": 3.6532,
        "60minAvgPrice": 3.5456,
        "h1MarkPrice": 3.3703,
        "h1IndexPrice": 3.4348,
        "FundingRate": "-1.26%",
        "15minFundingRate": "-0.95%",
        "1hFundingRate": "-0.30%",
        "sumOpenInterestValue": "13.857M",
        "1hsumOpenInterestValue": "9.157M",
        "4hsumOpenInterestValue": "6.410M",
        "1dsumOpenInterestValue": "5.972M",
        "1hOIChange": "51.33%",
        "4hOIChange": "116.18%",
        "1dOIChange": "132.03%",
        "LongShortRatioAccount": "1.030",
        "1hLongShortRatioAccount": "1.500",
        "4hLongShortRatioAccount": "2.041",
        "1dLongShortRatioAccount": "2.274",
        "1hLSRAChange": "-31.33%",
        "4hLSRAChange": "-49.53%",
        "1dLSRAChange": "-54.71%",
        "PremiumIndex": "-1.15%"
    }
symbol = obj.get("Symbol","")
rate_percentage = obj.get("FundingRate", "")
rate_str = rate_percentage.replace("%", "")
if rate_str:
    rate = float(rate_str)
    condition_2 = rate < -0.3
    try:
        obj["now fr"] = obj.pop("FundingRate", "no data")
        obj["15m fr"] = obj.pop("15minFundingRate", "no data")
        obj["1h fr"] = obj.pop("1hFundingRate", "no data")
    except Exception as e:
        print(f"沒有{e}無法刪除...")

else:
    print(f"{symbol}沒有funding rate")
    # error_log_array.append(f"{symbol}沒有funding rate")
    # continue
print(obj)
print(condition_2)

### 1hOIchange  or 4hOIchange 其中1個 > 10%
oi_1h_change_str = obj.get("1hOIChange", "")
oi_4h_change_str = obj.get("4hOIChange", "")
oi_1d_change_str = obj.get("1dOIChange", "")
if oi_1h_change_str and oi_4h_change_str:
    oi_1h_change = float(oi_1h_change_str.replace("%", "")) / 100
    oi_4h_change = float(oi_4h_change_str.replace("%", "")) / 100
    # oi_1d_change = float(oi_1d_change_str.replace("%", "")) / 100
    oi_conditions = [
        oi_1h_change > 0.1,
        oi_4h_change > 0.1,
        # oi_1d_change > 0.1,
    ]
    condition_3 = sum(oi_conditions) >= 1
    try:
        del obj["sumOpenInterestValue"]
        del obj["1hsumOpenInterestValue"]
        del obj["4hsumOpenInterestValue"]
        del obj["1dsumOpenInterestValue"]
        obj["1h OI%"] = obj.pop("1hOIChange")
        obj["4h OI%"] = obj.pop("4hOIChange")
        obj["1d OI%"] = obj.pop("1dOIChange")
    except Exception as e:
        print(f"沒有{e}無法刪除...")

else:
    print(f"{symbol}沒有1小時或4小時")
    # error_log_array.append(f"{symbol}沒有1小時或4小時")
    # continue

print(obj)
print(condition_3)

### LSRAccount < 1

ls_ratio_account_str = obj.get("LongShortRatioAccount", "")
if ls_ratio_account_str:
    ls_ratio_account = float(ls_ratio_account_str)
    condition_4 = ls_ratio_account < 1
    try:
        obj["LSRA"] = obj.pop("LongShortRatioAccount")
        # del obj["1hLongShortRatioAccount"]
        # del obj["4hLongShortRatioAccount"]
        # del obj["1dLongShortRatioAccount"]
        # obj["1h LSRA%"] = obj.pop("1hLSRAChange")
        # obj["4h LSRA%"] = obj.pop("4hLSRAChange")
        # obj["1d LSRA%"] = obj.pop("1dLSRAChange")
        del obj["1hLSRAChange"]
        del obj["4hLSRAChange"]
        del obj["1dLSRAChange"]
        print(obj)
        obj["LSRA_1h"] = obj.pop("1hLongShortRatioAccount")
        obj["LSRA_4h"] = obj.pop("4hLongShortRatioAccount")
        obj["LSRA_1d"] = obj.pop("1dLongShortRatioAccount")
    except Exception as e:
        print(f"沒有{e}無法刪除...")

else:
    print(f"{symbol}沒有long short ratio account數據")
    # error_log_array.append(f"{symbol}沒有long short ratio account數據")
    # continue

print(obj)
print(condition_4)

# 檢查有幾個條件符合
conditions_met = sum(
    [
        # condition_1,
        condition_2,
        condition_3,
        condition_4,
        # condition_5,
    ]
)
print(f"{symbol}有{conditions_met}項達到門檻")