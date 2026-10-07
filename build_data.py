import re,json,pathlib,shutil
root=pathlib.Path(__file__).parent
source=root.parent/'繪圖提示詞.txt'
if not source.exists():
    source=root/'data/繪圖提示詞原始.txt'
text=source.read_text(encoding='utf-8-sig')
text=re.sub(r'29\.\s*來像','來像',text)
for n,title in [(30,'風景'),(31,'水下'),(32,'雕像'),(33,'超現實'),(34,'手寫註記風格')]:
    text=re.sub(r'\n'+title+r'\s*\n'+str(n)+r'\.\s*','\n'+str(n)+'.\t'+title+'\n',text)
parts=re.split(r'(?m)^([0-9]+)\.\s*',text)
items=[]
for i in range(1,len(parts),2):
    number=int(parts[i]); title,_,body=parts[i+1].strip().partition('\n')
    body=body.strip()
    cat='奇幻與藝術'
    if re.search('廣告|品牌|產品|包裝|香水|珠寶|鐘錶|飯店|餐廳|文具',title):cat='品牌與產品'
    elif re.search('人像|頭像|肖像|妝容|色彩分析|髮型|形象|夜拍|修正|增強|晨霧|水下',title):cat='人像與攝影'
    elif re.search('圖表|指南|圖解|剖面|藍圖|分析|檔案|圖鑑|說明|專利|紀錄|地圖|圖譜|掛圖',title):cat='圖解與知識'
    elif re.search('漫畫|動漫|貼圖|遊戲|角色|童書|塗鴉|分身|黏土',title):cat='角色與插畫'
    elif re.search('海報|封面|報紙|雜誌|手冊|明信片|郵票|節目單|歌詞',title):cat='海報與出版'
    upload=bool(re.search('上傳|附上|這張|照片|圖片|人像|原圖|原始照片|這個主體',body))
    ref='portrait' if re.search('人物|人像|主角|角色|照片|肖像|髮型|妝容|手相',title+body) else 'object'
    if title=='室內設計':ref='room'
    if title=='圖畫':ref='sketch'
    if title=='手相':ref='palm'
    choice={'應用程式設計':'示範設定：App 名稱「小森日記」，用途為自然觀察記錄；美學為明亮、清爽的薄荷綠設計。','研究圖解':'示範主題：水循環。','圖文食譜':'示範料理：義式番茄羅勒義大利麵，三頁小誌以三頁並列展示。','超寫實桌布':'示範選擇：晨露中的苔蘚。','風景':'示範選擇：日出時的山谷與湖泊。','動物資訊圖表':'示範主題：小貓熊。','塔羅牌':'示範人物：自然觀察者，以虛構人物呈現。'}
    note=choice.get(title,'模擬參考：'+{'portrait':'虛構的短髮、圓框眼鏡人物，青綠外套與橘色肩包。','object':'青綠色貓頭鷹造型陶瓷物件。','room':'明亮客廳。','sketch':'童趣小屋與樹木圖畫。','palm':'虛構手掌照片，僅作娛樂性視覺示例。'}[ref] if upload else '依原提示詞製作的獨立範例。')
    items.append(dict(id=number,title=title,prompt=body,category=cat,upload=upload,reference=ref if upload else None,note=note,image=f'assets/examples/{number:03}.png'))
(root/'assets/examples').mkdir(parents=True,exist_ok=True)
(root/'assets/references').mkdir(parents=True,exist_ok=True)
(root/'data').mkdir(exist_ok=True)
if source.resolve()!=(root/'data/繪圖提示詞原始.txt').resolve():
    shutil.copyfile(source,root/'data/繪圖提示詞原始.txt')
(root/'data/prompts.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'data/prompts.js').write_text('window.PROMPTS = '+json.dumps(items,ensure_ascii=False)+';',encoding='utf-8')
print(f'{len(items)} prompts; '+str([(x['id'],x['title']) for x in items]))
