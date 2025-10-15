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
    print(settings.DASHSCOPE_API_KEY)
    
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


async def generate_react_component_from_html_with_aliyun(
    html_content: str,
    image_base64: Optional[str] = None,
    media_type: Optional[str] = None,
) -> str:
    """
    使用阿里云百炼API将HTML内容转换为TSX React组件。

    Args:
        html_content: 生成的HTML内容
        image_base64: 可选的base64编码图片
        media_type: 可选的图片MIME类型

    Returns:
        生成的TSX React组件代码字符串

    Raises:
        HTTPException: 如果API调用失败或未生成内容
    """
    try:
        # 创建阿里云百炼客户端
        client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )

        print("正在向阿里云百炼API发送请求生成React组件...")

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
            messages=messages
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
        react_component = await generate_react_component_from_html_with_aliyun(
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
        
        sample_fonts = ["微软雅黑", "Arial"]
        html_result = await generate_html_from_image_file(
            image_path=image_path,
            xml_content=xml_content,
            fonts=sample_fonts
        )
        print(html_result)
    
    # 运行异步函数
    asyncio.run(run_example())
    
