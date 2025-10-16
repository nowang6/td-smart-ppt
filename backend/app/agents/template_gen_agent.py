import os
import base64
from typing import Optional, List
from fastapi import HTTPException
from openai import OpenAI
from openai import APIError
from app.core.config import settings
from app.agents.temp_gen_prompt import GENERATE_HTML_SYSTEM_PROMPT, HTML_TO_REACT_SYSTEM_PROMPT
model = "qwen-vl-max"

async def generate_html_from_slide_with_aliyun(
    base64_image: str,
    media_type: str,
    xml_content: str,
    fonts: Optional[List[str]] = None,
) -> str:
    """
    使用阿里云百炼API从幻灯片图片和XML生成HTML内容。

    Args:
        base64_image: Base64编码的图片数据
        media_type: 图片的MIME类型 (e.g., 'image/png')
        xml_content: OXML内容文本
        fonts: 可选的字体列表，用于在输出中优先使用

    Returns:
        生成的HTML内容字符串

    Raises:
        HTTPException: 如果API调用失败或未生成内容
    """
    print("使用阿里云百炼API从幻灯片图片和XML生成HTML内容...")
    
    try:
        # 创建阿里云百炼客户端
        client = OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        # 构建数据URL
        data_url = f"data:{media_type};base64,{base64_image}"
        
        # 构建字体文本
        fonts_text = (
            f"\nFONTS (Normalized root families used in this slide, use where it is required): {', '.join(fonts)}"
            if fonts
            else ""
        )
        user_text = f"OXML: \n\n{fonts_text}"
        
        # 构建消息
        messages = [
            {"role": "system", "content": GENERATE_HTML_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text", "text": user_text},
                ],
            },
        ]

        print("正在向阿里云百炼API发送请求生成HTML...")
        
        # 调用阿里云百炼API
        response = client.chat.completions.create(
            model=model,  # 使用阿里云百炼的视觉模型
            messages=messages
        )

        # 提取响应内容
        html_content = response.choices[0].message.content or ""

        print(f"收到HTML内容长度: {len(html_content)}")

        if not html_content:
            raise HTTPException(
                status_code=500, detail="阿里云百炼API未生成HTML内容"
            )

        return html_content

    except APIError as e:
        print(f"阿里云百炼API错误: {e}")
        raise HTTPException(
            status_code=500, detail=f"阿里云百炼API调用失败: {str(e)}"
        )
    except Exception as e:
        # 处理各种API错误
        error_msg = str(e)
        print(f"发生异常: {error_msg}")
        print(f"异常类型: {type(e)}")
        
        if "timeout" in error_msg.lower():
            raise HTTPException(
                status_code=408,
                detail=f"阿里云百炼API超时: {error_msg}",
            )
        elif "connection" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail=f"阿里云百炼API连接错误: {error_msg}",
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"阿里云百炼API错误: {error_msg}",
            )


async def generate_html_from_image_file(
    image_path: str,
    xml_content: str,
    fonts: Optional[List[str]] = None,
) -> str:
    """
    从图片文件路径和XML内容生成HTML。

    Args:
        image_path: 图片文件路径
        xml_content: OXML内容文本
        fonts: 可选的字体列表

    Returns:
        生成的HTML内容字符串

    Raises:
        HTTPException: 如果文件不存在或处理失败
    """
    try:
        # 检查图片文件是否存在
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=404, detail=f"图片文件未找到: {image_path}"
            )

        # 读取并编码图片为base64
        with open(image_path, "rb") as image_file:
            image_content = image_file.read()
        base64_image = base64.b64encode(image_content).decode("utf-8")

        # 根据文件扩展名确定媒体类型
        file_extension = os.path.splitext(image_path)[1].lower()
        media_type_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        media_type = media_type_map.get(file_extension, "image/png")

        # 生成HTML
        html_content = await generate_html_from_slide_with_aliyun(
            base64_image=base64_image,
            media_type=media_type,
            xml_content=xml_content,
            fonts=fonts,
        )

        # 清理HTML内容，移除markdown代码块标记
        html_content = html_content.replace("```html", "").replace("```", "")

        return html_content

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 记录完整错误用于调试
        print(f"处理图片文件时发生意外错误: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"处理图片文件错误: {str(e)}"
        )


async def generate_react_component_from_html(
    html_content: str,
    image_base64: Optional[str] = None,
    media_type: Optional[str] = None,
) -> str:
    try:
        # 创建阿里云百炼客户端
        client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )

        print("正发送请求生成React组件...")

        # 构建消息内容
        content_parts = [{"type": "text", "text": f"HTML INPUT:\n{html_content}"}]
        if image_base64 and media_type:
            data_url = f"data:{media_type};base64,{image_base64}"
            content_parts.insert(0, {"type": "image_url", "image_url": {"url": data_url}})

        messages = [
            {"role": "system", "content": HTML_TO_REACT_SYSTEM_PROMPT},
            {"role": "user", "content": content_parts},
        ]

        # 调用阿里云百炼API
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            max_tokens=16000
        )

        # 提取响应内容
        react_content = response.choices[0].message.content or ""

        print(f"收到React内容长度: {len(react_content)}")

        if not react_content:
            raise HTTPException(
                status_code=500, detail="阿里云百炼API未生成React组件"
            )

        # 清理React内容，移除markdown代码块标记
        react_content = (
            react_content.replace("```tsx", "")
            .replace("```", "")
            .replace("typescript", "")
            .replace("javascript", "")
        )

        # 过滤掉以import或export开头的行
        filtered_lines = []
        for line in react_content.split("\n"):
            stripped_line = line.strip()
            if not (
                stripped_line.startswith("import ")
                or stripped_line.startswith("export ")
            ):
                filtered_lines.append(line)

        filtered_react_content = "\n".join(filtered_lines)
        print(f"过滤后的React内容长度: {len(filtered_react_content)}")

        return filtered_react_content

    except APIError as e:
        print(f"阿里云百炼API错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"阿里云百炼API调用失败: {str(e)}",
        )
    except Exception as e:
        # 处理各种API错误
        error_msg = str(e)
        print(f"发生异常: {error_msg}")
        print(f"异常类型: {type(e)}")
        
        if "timeout" in error_msg.lower():
            raise HTTPException(
                status_code=408,
                detail=f"阿里云百炼API超时: {error_msg}",
            )
        elif "connection" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail=f"阿里云百炼API连接错误: {error_msg}",
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"阿里云百炼API错误: {error_msg}",
            )


async def convert_html_to_react_with_aliyun(
    html_content: str,
    image_path: Optional[str] = None,
) -> dict:
    """
    兼容原有html-to-react接口的函数，使用阿里云百炼API
    
    Args:
        html_content: HTML内容
        image_path: 可选的图片文件路径
        
    Returns:
        包含success和react_component字段的字典，与原接口兼容
    """
    try:
        # 验证HTML内容
        if not html_content or not html_content.strip():
            return {
                "success": False,
                "react_component": "",
                "error": "HTML内容不能为空"
            }

        # 可选处理图片
        image_b64 = None
        media_type = None
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode("utf-8")
            ext = os.path.splitext(image_path)[1].lower()
            media_type = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".webp": "image/webp",
            }.get(ext, "image/png")

        # 转换HTML为React组件
        react_component = await generate_react_component_from_html(
            html_content=html_content,
            image_base64=image_b64,
            media_type=media_type,
        )

        # 清理React组件内容
        react_component = react_component.replace("```tsx", "").replace("```", "")

        return {
            "success": True,
            "react_component": react_component,
            "message": "React组件生成成功"
        }

    except Exception as e:
        return {
            "success": False,
            "react_component": "",
            "error": str(e)
        }


# 使用示例
async def example_usage():
    """
    使用示例：展示如何使用阿里云百炼API生成HTML模板
    
    需要设置环境变量：
    - DASHSCOPE_API_KEY: 阿里云百炼API密钥
    """
    
    # 示例1: 从图片文件生成HTML
    try:
        image_path = "/path/to/your/slide/image.png"
        xml_content = "<your-oxml-content>"
        fonts = ["Poppins", "Arial", "Helvetica"]
        
        html_result = await generate_html_from_image_file(
            image_path=image_path,
            xml_content=xml_content,
            fonts=fonts
        )
        
        print("生成的HTML:")
        print(html_result)
        
    except Exception as e:
        print(f"生成HTML时出错: {e}")
    
    # 示例2: 从base64图片数据生成HTML
    try:
        with open("/path/to/your/slide/image.png", "rb") as f:
            image_data = f.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        
        html_result = await generate_html_from_slide_with_aliyun(
            base64_image=base64_image,
            media_type="image/png",
            xml_content="<your-oxml-content>",
            fonts=["Poppins", "Arial"]
        )
        
        print("生成的HTML:")
        print(html_result)
        
    except Exception as e:
        print(f"生成HTML时出错: {e}")


# 如果需要替换原有的slide_to_html功能，可以使用以下函数
async def convert_slide_to_html_with_aliyun(
    image_path: str,
    xml_content: str,
    fonts: Optional[List[str]] = None,
) -> dict:
    """
    兼容原有slide_to_html接口的函数，使用阿里云百炼API
    
    Args:
        image_path: 图片文件路径
        xml_content: OXML内容
        fonts: 可选字体列表
        
    Returns:
        包含success和html字段的字典，与原接口兼容
    """
    try:
        html_content = await generate_html_from_image_file(
            image_path=image_path,
            xml_content=xml_content,
            fonts=fonts
        )
        
        return {
            "success": True,
            "html": html_content
        }
        
    except Exception as e:
        return {
            "success": False,
            "html": "",
            "error": str(e)
        }


async def main():
    
    # 示例XML内容
    sample_xml = """
    <p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
        <p:cSld>
            <p:spTree>
                <p:sp>
                    <p:txBody>
                        <a:p>
                            <a:r>
                                <a:t>示例幻灯片标题</a:t>
                            </a:r>
                        </a:p>
                    </p:txBody>
                </p:sp>
            </p:spTree>
        </p:cSld>
    </p:sld>
    """
    
    # 示例字体列表
    sample_fonts = ["Poppins", "Arial", "Helvetica"]
    
    print("\n=== 使用图片文件生成HTML ===")
    try:
        # 创建一个示例图片路径（实际使用时请替换为真实路径）
        sample_image_path = "/tmp/sample_slide.png"
        
        # 如果文件不存在，创建一个简单的示例
        if not os.path.exists(sample_image_path):
            print(f"⚠️  示例图片文件不存在: {sample_image_path}")
            print("请将实际的幻灯片图片放在该路径，或修改sample_image_path变量")
            print("跳过图片文件测试...")
        else:
            print(f"📁 使用图片文件: {sample_image_path}")
            html_result = await generate_html_from_image_file(
                image_path=sample_image_path,
                xml_content=sample_xml,
                fonts=sample_fonts
            )
            print("✅ HTML生成成功!")
            print(f"📄 生成的HTML长度: {len(html_result)} 字符")
            print("📋 HTML预览:")
            print("-" * 50)
            print(html_result[:200] + "..." if len(html_result) > 200 else html_result)
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ 测试1失败: {e}")
    
    
    print("\n=== HTML转React组件测试 ===")
    try:
        # 创建一个示例HTML内容
        sample_html = """
        <div class="relative w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video bg-white relative z-20 mx-auto overflow-hidden">
            <div class="flex flex-col h-full px-8 py-8">
                <h1 class="text-4xl font-bold text-gray-900 mb-4">示例标题</h1>
                <p class="text-lg text-gray-700 mb-6">这是一个示例描述文本，用于测试HTML转React功能。</p>
                <div class="flex space-x-4">
                    <div class="flex-1 bg-blue-100 p-4 rounded-lg">
                        <h3 class="text-xl font-semibold mb-2">特性1</h3>
                        <p class="text-gray-600">描述特性1的内容</p>
                    </div>
                    <div class="flex-1 bg-green-100 p-4 rounded-lg">
                        <h3 class="text-xl font-semibold mb-2">特性2</h3>
                        <p class="text-gray-600">描述特性2的内容</p>
                    </div>
                </div>
            </div>
        </div>
        """
        
        print("📝 使用示例HTML内容")
        react_result = await convert_html_to_react_with_aliyun(
            html_content=sample_html,
            image_path=None  # 不使用图片
        )
        
        if react_result["success"]:
            print("✅ HTML转React组件测试成功!")
            print(f"📄 生成的React组件长度: {len(react_result['react_component'])} 字符")
            print("📋 React组件预览:")
            print("-" * 50)
            preview = react_result['react_component'][:400]
            print(preview + "..." if len(react_result['react_component']) > 400 else preview)
            print("-" * 50)
        else:
            print(f"❌ HTML转React组件测试失败: {react_result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 测试4失败: {e}")
    


if __name__ == "__main__":
    import asyncio
    
    async def run_example():
        image_path = "resources/P70Pro2.jpg"
        xml_content = """
        <p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
            <p:cSld>
                <p:spTree>
                    <p:sp>
                        <p:txBody>
                            <a:p>
                                <a:r>
                                    <a:t>示例幻灯片标题</a:t>
                                </a:r>
                            </a:p>
                        </p:txBody>
                    </p:sp>
                </p:spTree>
            </p:cSld>
        </p:sld>
        """
        
        html_result = """<div class="relative w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video bg-white relative z-20 mx-auto overflow-hidden">
  <div class="flex flex-col h-full p-6">
    <!-- Header Section -->
    <div class="text-3xl font-bold mb-6 text-gray-800 font-['微软雅黑']">解决方案</div>
    
    <!-- Solution Cards Row 1 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <!-- Mine Communication Card -->
      <div class="flex flex-col">
        <img src="https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg" alt="Mine Communication" class="w-24 h-24 object-cover rounded-md mb-2" />
        <div class="flex flex-col">
          <h3 class="font-bold text-lg text-gray-800 font-['微软雅黑']">矿务通</h3>
          <div class="mt-2 text-sm text-gray-600 font-['微软雅黑']">
            <p>防爆电池改造、电池防伪、电池保护</p>
            <p>适配矿山井下专网，支持高清音视频通话</p>
            <p>支持矿鸿软总线，多设备协同管理、卡片化呈现</p>
          </div>
        </div>
      </div>

      <!-- Quantum Secure Call Card -->
      <div class="flex flex-col">
        <img src="https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg" alt="Quantum Secure Call" class="w-24 h-24 object-cover rounded-md mb-2" />
        <div class="flex flex-col">
          <h3 class="font-bold text-lg text-gray-800 font-['微软雅黑']">量子密话</h3>
          <div class="mt-2 text-sm text-gray-600 font-['微软雅黑']">
            <p>量子加密，一话一密，端到端加密</p>
            <p>原生拨号盘定制，一键拨打VoLTE高清通话</p>
            <p>来电明密识别，显性状态提示</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Solution Cards Row 2 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <!-- Conference Call Card -->
      <div class="flex flex-col">
        <img src="https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg" alt="Conference Call" class="w-24 h-24 object-cover rounded-md mb-2" />
        <div class="flex flex-col">
          <h3 class="font-bold text-lg text-gray-800 font-['微软雅黑']">和对讲</h3>
          <div class="mt-2 text-sm text-gray-600 font-['微软雅黑']">
            <p>专业对讲，音量键长按发起频道沟通</p>
            <p>调度平台适配，保持终端数据长连接</p>
            <p>应用预置，和对讲APP预置/保活/卸载</p>
          </div>
        </div>
      </div>

      <!-- Government Security Card -->
      <div class="flex flex-col">
        <img src="https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg" alt="Government Security" class="w-24 h-24 object-cover rounded-md mb-2" />
        <div class="flex flex-col">
          <h3 class="font-bold text-lg text-gray-800 font-['微软雅黑']">政企通</h3>
          <div class="mt-2 text-sm text-gray-600 font-['微软雅黑']">
            <p>应用安全隔离</p>
            <p>国密算法，端到端加密</p>
            <p>MDM设备安全管控</p>
            <p>防信息海外泄露</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Product Title -->
    <div class="text-2xl font-bold mb-6 text-gray-800 font-['微软雅黑']">HUAWEI Mate 70 Pro</div>

    <!-- Specifications Table -->
    <div class="overflow-x-auto mb-8">
      <table class="w-full border-collapse">
        <thead>
          <tr class="bg-gray-200">
            <th class="border px-4 py-2 text-left text-sm font-medium text-gray-700 font-['微软雅黑']">产品规格</th>
            <th class="border px-4 py-2 text-left text-sm font-medium text-gray-700 font-['微软雅黑']"></th>
          </tr>
        </thead>
        <tbody>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">操作系统</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">HarmonyOS 4.3</td>
          </tr>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">双卡</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">双卡双待双通</td>
          </tr>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">屏幕</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">屏幕尺寸: 6.9英寸 分辨率: FHD+ 2832×1316像素 屏幕像素密度: 454 PPI<br />OLED; 支持1-120Hz LTPO自适应刷新率, 1440Hz高帧PWM调光, 300Hz触控采样率 第二代昆仑玻璃</td>
          </tr>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">传感器</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">3D人脸识别, 环境光传感器, 红外传感器, 指纹传感器, 霍尔传感器, 陀螺仪, 指南针, NFC, 气压计, 接近光传感器<br />重力传感器, 姿态感应器, Camera激光对焦传感器, 色温传感器</td>
          </tr>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">存储</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">运行内存 (RAM): 12GB RAM, 机身内存 (ROM): 256GB / 512GB</td>
          </tr>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">拍摄功能</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">后置摄像头: 5000万像素超聚光摄像头 (F1.4-F4.0光圈, OIS光学防抖) +4000万像素超广角摄像头 (F2.2光圈)<br />+4800万像素超聚光微距长焦摄像头 (F2.1光圈, OIS光学防抖) +150万多元谱通道红枫原色摄像头<br />前置摄像头: 1300万像素超广角摄像头 (F2.4光圈) +3D深感摄像头</td>
          </tr>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">WLAN</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">2.4GHz和5GHz, 802.11 a/b/g/n/ac/ax, 2x2 MIMO, HE160, 1024 QAM, 8 Spatial-stream Sounding MU-MIMO</td>
          </tr>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">蓝牙</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">Bluetooth 5.2, 支持低功耗蓝牙, 支持SBC、AAC, 支持LDAC和L2HC高清音频</td>
          </tr>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">定位</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">支持GPS (L1+L5双频) /AGPS/GLONASS/北斗 (B1I+B1C+B2a+B2b四频) /GALILEO (E1+E5a+E5b三频)<br />QZSS (L1+L5双频) /NavIC</td>
          </tr>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">电池容量</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">5500mAh (典型值)</td>
          </tr>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">充电</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">有线充电: 手机支持最大超级快充100W (20V/5A), 兼容20V/4.4A或11V/6A或10V/4A或10V/2.25A或4.5V/5A或5V/4.5A超级快充, 兼容9V/2A快充, 支持18W有线反向充电<br />无线充电: 支持80W华为无线超级快充, 支持20W无线反向充电</td>
          </tr>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">机身尺寸</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">164.6mm (长) ×79.5mm (宽) ×8.2mm (厚)</td>
          </tr>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">机身重量</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">约221克 (含电池)</td>
          </tr>
          <tr class="border-t">
            <td class="px-4 py-2 text-sm font-medium text-gray-700 font-['微软雅黑']">防尘抗水</td>
            <td class="px-4 py-2 text-sm text-gray-600 font-['微软雅黑']">IP68级6米抗水, IP69级抗高温高压喷水</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Footer with QR Codes and Contacts -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
      <div class="flex space-x-4">
        <div class="flex flex-col items-center">
          <img src="https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg" alt="QR Code" class="w-24 h-24 object-cover" />
          <p class="text-xs text-gray-500 mt-1 font-['微软雅黑']">关注群聊通信，了解更多信息</p>
        </div>
        <div class="flex flex-col items-center">
          <img src="https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg" alt="QR Code" class="w-24 h-24 object-cover" />
          <p class="text-xs text-gray-500 mt-1 font-['微软雅黑']">关注群聊通信，了解更多信息</p>
        </div>
      </div>

      <div class="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-12">
        <div class="text-sm font-['微软雅黑']">
          <p class="font-bold text-gray-800">北京</p>
          <p>北京市朝阳区望京北路9号</p>
          <p>叶青大厦C座1层</p>
          <p><span class="text-gray-500">📞</span> +86 010 58223366</p>
          <p><span class="text-gray-500">📱</span> +86 010 58223466</p>
        </div>
        <div class="text-sm font-['微软雅黑']">
          <p class="font-bold text-gray-800">上海</p>
          <p>上海市浦东新区新金桥路1888号楼</p>
          <p>55号楼1-5层</p>
          <p><span class="text-gray-500">📞</span> +86 021 60612008</p>
          <p><span class="text-gray-500">📱</span> +86 021 60612009</p>
        </div>
        <div class="text-sm font-['微软雅黑']">
          <p class="font-bold text-gray-800">成都</p>
          <p>中国 (四川) 自由贸易试验区成都市高新区</p>
          <p>天华二路219号C区3栋</p>
          <p><span class="text-gray-500">📞</span> +86 028 63906008</p>
          <p><span class="text-gray-500">📱</span> +86 028 63906007</p>
        </div>
      </div>
    </div>
  </div>
</div>
            """
         
        react_result = await generate_react_component_from_html(
            html_content=html_result,
            image_base64=None,
            media_type=None
        )
        print(react_result)
        
        # sample_fonts = ["微软雅黑", "Arial"]
        # html_result = await generate_html_from_image_file(
        #     image_path=image_path,
        #     xml_content=xml_content,
        #     fonts=sample_fonts
        # )
        # print(html_result)
    
    # 运行异步函数
    asyncio.run(run_example())
    
