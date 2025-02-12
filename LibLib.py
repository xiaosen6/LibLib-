import hmac
import time
import requests
from datetime import datetime
import hashlib
import uuid
import base64
import os

class ImageConfig:
    def __init__(self):
        self.default_config = {  
            "checkPointId": "8d7785156c4d4c71b94df311be467537",    # 8d7785156c4d4c71b94df311be467537
            "prompt": "",
            "negativePrompt": "ng_deepnegative_v1_75t,(badhandv4:1.2),EasyNegative,(worst quality:2),",
            "width": 1024,
            "height": 1024,
            "imgCount": 2,
            "cfgScale": 5,
            "randnSource": 1,
            "seed": -1,
            "clipSkip": 2,
            "sampler": 15,
            "steps": 20,
            "restoreFaces": 0,
        }
        
        self.ultra_config = {
            **self.default_config,
            "steps": 20,
            "imgCount": 2,
            "aspectRatio": "portrait",
            "imageSize": "1024x1024"
        }

class Text2img:
    def __init__(self, ak='5vldHnK9Zu-jd_C5BRpguQ', sk='DGXN9Oem2Jd25aggpmilhIBguBbL17X3', interval=5):
        """
        :param ak: 访问密钥
        :param sk: 秘密密钥
        :param interval: 轮询间隔
        """
        self.ak = ak
        self.sk = sk
        self.interval = interval
        self.headers = {'Content-Type': 'application/json'}
        self.config = ImageConfig()
        self.output_dir = "generated_images"
        os.makedirs(self.output_dir, exist_ok=True)
        self._update_signatures()

    def _update_signatures(self):
        """更新所有签名"""
        self.time_stamp = int(datetime.now().timestamp() * 1000)
        self.signature_nonce = uuid.uuid1()
        self.signature_img = self._hash_sk(self.sk, self.time_stamp, self.signature_nonce)
        self.signature_ultra_img = self._hash_ultra_sk(self.sk, self.time_stamp, self.signature_nonce)
        self.signature_status = self._hash_sk_status(self.sk, self.time_stamp, self.signature_nonce)
        # 更新URL
        self.text2img_url = self.get_image_url(self.ak, self.signature_img, self.time_stamp, self.signature_nonce)
        self.text2img_ultra_url = self.get_ultra_image_url(self.ak, self.signature_ultra_img, self.time_stamp, self.signature_nonce)
        self.generate_url = self.get_generate_url(self.ak, self.signature_status, self.time_stamp, self.signature_nonce)

    def hmac_sha1(self, key, code):
        hmac_code = hmac.new(key.encode(), code.encode(), hashlib.sha1)
        return hmac_code.digest()

    def _hash_sk(self, key, s_time, ro):
        """加密sk"""
        data = "/api/generate/webui/text2img" + "&" + str(s_time) + "&" + str(ro)
        s = base64.urlsafe_b64encode(self.hmac_sha1(key, data)).rstrip(b'=').decode()
        return s

    def _hash_ultra_sk(self, key, s_time, ro):
        """加密sk"""
        data = "/api/generate/webui/text2img/ultra" + "&" + str(s_time) + "&" + str(ro)
        s = base64.urlsafe_b64encode(self.hmac_sha1(key, data)).rstrip(b'=').decode()
        return s

    def _hash_sk_status(self, key, s_time, ro):
        """加密sk"""
        data = "/api/generate/webui/status" + "&" + str(s_time) + "&" + str(ro)
        s = base64.urlsafe_b64encode(self.hmac_sha1(key, data)).rstrip(b'=').decode()
        return s

    def get_image_url(self, ak, signature, time_stamp, signature_nonce):
        url = f"https://openapi.liblibai.cloud/api/generate/webui/text2img?AccessKey={ak}&Signature={signature}&Timestamp={time_stamp}&SignatureNonce={signature_nonce}"
        return url

    def get_ultra_image_url(self, ak, signature, time_stamp, signature_nonce):
        url = f"https://openapi.liblibai.cloud/api/generate/webui/text2img/ultra?AccessKey={ak}&Signature={signature}&Timestamp={time_stamp}&SignatureNonce={signature_nonce}"
        return url

    def get_generate_url(self, ak, signature, time_stamp, signature_nonce):
        url = f"https://openapi.liblibai.cloud/api/generate/webui/status?AccessKey={ak}&Signature={signature}&Timestamp={time_stamp}&SignatureNonce={signature_nonce}"
        return url

    def ultra_text2img(self, prompt, additional_params=None):
        """
        Ultra高质量文生图
        :param prompt: 提示词
        :param additional_params: 额外的参数配置
        """
        params = self.config.ultra_config.copy()
        params["prompt"] = prompt
        if additional_params:
            params.update(additional_params)

        base_json = {
            "templateUuid": "5d7e67009b344550bc1aa6ccbfa1d7f4",
            "generateParams": {
                **params,
                "additionalNetwork": [
                    {
                        "modelId": "b3b422dbdb154792aac19fe2bdba310e",  # 使用相同的模型ID
                        "weight": 0.6
                    }
                ],
                "hiResFixInfo": {
                    "hiresDenoisingStrength": 0.80,
                    "hiresSteps": 15,
                    "resizedHeight": 1024,  # 固定分辨率
                    "resizedWidth": 1024,   # 固定分辨率
                    "upscaler": 10
                }
            }
        }
        return self.run(base_json, self.text2img_ultra_url)

    def text2img(self, prompt, additional_params=None):
        """
        标准文生图
        :param prompt: 提示词
        :param additional_params: 额外的参数配置
        """
        params = self.config.default_config.copy()
        params["prompt"] = prompt
        if additional_params:
            params.update(additional_params)

        base_json = {    
            "templateUuid": "5d7e67009b344550bc1aa6ccbfa1d7f4",     # 星流3：5d7e67009b344550bc1aa6ccbfa1d7f4   
            "generateParams": {
                **params,
                "additionalNetwork": [
                    {
                        "modelId": "3b3ac37106a142a39b3408e4517bf682",   # 黑丝高跟鞋模特：b3b422dbdb154792aac19fe2bdba310e  
                        "weight": 0.6
                    },
                    # F.1超模好身材美女写真53号_极致逼真人像摄影:10e5932187ad4b178280a104b3f8c4a6
                    # 写实(清源)_INS风格 v3：874eeccc7a284b2ea73201b96e09b65e
                    # F.1- 黑丝.美.腿：b3b422dbdb154792aac19fe2bdba310e
                    # majicFlus光影MAX_极致光影胶片质感:84376c3283f14c41993b873ee843f67f
                    # 衣服系列_一字肩蕾丝裙:3b3ac37106a142a39b3408e4517bf682
                    {
                        "modelId": "10e5932187ad4b178280a104b3f8c4a6",   # F.1- 白丝.美.腿:e8311e0beae04687b38255282b84e12d
                        "weight": 0.6
                    },
                ],
                "hiResFixInfo": {
                    "hiresDenoisingStrength": 0.80,
                    "hiresSteps": 15,
                    "resizedHeight": params["height"],
                    "resizedWidth": params["width"],
                    "upscaler": 10
                }
            }
        }
        return self.run(base_json, self.text2img_url)

    def run(self, data, url, timeout=120):
        """
        发送任务到生图接口，直到返回image为止，失败抛出异常信息
        """
        # 每次请求前更新签名
        self._update_signatures()
        
        start_time = time.time()
        response = requests.post(url=url, headers=self.headers, json=data)
        response.raise_for_status()
        progress = response.json()
        print(progress)

        if progress['code'] == 0:
            while True:
                current_time = time.time()
                if (current_time - start_time) > timeout:
                    print(f"{timeout}s任务超时，已退出轮询。")
                    return None

                generate_uuid = progress["data"]['generateUuid']
                data = {"generateUuid": generate_uuid}
                # 状态查询前也更新签名
                self._update_signatures()
                response = requests.post(url=self.generate_url, headers=self.headers, json=data)
                response.raise_for_status()
                progress = response.json()
                print(progress)

                if progress['data'].get('images') and any(
                        image for image in progress['data']['images'] if image is not None):
                    print("任务完成，获取到图像数据。")
                    images = progress['data']['images']
                    for idx, img_data in enumerate(images):
                        try:
                            # 检查审核状态
                            if isinstance(img_data, dict):
                                audit_status = img_data.get('auditStatus', 0)
                                if audit_status == 4:
                                    print(f"图片{idx}未通过审核，正在尝试获取原始数据...")
                                    # 这里可以添加获取原始数据的逻辑
                                    continue
                                
                                if 'imageUrl' in img_data and img_data['imageUrl']:
                                    img_url = img_data['imageUrl']
                                    # 下载图片
                                    response = requests.get(img_url)
                                    response.raise_for_status()
                                    img_bytes = response.content
                                    # 保存图片
                                    file_path = os.path.join(self.output_dir, f'output_{idx}.png')
                                    with open(file_path, 'wb') as f:
                                        f.write(img_bytes)
                                    print(f"图片已保存到 {file_path}")
                            elif isinstance(img_data, str):
                                if img_data.startswith('data:'):
                                    mime_type = img_data.split(';')[0].split(':')[1]
                                    if mime_type == 'image/png':
                                        ext = 'png'
                                    elif mime_type == 'image/jpeg':
                                        ext = 'jpg'
                                    else:
                                        ext = 'png'  # 默认
                                    img_data = img_data.split(',')[-1]
                                    img_bytes = base64.b64decode(img_data)
                                    file_path = os.path.join(self.output_dir, f'output_{idx}.{ext}')
                                    with open(file_path, 'wb') as f:
                                        f.write(img_bytes)
                                    print(f"图片已保存到 {file_path}")
                                elif img_data.startswith('http'):
                                    response = requests.get(img_data)
                                    response.raise_for_status()
                                    img_bytes = response.content
                                    file_path = os.path.join(self.output_dir, f'output_{idx}.jpg')
                                    with open(file_path, 'wb') as f:
                                        f.write(img_bytes)
                                    print(f"图片已保存到 {file_path}")
                                else:
                                    print(f"无法识别的图片数据: {img_data}")
                        except Exception as e:
                            print(f"保存图片{idx}时出错: {e}")
                    return progress

                print(f"任务尚未完成，等待 {self.interval} 秒...")
                time.sleep(self.interval)
        else:
            return f'任务失败,原因：code {progress["msg"]}'

def main():
    test = Text2img()
    
    # 基础提示词lower body ,pick up high heels  ,wearing stockings
    base_prompt = "1 sexy girl,solo,high heels,detailed face,sexy and voluptuous body,Semi-exposed chest,off-shoulder lace short dress,Cleavage,high-resolution photo,kneeling,Glamorous thighs,Slightly larger heels,Create dramatic shadows,lips,Asian woman,"
    
    print("=== 开始生成标准图像 ===")
    # 标准生图
    result = test.text2img(base_prompt)
    
    if result and not isinstance(result, str):
        print("标准图像生成完成！")
    else:
        print(f"生成失败: {result}")

if __name__ == '__main__':
    main()