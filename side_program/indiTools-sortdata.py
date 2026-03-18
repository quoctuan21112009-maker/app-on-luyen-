import json

# Your JSON snippet
# json_data = {
#     "assignId": "69476438b20477e46b99a44d",
#     "assignmentContentType": 4,
#     "name": "ÔN TẬP CUỐI HỌC KÌ I",
#     "data": [
#         {
#             "stepIndex": 0,
#             "content-dataStandard": "<p>. Trong thời kì chống Mỹ...</p>",
#             "numberQuestion": 95,
#             "typeAnswer": 0,
#             "content": ["Đường Hồ Chí Minh."]
#         },
#         {
#             "stepIndex": 1,
#             "content-dataStandard": "<p>. Nội dung nào sau đây...</p>",
#             "numberQuestion": 46,
#             "typeAnswer": 0,
#             "content": ["Quá trình chuẩn bị chu đáo..."]
#         },
#         {
#             "stepIndex": 2,
#             "content-dataStandard": "<p>. Từ sau ngày 19-12-1946...</p>",
#             "numberQuestion": 60,
#             "typeAnswer": 0,
#             "content": ["Chiến đấu ở các đô thị..."]
#         }
#     ]
# }
with open("Trần Đức Toàn-69460c230e27bfbc899894f4-ANSWER.json", 'r', encoding='utf-8') as f:
    json_data = f.read()
json_data = json.loads(json_data)
# Sort the 'data' list based on 'numberQuestion'
# item['numberQuestion'] tells Python which field to look at for comparison
json_data["data"].sort(key=lambda item: item["numberQuestion"])

# Output the result
jsonfinal = json.dumps(json_data, indent=4, ensure_ascii=False)
print("Writing to file...")
with open(f'anssort.json','w', encoding = 'utf8') as f:
    f.write(str(jsonfinal))
