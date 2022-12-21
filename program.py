import requests
import json
import xmltodict
import html
import os

# github라는 오픈소스 공간에서 SLACK_WEBHOOK_URL을 암호화하기 위한 코드.
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

def makePayloadItem(newsItem):
  return      {
          "type": "Card",
          "fallback": "Something bad happened",
          "color": "#00ff2a",
          "title": f"{html.unescape(newsItem['title'])}",
          "text": f"{html.unescape(newsItem['descript'])}",
          "fields": [
          {
                "type": "mrkdwn",
              "title": "출처",
              "value": f"{newsItem['source']}",
              "short": 'true'
          },
          {
                "type": "mrkdwn",
              "title": "*원문*",
              "value": f"<{newsItem['url']}|뉴스 링크>",
              "short": 'true'
          },
          {
                    "type": "divider"
              }
          ]
      }

def callWebhook (payload):
  headers = {
    'Content-type' : 'application/json',
  }
  res = requests.post(SLACK_WEBHOOK_URL, headers=headers, json=payload)
  print(res.text)

def getNewsFromRss():
  RSS_URL = 'https://trends.google.com/trends/trendingsearches/daily/rss?geo=KR'
  res = requests.get(RSS_URL)
  ordered_dict = xmltodict.parse(res.text)
  json_type = json.dumps(ordered_dict)
  res_dict = json.loads(json_type)

  itemList = res_dict['rss']['channel']['item']
  newsList = []

  for idx,item in enumerate(itemList):
      news_item_list = item['ht:news_item']

      def mapping (news_item):
          temp_dict = dict()
          temp_dict['title'] = news_item['ht:news_item_title']
          temp_dict['descript'] = news_item['ht:news_item_snippet']
          temp_dict['url'] = news_item['ht:news_item_url']
          temp_dict['source'] = news_item['ht:news_item_source']
          return temp_dict

      if(isinstance(news_item_list,list)):
        # news item 이 list형태로 mapping 된 경우
        for n_idx, news_item in enumerate(news_item_list):
          newsList.append(mapping(news_item))
      else:
          news_item = news_item_list
          newsList.append(mapping(news_item))

  return newsList

def main():
  print(f'\n\n뉴스 기사 수집을 시작합니다...')
  newsList = getNewsFromRss()
  newsLen = len(newsList)
  print(f'>>> {newsLen}개의 기사를 수집하였습니다')

  print(f'\n\n뉴스 카드 생성을 시작합니다...')
  cardList = dict()
  cardList['attachments'] = []
  for idx,newsItem in enumerate(newsList):
    item = makePayloadItem(newsItem)
    cardList['attachments'].append(item)
    print(f'>>> [{idx}/{newsLen}] 번째 NEWS CARD를 생성하였습니다.')

  print(f'\n\nSLACK 발송을 시작합니다...')
  callWebhook(
    {'blocks':[
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*오늘자 뉴스*"
        }
      },
      {
        "type": "divider"
      },
    ]}
  )
  callWebhook(cardList)

if __name__ == "__main__":
  main()
