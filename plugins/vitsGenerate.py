# -*- coding: utf-8 -*-
import asyncio
import json
import os
import subprocess
from asyncio import sleep

import httpx
import librosa
import requests
import soundfile
import yaml

from plugins.RandomStr import random_str
from plugins.translater import translate
from vits.MoeGoe import vG

with open('config/api.yaml', 'r', encoding='utf-8') as f:
    resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
modelscopeCookie=resulttr.get("modelscopeCookie")
if modelscopeCookie=="":
    modelscopeCookie="cna=j117HdPDmkoCAXjC3hh/4rjk; ajs_anonymous_id=5aa505b4-8510-47b5-a1e3-6ead158f3375; t=27c49d517b916cf11d961fa3769794dd; uuid_tt_dd=11_99759509594-1710000225471-034528; log_Id_click=16; log_Id_pv=12; log_Id_view=277; xlly_s=1; csrf_session=MTcxMzgzODI5OHxEdi1CQkFFQ180SUFBUkFCRUFBQU12LUNBQUVHYzNSeWFXNW5EQW9BQ0dOemNtWlRZV3gwQm5OMGNtbHVad3dTQUJCNFkwRTFkbXAwV0VVME0wOUliakZwfHNEIp5sKWkjeJWKw1IphSS3e4R_7GyEFoKKuDQuivUs; csrf_token=TkLyvVj3to4G5Mn_chtw3OI8rRA%3D; _samesite_flag_=true; cookie2=11ccab40999fa9943d4003d08b6167a0; _tb_token_=555ee71fdee17; _gid=GA1.2.1037864555.1713838369; h_uid=2215351576043; _xsrf=2|f9186bd2|74ae7c9a48110f4a37f600b090d68deb|1713840596; csg=242c1dff; m_session_id=769d7c25-d715-4e3f-80de-02b9dbfef325; _gat_gtag_UA_156449732_1=1; _ga_R1FN4KJKJH=GS1.1.1713838368.22.1.1713841094.0.0.0; _ga=GA1.1.884310199.1697973032; tfstk=fE4KxBD09OXHPxSuRWsgUB8pSH5GXivUTzyBrU0oKGwtCSJHK7N3ebe0Ce4n-4Y8X8wideDotbQ8C7kBE3queYwEQ6OotW08WzexZUVIaNlgVbmIN7MQBYNmR0rnEvD-y7yAstbcoWPEz26cnZfu0a_qzY_oPpRUGhg5ntbgh_D3W4ZudTQmX5MZwX9IN8ts1AlkAYwSdc9sMjuSF8g56fGrgX9SFbgs5bGWtBHkOYL8Srdy07KF-tW4Wf6rhWQBrfUt9DHbOyLWPBhKvxNIBtEfyXi_a0UyaUn8OoyrGJ9CeYzT1yZbhOxndoh8iuFCRFg38WZjVr6yVWunpVaQDQT762H3ezewpOHb85aq5cbfM5aaKWzTZQ_Ss-D_TygRlsuKRvgt_zXwRYE_VymEzp6-UPF_RuIrsr4vHFpmHbxC61Ky4DGguGhnEBxD7Zhtn1xM43oi_fHc61Ky4DGZ6xfGo3-rjf5..; isg=BKKjOsZlMNqsZy8UH4-lXjE_8ygE86YNIkwdKew665XKv0I51IGvHCUz7_tDrx6l"
async def superVG(data,mode,urls="",langmode="<zh>"):
    if langmode=="<jp>":
        try:
            #r=await translate(data.get("text"))
            #print(r)
            data["text"]=await translate(data.get("text"))
        except:
            print("语音合成翻译出错")
    elif langmode=="<en>":
        try:
            #r=await translate(data.get("text"))
            #print(r)
            data["text"]=await translate(data.get("text"),"ZH_CN2EN")
        except:
            print("语音合成翻译出错")
    if mode=="edgetts":
        speaker = data.get("speaker")
        text = data.get("text")
        # os.system("where python")
        p = random_str() + ".mp3"
        prf = "data/voices/" + p
        command = f"edge-tts --voice {speaker} --text {text} --write-media {prf}"
        os.system(command)
        return prf
    elif mode=="so-vits":
        url = "http://127.0.0.1:9082/synthesize"  # 后端服务的地址
        params = data  # 请求参数
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.post(url, json=json.dumps(params))
            p = "data/voices/" + random_str() + '.wav'
            print("sovits语音合成路径：" + p)
            with open(p, "wb") as f:
                f.write(r.content)
            return p
    elif mode=="vits":
        # 向本地 API 发送 POST 请求
        if "MoeGoe.py" in os.listdir():
            from MoeGoe import voiceGenerate as vg
            # 解析请求中的参数
            text = data['text']
            out = data["out"]

            try:
                speaker = data['speaker']
                modelSelect = data['modelSelect']
            except:
                speaker = 2
                modelSelect = ['voiceModel/nene/1374_epochsm.pth', 'voiceModel/nene/config.json']

                # with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                # result = yaml.load(f.read(), Loader=yaml.FullLoader)
                # speaker = result.get("vits").get("speaker")
                # modelSelect = result.get("vits").get("modelSelect")
            # 调用 voiceG() 函数
            if modelSelect[0].endswith("I.pth"):
                text = text.replace("[JA]", "").replace("[ZH]", "")
            await vg(tex=text, out=out, speakerID=speaker, modelSelect=modelSelect)
            print("语音生成完成")
            # 将生成的音频返回给客户端
            return out

        else:
            print("start voice generate")

            text = data['text']
            out = data["out"]
            try:
                speaker = data['speaker']
                modelSelect = data['modelSelect']
            except Exception as e:
                speaker = 2
                modelSelect = ['vits/voiceModel/nene/1374_epochsm.pth', 'vits/voiceModel/nene/config.json']
                print(e)
                # with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                # result = yaml.load(f.read(), Loader=yaml.FullLoader)
                # speaker = result.get("vits").get("speaker")
                # modelSelect = result.get("vits").get("modelSelect")
            # 调用 voiceG() 函数
            if modelSelect[0].endswith("I.pth"):
                text = text.replace("[JA]", "").replace("[ZH]", "")
            # print("get")
            await vG(tex=text, out=out, speakerID=speaker, modelSelect=modelSelect)
            print("语音生成完成")
            return out
    elif mode=="bert_vits2":
        if urls == '':
            urls = "http://localhost:9080/synthesize"  # 后端服务的地址
            async with httpx.AsyncClient(timeout=200) as client:
                r = await client.post(urls, json=json.dumps(data))
                p = "data/voices/" + random_str() + '.wav'
                print("bert_vits语音合成路径：" + p)
                with open(p, "wb") as f:
                    f.write(r.content)
                return p
        else:
            if str(urls).endswith("/synthesize"):
                pass
            elif str(urls).endswith("/"):
                urls += "synthesize"
            else:
                urls += "/synthesize"
            '''proxies = {
                "http://": proxy,
                "https://": proxy
            }'''
            # 请求参数

            async with httpx.AsyncClient(timeout=200) as client:
                r = await client.post(urls, json=json.dumps(data))
                p = "data/voices/" + random_str() + '.wav'
                print("bert_vits语音合成路径：" + p)
                with open(p, "wb") as f:
                    f.write(r.content)
                return p
    elif mode=="modelscopeTTS":
        speaker = data.get("speaker")
        text = data.get("text")

        headers = {
            "Content-Type": "application/json",
            "Origin": "https://www.modelscope.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
            "Cookie": modelscopeCookie
        }
        if text == "" or text == " ":
            text = "哼哼"
        if speaker == "阿梓":
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azusa-Bert-VITS2-2.3/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azusa-Bert-VITS2-2.3/gradio/file="
        elif speaker == "otto":
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/otto-Bert-VITS2-2.3/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/otto-Bert-VITS2-2.3/gradio/file="
        elif speaker == "塔菲":
            speaker = "taffy"
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Taffy-Bert-VITS2/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Taffy-Bert-VITS2/gradio/file="
        elif speaker == "星瞳":
            speaker = "XingTong"
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/XingTong-Bert-VITS2/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/XingTong-Bert-VITS2/gradio/file="
        elif speaker == "丁真":
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/DZ-Bert-VITS2-2.3/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/DZ-Bert-VITS2-2.3/gradio/file="
        elif speaker == "东雪莲":
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azuma-Bert-VITS2-2.3/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azuma-Bert-VITS2-2.3/gradio/file="
        elif speaker == "嘉然":
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Diana-Bert-VITS2-2.3/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Diana-Bert-VITS2-2.3/gradio/file="
        elif speaker == "孙笑川":
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/SXC-Bert-VITS2/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/SXC-Bert-VITS2/gradio/file="
        elif speaker == "鹿鸣":
            speaker = "Lumi"
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Lumi-Bert-VITS2/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Lumi-Bert-VITS2/gradio/file="
        elif speaker == "文静":
            speaker = "Wenjing"
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Wenjing-Bert-VITS2/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Wenjing-Bert-VITS2/gradio/file="
        elif speaker == "亚托克斯":
            speaker = "Aatrox"
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Aatrox-Bert-VITS2/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Aatrox-Bert-VITS2/gradio/file="
        elif speaker == "奶绿":
            speaker = "明前奶绿"
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/LAPLACE-Bert-VITS2-2.3/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/LAPLACE-Bert-VITS2-2.3/gradio/file="
        elif speaker == "七海":
            speaker = "Nana7mi"
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Nana7mi-Bert-VITS2/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Nana7mi-Bert-VITS2/gradio/file="
        elif speaker == "恬豆":
            speaker = "Bekki"
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Bekki-Bert-VITS2/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Bekki-Bert-VITS2/gradio/file="
        elif speaker == "科比":
            url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Kobe-Bert-VITS2-2.3/gradio/run/predict"
            newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Kobe-Bert-VITS2-2.3/gradio/file="
        data = {
            "data": [text, speaker, 0.5, 0.5, 0.9, 1, "auto", None, "Happy", "Text prompt", "", 0.7],
            "event_data": None,
            "fn_index": 0,
            "dataType": ["textbox", "dropdown", "slider", "slider", "slider", "slider", "dropdown", "audio", "textbox",
                         "radio", "textbox", "slider"],
            "session_hash": "xjwen214wqf"
        }
        p = "data/voices/" + random_str() + '.wav'
        async with httpx.AsyncClient(timeout=200,headers=headers) as client:
            r = await client.post(url, json=data)
            newurl = newurp + \
                     r.json().get("data")[1].get("name")
            async with httpx.AsyncClient(timeout=200) as client:
                r = await client.get(newurl)
                with open(p, "wb") as f:
                    f.write(r.content)
                return p
    elif mode=="outVits":
        speaker = data.get("speaker")
        text = data.get("text")
        # os.system("where python")
        # p = random_str() + ".mp3"
        # p = "data/voices/" + p
        p = "data/voices/" + random_str() + '.wav'
        url = f"https://api.lolimi.cn/API/yyhc/y.php?msg={text}&speaker={speaker}"
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.post(url)
            newUrl = r.json().get("music")
            print("outvits语音合成路径：" + p)
            r1 = requests.get(newUrl)
            with open(p, "wb") as f:
                f.write(r1.content)
            # await change_sample_rate(p)
            return p

async def edgetts(data):
    speaker=data.get("speaker")
    text=data.get("text")
    #os.system("where python")
    p = random_str() + ".mp3"
    prf = "data/voices/" + p
    command = f"edge-tts --voice {speaker} --text {text} --write-media {prf}"
    os.system(command)
    return prf
async def sovits(data):
    url = "http://127.0.0.1:9082/synthesize"  # 后端服务的地址
    params = data  # 请求参数
    async with httpx.AsyncClient(timeout=200) as client:
        r=await client.post(url, json=json.dumps(params))
        p = "data/voices/" + random_str() + '.wav'
        print("sovits语音合成路径：" + p)
        with open(p, "wb") as f:
            f.write(r.content)
        return p
async def taffySayTest(data,url,proxy=None):
    if url=='':
        url = "http://localhost:9080/synthesize"  # 后端服务的地址
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.post(url, json=json.dumps(data))
            p = "data/voices/" + random_str() + '.wav'
            print("bert_vits语音合成路径：" + p)
            with open(p, "wb") as f:
                f.write(r.content)
            return p
    else:
        if str(url).endswith("/synthesize"):
            pass
        elif str(url).endswith("/"):
            url+="synthesize"
        else:
            url+="/synthesize"
        '''proxies = {
            "http://": proxy,
            "https://": proxy
        }'''
        # 请求参数

        async with httpx.AsyncClient(timeout=200) as client:
            r=await client.post(url, json=json.dumps(data))
            p="data/voices/"+random_str()+'.wav'
            print("bert_vits语音合成路径："+p)
            with open(p, "wb") as f:
                f.write(r.content)
            return p
async def outVits(data):
    speaker = data.get("speaker")
    text = data.get("text")
    # os.system("where python")
    #p = random_str() + ".mp3"
    #p = "data/voices/" + p
    p="data/voices/" + random_str() + '.wav'
    url=f"https://api.lolimi.cn/API/yyhc/y.php?msg={text}&speaker={speaker}"
    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.post(url)
        newUrl=r.json().get("music")
        print("outvits语音合成路径：" + p)
        r1=requests.get(newUrl)
        with open(p, "wb") as f:
            f.write(r1.content)
        #await change_sample_rate(p)
        return p

async def voiceGenerate(data):
    # 向本地 API 发送 POST 请求
    if "MoeGoe.py" in os.listdir():
        from MoeGoe import voiceGenerate as vg
        # 解析请求中的参数
        text = data['text']
        out = data["out"]

        try:
            speaker = data['speaker']
            modelSelect = data['modelSelect']
        except:
            speaker = 2
            modelSelect = ['voiceModel/nene/1374_epochsm.pth', 'voiceModel/nene/config.json']

            # with open('config/settings.yaml', 'r', encoding='utf-8') as f:
            # result = yaml.load(f.read(), Loader=yaml.FullLoader)
            # speaker = result.get("vits").get("speaker")
            # modelSelect = result.get("vits").get("modelSelect")
        # 调用 voiceG() 函数
        if modelSelect[0].endswith("I.pth"):
            text = text.replace("[JA]", "").replace("[ZH]", "")
        await vg(tex=text, out=out, speakerID=speaker, modelSelect=modelSelect)
        print("语音生成完成")
        # 将生成的音频返回给客户端
        return out

    else:
        print("start voice generate")

        text = data['text']
        out = data["out"]
        try:
            speaker = data['speaker']
            modelSelect = data['modelSelect']
        except Exception as e:
            speaker = 2
            modelSelect = ['vits/voiceModel/nene/1374_epochsm.pth', 'vits/voiceModel/nene/config.json']
            print(e)
            # with open('config/settings.yaml', 'r', encoding='utf-8') as f:
            # result = yaml.load(f.read(), Loader=yaml.FullLoader)
            # speaker = result.get("vits").get("speaker")
            # modelSelect = result.get("vits").get("modelSelect")
        # 调用 voiceG() 函数
        if modelSelect[0].endswith("I.pth"):
            text = text.replace("[JA]", "").replace("[ZH]", "")
        # print("get")
        await vG(tex=text, out=out, speakerID=speaker, modelSelect=modelSelect)
        print("语音生成完成")
        return out
async def modelscopeTTS(data):
    speaker = data.get("speaker")
    text = data.get("text")
    if speaker == "阿梓":
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azusa-Bert-VITS2-2.3/gradio/run/predict"

    data = {
        "data": ["<zh>" + text, speaker, 0.5, 0.5, 0.9, 1, "ZH", None, "Happy", "Text prompt", "", 0.7],
        "event_data": None,
        "fn_index": 0,
        "dataType": ["textbox", "dropdown", "slider", "slider", "slider", "slider", "dropdown", "audio", "textbox",
                     "radio", "textbox", "slider"],
        "session_hash": "xjwen214wqf"
    }
    p = "data/voices/" + random_str() + '.wav'
    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.post(url, json=data)
        newurl = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azusa-Bert-VITS2-2.3/gradio/file=" + \
                 r.json().get("data")[1].get("name")
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.get(newurl)
            with open(p, "wb") as f:
                f.write(r.content)
            return p

async def change_sample_rate(path,new_sample_rate=44100):
    #wavfile = path  # 提取音频文件名，如“1.wav"
    # new_file_name = wavfile.split('.')[0] + '_8k.wav'      #此行代码可用于对转换后的文件进行重命名（如有需要）

    signal, sr = librosa.load(path, sr=None)  # 调用librosa载入音频

    new_signal = librosa.resample(signal, orig_sr=sr, target_sr=new_sample_rate)  # 调用librosa进行音频采样率转换

    new_path = path # 指定输出音频的路径，音频文件与原音频同名
    # new_path = os.path.join(new_dir_path, new_file_name)      #若需要改名则启用此行代码
    #print("?")
    #print(new_path)

    # librosa.output.write_wav(new_path, new_signal , new_sample_rate)      #因版本问题，此方法可能用不了
    soundfile.write(new_path, new_signal, new_sample_rate)

#asyncio.run(outVits({"text":"你好啊，你吃饭了吗，今天吃的怎么样，开心吗？",'speaker':"黑塔"}))
