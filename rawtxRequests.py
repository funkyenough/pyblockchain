import requests

APIURL = "https://blockchain.info/rawtx/"
TXID = "0e942bb178dbf7ae40d36d238d559427429641689a379fc43929f15275a75fa6"

r = requests.get(APIURL + TXID)
print(r.text)
