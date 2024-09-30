import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
import sys
import numpy_financial as npf
import os

# Line Bot API Integration with Flask 設定
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#Step 2: 標的篩選  

# Define a top 10 list of US stock ETF tickers by assets under management (AUM)
tickers = ["SPY", "VOO", "IVV", "VTI", "QQQ", "IWM", "EEM", "EFA", "VEA", "XLU"]

# Create an empty dictionary to store the Sharpe ratios
sharpe_ratios = {}

# Create an empty dictionary to store the annualized returns
annualized_returns = {}

# Loop through each ticker
for ticker in tickers:
    # Download the historical price data for the past max years
    data = yf.download(ticker, period="max")

    # Calculate the daily returns
    data["daily_return"] = data["Adj Close"].pct_change()

    # Calculate the annualized Sharpe ratio
    sharpe_ratio = data["daily_return"].mean() / data["daily_return"].std() * np.sqrt(252)

    # Calculate the annualized return
    annualized_return = (1 + data["daily_return"].mean()) ** 252 - 1

    # Store the Sharpe ratio in the dictionary
    sharpe_ratios[ticker] = sharpe_ratio
    # Store the annualized return in the dictionary
    annualized_returns[ticker] = annualized_return

# Sort the dictionary by values in descending order
sorted_sharpe_ratios = sorted(sharpe_ratios.items(), key=lambda x: x[1], reverse=True)

# Get the top 5 tickers with the highest Sharpe ratios
top_5_tickers = [ticker for ticker, _ in sorted_sharpe_ratios[:5]]
# Get the top 5 tickers' annualized returns 
top_5_annualized_returns = {ticker: annualized_returns[ticker] for ticker in top_5_tickers}

# Print the top 5 tickers
# Print their Sharpe ratios and annualized returns round to 2 decimals
print("The top 5 tickers are: ", top_5_tickers)
print("")

global 標的篩選
標的篩選 = "夏普值前5名美股ETF為:\n"+str(top_5_tickers[0])+", "+str(top_5_tickers[1])+", "+str(top_5_tickers[2])+", "+str(top_5_tickers[3])+", "+str(top_5_tickers[4])
print(標的篩選)

for ticker, sharpe_ratio in sorted_sharpe_ratios[:5]:
    print(f"The annualized Sharpe ratio for {ticker} is {sharpe_ratio:.2f}")
    print(f"The annualized return for {ticker} is {annualized_returns[ticker]:.2f}")
    print("")

# Line Bot API Integration with Flask 設定
app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = 'a7kYJhH4DpJ9OA7OU3ROU+ggERb60bIpvYdoBAoMSc06cv2S9dxisH7JyjcwtFquXPAKM6mUk435keQyMd2KHRIAuqqlTOt5tpJoYJMO5H4cS+Gao20dUI8Eqm20QvO4ifHBzJoc9zjVJmvl7L6I/AdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'a725286b58a4ce5b438e552b7dff8b28'
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global count_input
    global current_age
    global retire_age
    global years_left
    global annual_spending
    global total_amount_needed
    global tickers
    global sharpe_ratios
    global annualized_returns
    global top_5_tickers
    global top_5_annualized_returns
    global sorted_sharpe_ratios
    global data
    global 標的篩選

    msg = str(event.message.text)
    if msg == "理財目標設定": #Step 1: 理財目標設定
        line_bot_api.reply_message(event.reply_token, TextSendMessage("歡迎使用理財目標設定功能！\n請輸入您的年齡："))
        count_input = 0
    
    elif msg.isdigit() and count_input == 0:
        current_age = eval(msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage("您輸入的年齡是"+str(current_age)+"歲。\n請輸入您希望退休的年齡："))
        count_input += 1

    elif msg.isdigit() and count_input == 1:
        retire_age = eval(msg)
        years_left = retire_age - current_age
        line_bot_api.reply_message(event.reply_token, TextSendMessage("您輸入的希望退休年齡是"+str(retire_age)+"歲。\n請輸入您退休後每年的預期花費：新台幣$"))
        count_input += 1

    elif msg.isdigit() and count_input == 2:
        annual_spending = eval(msg)
        total_amount_needed = int(annual_spending /(0.04))
        annual_spending = format(annual_spending, ',')
        total_amount_needed = format(total_amount_needed, ',')  
        line_bot_api.reply_message(event.reply_token, TextSendMessage("您輸入的退休後每年的預期花費為：新台幣$"+str(annual_spending)+"。\n您"+str(years_left)+"年後退休後所需的總金額為：新台幣$"+str(total_amount_needed)+"。"))
        count_input += 1
    
    elif msg == "標的篩選": #Step 2: 標的篩選  
        line_bot_api.reply_message(event.reply_token, TextSendMessage("歡迎使用標的篩選功能！\n系統將為您篩選夏普值前5名ETF。\n"+標的篩選+"\n請輸入'Chart'查看ETF價格走勢圖。"))
        count_input = 0

    elif msg == "Chart":    
        #top 5 ETF price list.png傳到Line
        image_url = "https://raw.githubusercontent.com/243kevinkan/Project/refs/heads/main/top%205%20ETF%20price%20list.png"
        image_message = ImageSendMessage(
            original_content_url = image_url,
            preview_image_url = image_url
        )
        line_bot_api.reply_message(event.reply_token, image_message)
    
    elif msg == "投資組合推薦": #Step 3: 投資組合建議
         #Step 3: 投資組合建議
        # Connect to OpenAI API to get the portfolio recommendation
        import os
        import requests
        import base64

        # Configuration
        API_KEY = "cad6f84406c0487fb434010c83b6f142"
        IMAGE_PATH = "Doggy.jpg"
        encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')
        headers = {
            "Content-Type": "application/json",
            "api-key": API_KEY,
        }

        # Payload for the request 
        # 提供Step 1 理財目標及Step 2 Top 5 ETF 給GPT，GPT回覆投資組合建議 
        payload = {
        "messages": [
            {
            "role": "system",
            "content": "You are a financial specialist and math expert."
            },
            {
                "role": "user",
            "content": "Please recommend one investment portflio based on"+str(top_5_tickers)+"for a person who is"+str(current_age)+ 
            "and plans to retire in"+str(years_left)+"years."+ 
            "Please calculate weighted annualized return based on"+str(top_5_annualized_returns)+
            "Please calculate the required monthly contribution to achieve the total amount of $"+str(total_amount_needed)+
            "Please reply only summary of ticker, weight, portfolio's annualized return, required montly contribution, followin by rationale."
            "No need to show the details of calculation. 請用繁體中文回答"
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
        }

        ENDPOINT = "https://azure-openai-eastus-20240916.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview"

        # Send request
        try:
            response = requests.post(ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        except requests.RequestException as e:
            raise SystemExit(f"Failed to make the request. Error: {e}")

        # Select the portfolio recommendation part from the reponse and print out
        response_json = response.json()
        portfolio_recommendation = response_json['choices'][0]['message']['content']
        # print("")
        # print(portfolio_recommendation)

        global 投資組合建議
        投資組合建議 = "針對您設定的理財目標，\n以夏普值前5名的ETF為標的，\nAI推薦的投資組合如下:\n"+str(portfolio_recommendation)
        # print(投資組合建議)  

        line_bot_api.reply_message(event.reply_token, TextSendMessage("歡迎使用投資組合建議功能！\nAI將為您提供投資組合建議。\n"+投資組合建議))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage("請輸入正確的指令，並重新點選Step 1！"))        

if __name__ == "__main__":
    app.run()

