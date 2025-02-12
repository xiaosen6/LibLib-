from LibLib import Text2img
import time

def main():
    test = Text2img()
    
    # 基础提示词
    base_prompt = "1girl,solo,high heels,sexy,pencil skirt,kneeling,lips,a slender and petite Asian woman, wearing black stockings,bedroom"
    
    print("=== 开始生成高质量图像 ===")
    # 增强的标准方案
    enhanced_prompt = base_prompt + ",masterpiece,best quality,highly detailed,perfect lighting"
    params = {
        "width": 1024,
        "height": 1024,
        "steps": 22,
        "imgCount": 2,
        "cfgScale": 7,
        "sampler": 15,
        "seed": -1,
        "additionalNetwork": [
            {
                "modelId": "b3b422dbdb154792aac19fe2bdba310e",
                "weight": 0.8
            }
        ],
        "hiResFixInfo": {
            "hiresDenoisingStrength": 0.65,
            "hiresSteps": 15,
            "resizedHeight": 1024,
            "resizedWidth": 1024,
            "upscaler": 10
        }
    }
    
    # 第一次尝试
    print("使用标准模式生成高质量图像...")
    result = test.text2img(enhanced_prompt, params)
    
    if result and not isinstance(result, str):
        print("图像生成完成！")
    else:
        print(f"第一次尝试失败: {result}")
        print("\n等待15秒后进行第二次尝试...")
        time.sleep(15)
        
        # 如果失败，尝试不同的模型组合
        print("尝试不同的模型组合...")
        params.update({
            "steps": 20,
            "additionalNetwork": [
                {
                    "modelId": "4b85a715f7b0414eb142c64c3ab08b98",  # 使用不同的模型
                    "weight": 0.7
                }
            ],
            "hiResFixInfo": {
                "hiresDenoisingStrength": 0.60,
                "hiresSteps": 12,
                "resizedHeight": 1024,
                "resizedWidth": 1024,
                "upscaler": 10
            }
        })
        result = test.text2img(enhanced_prompt, params)
        
        if result and not isinstance(result, str):
            print("第二次尝试成功！")
        else:
            print(f"第二次尝试也失败了: {result}")

if __name__ == '__main__':
    main() 