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
        image_path = "resources/P70Pro1.jpg"
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
        
        html_result = """
            <div class="relative w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video bg-white relative z-20 mx-auto overflow-hidden">
            <!-- Background Image -->
            <img src="https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg" alt="Background" class="absolute inset-0 w-full h-full object-cover">

            <!-- Logo and Brand -->
            <div class="absolute top-6 left-6 flex items-center space-x-2">
                <div class="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center text-white font-bold text-lg">i</div>
                <span class="text-gray-700 font-bold text-xl font-['微软雅黑']">TDTECH</span>
            </div>

            <!-- Main Title -->
            <div class="absolute top-32 left-1/2 transform -translate-x-1/2 text-center px-4">
                <h1 class="text-3xl md:text-4xl font-bold text-gray-800 font-['微软雅黑'] leading-tight">
                基于HUAWEI<br>Mate 70 Pro定制的行业终端
                </h1>
            </div>

            <!-- Subtitle -->
            <div class="absolute top-56 left-1/2 transform -translate-x-1/2 text-center px-4">
                <div class="inline-block bg-white bg-opacity-90 px-6 py-2 rounded-full border border-gray-300 text-gray-700 font-medium text-lg font-['微软雅黑']">
                移动安全 鼎力相助
                </div>
            </div>

            <!-- Features Line -->
            <div class="absolute top-64 left-1/2 transform -translate-x-1/2 text-center px-4 text-gray-600 text-sm font-['微软雅黑']">
                北斗卫星消息 | 红枫原色影像 | 超可靠玄武架构
            </div>

            <!-- Phone Images -->
            <div class="absolute top-72 left-1/2 transform -translate-x-1/2 flex space-x-6">
                <img src="https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg" alt="Phone Back" class="w-40 h-80 object-contain">
                <img src="https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg" alt="Phone Front" class="w-40 h-80 object-contain">
            </div>

            <!-- Customization Section Header -->
            <div class="absolute bottom-64 left-1/2 transform -translate-x-1/2 text-center px-4">
                <div class="flex items-center justify-center space-x-2">
                <div class="w-1 h-6 bg-red-500"></div>
                <h2 class="text-xl font-bold text-gray-800 font-['微软雅黑']">定制能力</h2>
                <div class="w-1 h-6 bg-red-500"></div>
                </div>
            </div>

            <!-- Feature Cards -->
            <div class="absolute bottom-20 left-1/2 transform -translate-x-1/2 grid grid-cols-3 gap-6 w-11/12 max-w-6xl">
                <!-- Card 1 -->
                <div class="flex flex-col items-start space-y-2">
                <div class="flex items-center space-x-2">
                    <div class="w-10 h-10 bg-white border border-gray-300 rounded flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <path d="M12 8v4l2 2"></path>
                    </svg>
                    </div>
                    <div class="text-sm font-semibold text-gray-700 font-['微软雅黑']">行业鸿蒙</div>
                </div>
                <div class="text-xs text-gray-600 font-['微软雅黑'] leading-tight">
                    国产操作系统行业定制<br>
                    分布式可信互联，应用跨设备流转
                </div>
                </div>

                <!-- Card 2 -->
                <div class="flex flex-col items-start space-y-2">
                <div class="flex items-center space-x-2">
                    <div class="w-10 h-10 bg-white border border-gray-300 rounded flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                        <path d="M7 11V7a4 4 0 0 1 8 0v4"></path>
                        <path d="M12 11v4"></path>
                    </svg>
                    </div>
                    <div class="text-sm font-semibold text-gray-700 font-['微软雅黑']">安全架构</div>
                </div>
                <div class="text-xs text-gray-600 font-['微软雅黑'] leading-tight">
                    系统级防root防刷机，安全启动<br>
                    系统加密，应用安全隔离
                </div>
                </div>

                <!-- Card 3 -->
                <div class="flex flex-col items-start space-y-2">
                <div class="flex items-center space-x-2">
                    <div class="w-10 h-10 bg-white border border-gray-300 rounded flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="3" y1="9" x2="21" y2="9"></line>
                        <line x1="9" y1="21" x2="9" y2="9"></line>
                    </svg>
                    </div>
                    <div class="text-sm font-semibold text-gray-700 font-['微软雅黑']">设备管控</div>
                </div>
                <div class="text-xs text-gray-600 font-['微软雅黑'] leading-tight">
                    适配行业MDM管控平台<br>
                    外设接口管控，一键清除设备数据
                </div>
                </div>

                <!-- Card 4 -->
                <div class="flex flex-col items-start space-y-2">
                <div class="flex items-center space-x-2">
                    <div class="w-10 h-10 bg-white border border-gray-300 rounded flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="16" y2="13"></line>
                        <line x1="16" y1="17" x2="16" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                    </div>
                    <div class="text-sm font-semibold text-gray-700 font-['微软雅黑']">内容定制</div>
                </div>
                <div class="text-xs text-gray-600 font-['微软雅黑'] leading-tight">
                    应用预置/保活/自启动/防卸载<br>
                    开机动画定制，产品包装定制
                </div>
                </div>

                <!-- Card 5 -->
                <div class="flex flex-col items-start space-y-2">
                <div class="flex items-center space-x-2">
                    <div class="w-10 h-10 bg-white border border-gray-300 rounded flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <path d="M12 8v4l2 2"></path>
                    </svg>
                    </div>
                    <div class="text-sm font-semibold text-gray-700 font-['微软雅黑']">定位增强</div>
                </div>
                <div class="text-xs text-gray-600 font-['微软雅黑'] leading-tight">
                    单北斗定位<br>
                    模糊定位
                </div>
                </div>

                <!-- Card 6 -->
                <div class="flex flex-col items-start space-y-2">
                <div class="flex items-center space-x-2">
                    <div class="w-10 h-10 bg-white border border-gray-300 rounded flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="16" y2="13"></line>
                        <line x1="16" y1="17" x2="16" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                    </div>
                    <div class="text-sm font-semibold text-gray-700 font-['微软雅黑']">场景化方案</div>
                </div>
                <div class="text-xs text-gray-600 font-['微软雅黑'] leading-tight">
                    全局水印，企业黄页<br>
                    物理按键定制
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
    
