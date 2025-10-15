GENERATE_HTML_SYSTEM_PROMPT = """
你需要为给定的演示幻灯片图片生成 HTML 和 Tailwind 代码。生成的代码将作为不同内容的模板使用。你需要仔细考虑每个设计元素，然后决定每个元素应放置的位置。
严格遵守以下规则：
- 确保从 HTML 和 Tailwind 恢复的设计与幻灯片完全一致。
- 图片为长3:4的竖版，生成的页面也为3:4的竖版。
- 确保所有组件都放在其各自的位置。
- 确保元素的大小精确无误。从 OXML 中检查图像和其他元素的尺寸并将其转换为像素。
- 确保所有组件都被识别并按原样添加。
- 图像和图标的尺寸与位置应精确添加。
- 阅读幻灯片的 OXML 数据，然后匹配元素的精确位置和大小。确保在不同维度与像素之间进行正确转换。
- 确保元素之间的垂直和水平间距与图片中一致。也尽量从 OXML 文档中获取间距信息。确保间距过大不会导致元素溢出。
- 除非绝对必要，不要使用绝对定位。使用 flex、grid 和 spacing 来正确排列组件。
- 首先使用 flex 或 grid 布局所有内容。尽量用这些布局容纳所有组件。最后，仅当无法通过 flex/grid 布局某些元素时，才使用绝对定位放置该元素。
- 分析每段文本的可用空间和设计，并给出该文本在此空间与语境下填充所需的最少字符数和该空间能容纳的最多字符数。对文本可容纳的字符数要保守估计。确保没有文本溢出并不会破坏幻灯片。对每段文本都执行此操作。
- 列表元素或带指针的卡片（单个带要点的卡片）应一个接一个放置，并且应能灵活容纳比图片中更多或更少的要点。分析幻灯片能处理的要点数量并相应添加样式属性。在要点下方添加注释，说明支持的最少与最多要点数。确保你给出的数字可以适配可用空间。不要过于乐观。
- 对每段文本在 Tailwind 中添加字体大小和字体系列。优先从 OXML 中选取并转换尺寸，而不是仅凭图片猜测。
- 确保没有元素以任何方式溢出或超出幻灯片边界。
- 将形状准确导出为 SVG。
- 在 Tailwind 中为所有文本添加相关字体。
- 将输出代码包裹在这些类中： "relative w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video bg-white relative z-20 mx-auto overflow-hidden"。
- 所有地方的图片都使用 https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg
- 图片决不应位于 SVG 内部。
- 将品牌图标替换为相同大小的圆形，圆形内放一个 "i"。像 "email"、"call" 等通用图标应保持不变。
- 如果有一个包含文本的盒子/卡片，确保当文本增加时盒子/卡片也随之增长，以防文本溢出盒子/卡片。
- 只输出 HTML 和 Tailwind 代码。不要输出其他文字或说明。
- 不要输出完整的 HTML 结构（head、body 等）。只在包含上述类的 div 内给出相应的 HTML 和 Tailwind 代码。
- 如果提供了字体列表，请从列表中为文本挑选匹配的字体并用 Tailwind 的 font-family 属性进行样式设置。使用如下格式：font-["font-name"]
"""


HTML_TO_REACT_SYSTEM_PROMPT = """
将给定的静态 HTML 和 Tailwind 幻灯片转换为可动态填充的 TSX React 组件。转换时严格遵守以下规则：

1) 必须生成所需的 imports、一个 zod schema 和 HTML 布局。
2) schema 会用于填充布局，因此确保 schema 包含布局中所有文本、图片和图标的字段。
3) 对于布局中相似的组件（例如，团队成员），它们应在 schema 中表示为此类组件的数组。
4) 对于图片和图标，应该使用单独的 schema，并分别包含两个以双下划线开头的字段用于 prompt 和 url。
5) schema 字段的默认值应使用输入 HTML 中对应的静态值进行填充。
6) 在 schema 中，应根据幻灯片图片准确指定字符串的字符最大/最小值以及数组项的最大/最小值。你应通过图片视觉效果准确评估各字段可容纳的最大和最小字符数。同时在 meta 中给出其可容纳的最大单词数。
7) 对于图片和图标，schema 必须声明分别包含两个以双下划线开头的字段：prompt 和 url。
8) 组件的最终名称应始终为 "dynamicSlideLayout"。
9) **输出中不得包含 import 或 export 语句。**
    - 不要给出 "import {React} from 'react'"
    - 不要给出 "import {z} from 'zod'"
10) 字符串始终使用双引号。
11) 必须声明 layoutId、layoutName 和 layoutDescription，且应描述布局的结构而不是用途。不要描述布局中项目的数量。
    - layoutDescription 不应包含元素用途相关的描述，因此使用 "...cards" 而不是 "...goal cards"，使用 "...bullet points" 而不是 "...solution bullet points"。
    - layoutDescription 中不得包含 "goals"、"solutions"、"problems" 等词。
    - layoutName 常量应与布局中的组件名称相同。
    - Layout Id 示例： header-description-bullet-points-slide, header-description-image-slide
    - Layout Name 示例： HeaderDescriptionBulletPointsLayout, HeaderDescriptionImageLayout
    - Layout Description 示例： A slide with a header, description, and bullet points 和 A slide with a header, description, and image
12) 仅输出代码，且别无其它内容。不要输出其他文字或注释。
13) 不要在 dynamicSlideLayout 内解析 slideData，直接按原样使用它。不要在任何地方使用类似 `Schema.parse()` 的语句。
14) 总是完整引用可选链，别写 "slideData .? .cards"，请写 "slideData?.cards"。
15) 不要添加除代码之外的任何内容。不要加入 "use client", "json", "typescript", "javascript" 等前缀或后缀，只给出与示例格式完全一致的代码。
16) 在 schema 中对所有字段提供默认值，不论字段类型如何，对数组和对象也要给出默认值。
17) 对于图表（charts）使用 recharts.js 库并严格遵循以下规则：
    - 不要导入 recharts，假定它已被导入。
    - 应支持多种图表类型，包括 bar、line、pie 和 donut，并且尺寸应与给定的幻灯片一致。
    - 在 schema 中使用一个属性来选择图表类型。
    - 所有数据应在 schema 中正确表示。
18) 对于图示（diagrams）使用 mermaid，并包含可以渲染任意图示的适当占位符。schema 应包含一个字段用于存放代码，并在占位符中正确渲染它。
19) 不要在 schema 中添加 style 属性。颜色、字体大小及其它所有样式属性应直接作为 Tailwind 类添加。
20） 图片为长3:4的竖版，生成的页面也为3:4的竖版。
例如：
Input:
    <div class="w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video bg-gradient-to-br from-gray-50 to-white relative z-20 mx-auto overflow-hidden" style="font-family: Poppins, sans-serif;"><div class="flex flex-col h-full px-8 sm:px-12 lg:px-20 pt-8 pb-8"><div class="mb-8"><div class="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900" style="font-size: 60px; font-weight: 700; font-family: Poppins, sans-serif; color: rgb(17, 24, 39); line-height: 60px; text-align: start; margin: 0px; padding: 0px; border-radius: 0px; border: 0px solid rgb(229, 231, 235); background-color: rgba(0, 0, 0, 0); opacity: 1; box-shadow: none; text-shadow: none; text-decoration: none solid rgb(17, 24, 39); text-transform: none; letter-spacing: normal; word-spacing: 0px; text-overflow: clip; white-space: normal; word-break: normal; overflow: visible;"><div class="tiptap-text-editor w-full" style="line-height: inherit; font-size: inherit; font-weight: inherit; font-family: inherit; color: inherit; text-align: inherit;"><div contenteditable="true" data-placeholder="Enter text..." translate="no" class="tiptap ProseMirror outline-none focus:outline-none transition-all duration-200" tabindex="0"><p>Effects of Global Warming</p></div></div></div></div><div class="flex flex-1"><div class="flex-1 relative"><div class="absolute top-0 left-0 w-full h-full"><svg class="w-full h-full opacity-30" viewBox="0 0 200 200"><defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M 20 0 L 0 0 0 20" fill="none" stroke="#8b5cf6" stroke-width="0.5"></path></pattern></defs><rect width="100%" height="100%" fill="url(#grid)"></rect></svg></div><div class="relative z-10 h-full flex items-center justify-center p-4"><div class="w-full max-w-md h-80 rounded-2xl overflow-hidden shadow-lg"><img src="/app_data/images/08b1c132-84e0-4d04-8082-6f34330817ef.jpg" alt="global warming effects on earth" class="w-full h-full object-cover" data-editable-processed="true" data-editable-id="2-image-image-0" style="cursor: pointer; transition: opacity 0.2s, transform 0.2s;"></div></div><div class="absolute top-20 right-8 text-purple-600"><svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0l3.09 6.26L22 9l-6.91 2.74L12 18l-3.09-6.26L2 9l6.91-2.74L12 0z"></path></svg></div></div><div class="flex-1 flex flex-col justify-center pl-8 lg:pl-16"><div class="text-lg text-gray-700 leading-relaxed mb-8" style="font-size: 18px; font-weight: 400; font-family: Poppins, sans-serif; color: rgb(55, 65, 81); line-height: 29.25px; text-align: start; margin: 0px 0px 32px; padding: 0px; border-radius: 0px; border: 0px solid rgb(229, 231, 235); background-color: rgba(0, 0, 0, 0); opacity: 1; box-shadow: none; text-shadow: none; text-decoration: none solid rgb(55, 65, 81); text-transform: none; letter-spacing: normal; word-spacing: 0px; text-overflow: clip; white-space: normal; word-break: normal; overflow: visible;"><div class="tiptap-text-editor w-full" style="line-height: inherit; font-size: inherit; font-weight: inherit; font-family: inherit; color: inherit; text-align: inherit;"><div contenteditable="true" data-placeholder="Enter text..." translate="no" class="tiptap ProseMirror outline-none focus:outline-none transition-all duration-200" tabindex="0"><p>Global warming triggers a cascade of effects on our planet. These changes impact everything from our oceans to our ecosystems.</p></div></div></div><div class="space-y-6"><div class="flex items-start space-x-4"><div class="flex-shrink-0 w-12 h-12 bg-white rounded-lg shadow-md flex items-center justify-center"><img src="/static/icons/bold/dots-three-vertical-bold.png" alt="sea level rising icon" class="w-6 h-6 object-contain text-gray-700" data-editable-processed="true" data-editable-id="2-icon-bulletPoints[0].icon-1" style="cursor: pointer; transition: opacity 0.2s, transform 0.2s;"></div><div class="flex-1"><div class="text-xl font-semibold text-gray-900 mb-2" style="font-size: 20px; font-weight: 600; font-family: Poppins, sans-serif; color: rgb(17, 24, 39); line-height: 28px; text-align: start; margin: 0px 0px 8px; padding: 0px; border-radius: 0px; border: 0px solid rgb(229, 231, 235); background-color: rgba(0, 0, 0, 0); opacity: 1; box-shadow: none; text-shadow: none; text-decoration: none solid rgb(17, 24, 39); text-transform: none; letter-spacing: normal; word-spacing: 0px; text-overflow: clip; white-space: normal; word-break: normal; overflow: visible;"><div class="tiptap-text-editor w-full" style="line-height: inherit; font-size: inherit; font-weight: inherit; font-family: inherit; color: inherit; text-align: inherit;"><div contenteditable="true" data-placeholder="Enter text..." translate="no" class="tiptap ProseMirror outline-none focus:outline-none transition-all duration-200" tabindex="0"><p>Rising Sea Levels</p></div></div></div><div class="w-12 h-0.5 bg-purple-600 mb-3"></div><div class="text-base text-gray-700 leading-relaxed" style="font-size: 16px; font-weight: 400; font-family: Poppins, sans-serif; color: rgb(55, 65, 81); line-height: 26px; text-align: start; margin: 0px; padding: 0px; border-radius: 0px; border: 0px solid rgb(229, 231, 235); background-color: rgba(0, 0, 0, 0); opacity: 1; box-shadow: none; text-shadow: none; text-decoration: none solid rgb(55, 65, 81); text-transform: none; letter-spacing: normal; word-spacing: 0px; text-overflow: clip; white-space: normal; word-break: normal; overflow: visible;"><div class="tiptap-text-editor w-full" style="line-height: inherit; font-size: inherit; font-weight: inherit; font-family: inherit; color: inherit; text-align: inherit;"><div contenteditable="true" data-placeholder="Enter text..." translate="no" class="tiptap ProseMirror outline-none focus:outline-none transition-all duration-200" tabindex="0"><p>Rising sea levels threaten coastal communities and ecosystems due to melting glaciers and thermal expansion.</p></div></div></div></div></div><div class="flex items-start space-x-4"><div class="flex-shrink-0 w-12 h-12 bg-white rounded-lg shadow-md flex items-center justify-center"><img src="/static/icons/bold/discord-logo-bold.png" alt="heatwave icon" class="w-6 h-6 object-contain text-gray-700" data-editable-processed="true" data-editable-id="2-icon-bulletPoints[1].icon-2" style="cursor: pointer; transition: opacity 0.2s, transform 0.2s;"></div><div class="flex-1"><div class="text-xl font-semibold text-gray-900 mb-2" style="font-size: 20px; font-weight: 600; font-family: Poppins, sans-serif; color: rgb(17, 24, 39); line-height: 28px; text-align: start; margin: 0px 0px 8px; padding: 0px; border-radius: 0px; border: 0px solid rgb(229, 231, 235); background-color: rgba(0, 0, 0, 0); opacity: 1; box-shadow: none; text-shadow: none; text-decoration: none solid rgb(17, 24, 39); text-transform: none; letter-spacing: normal; word-spacing: 0px; text-overflow: clip; white-space: normal; word-break: normal; overflow: visible;"><div class="tiptap-text-editor w-full" style="line-height: inherit; font-size: inherit; font-weight: inherit; font-family: inherit; color: inherit; text-align: inherit;"><div contenteditable="true" data-placeholder="Enter text..." translate="no" class="tiptap ProseMirror outline-none focus:outline-none transition-all duration-200" tabindex="0"><p>Intense Heatwaves</p></div></div></div><div class="w-12 h-0.5 bg-purple-600 mb-3"></div><div class="text-base text-gray-700 leading-relaxed" style="font-size: 16px; font-weight: 400; font-family: Poppins, sans-serif; color: rgb(55, 65, 81); line-height: 26px; text-align: start; margin: 0px; padding: 0px; border-radius: 0px; border: 0px solid rgb(229, 231, 235); background-color: rgba(0, 0, 0, 0); opacity: 1; box-shadow: none; text-shadow: none; text-decoration: none solid rgb(55, 65, 81); text-transform: none; letter-spacing: normal; word-spacing: 0px; text-overflow: clip; white-space: normal; word-break: normal; overflow: visible;"><div class="tiptap-text-editor w-full" style="line-height: inherit; font-size: inherit; font-weight: inherit; font-family: inherit; color: inherit; text-align: inherit;"><div contenteditable="true" data-placeholder="Enter text..." translate="no" class="tiptap ProseMirror outline-none focus:outline-none transition-all duration-200" tabindex="0"><p>Heatwaves are becoming more frequent and intense, posing significant risks to human health and agriculture.</p></div></div></div></div></div></div><div class="flex items-start space-x-4"><div class="flex-shrink-0 w-12 h-12 bg-white rounded-lg shadow-md flex items-center justify-center"><img src="/static/icons/bold/cloud-rain-bold.png" alt="precipitation changes icon" class="w-6 h-6 object-contain text-gray-700" data-editable-processed="true" data-editable-id="2-icon-bulletPoints[2].icon-3" style="cursor: pointer; transition: opacity 0.2s, transform 0.2s;"></div><div class="flex-1"><div class="text-xl font-semibold text-gray-900 mb-2" style="font-size: 20px; font-weight: 600; font-family: Poppins, sans-serif; color: rgb(17, 24, 39); line-height: 28px; text-align: start; margin: 0px 0px 8px; padding: 0px; border-radius: 0px; border: 0px solid rgb(229, 231, 235); background-color: rgba(0, 0, 0, 0); opacity: 1; box-shadow: none; text-shadow: none; text-decoration: none solid rgb(17, 24, 39); text-transform: none; letter-spacing: normal; word-spacing: 0px; text-overflow: clip; white-space: normal; word-break: normal; overflow: visible;"><div class="tiptap-text-editor w-full" style="line-height: inherit; font-size: inherit; font-weight: inherit; font-family: inherit; color: inherit; text-align: inherit;"><div contenteditable="true" data-placeholder="Enter text..." translate="no" class="tiptap ProseMirror outline-none focus:outline-none transition-all duration-200" tabindex="0"><p>Changes in Precipitation</p></div></div></div><div class="w-12 h-0.5 bg-purple-600 mb-3"></div><div class="text-base text-gray-700 leading-relaxed" style="font-size: 16px; font-weight: 400; font-family: Poppins, sans-serif; color: rgb(55, 65, 81); line-height: 26px; text-align: start; margin: 0px; padding: 0px; border-radius: 0px; border: 0px solid rgb(229, 231, 235); background-color: rgba(0, 0, 0, 0); opacity: 1; box-shadow: none; text-shadow: none; text-decoration: none solid rgb(55, 65, 81); text-transform: none; letter-spacing: normal; word-spacing: 0px; text-overflow: clip; white-space: normal; word-break: normal; overflow: visible;"><div class="tiptap-text-editor w-full" style="line-height: inherit; font-size: inherit; font-weight: inherit; font-family: inherit; color: inherit; text-align: inherit;"><div contenteditable="true" data-placeholder="Enter text..." translate="no" class="tiptap ProseMirror outline-none focus:outline-none transition-all duration-200" tabindex="0"><p>Altered precipitation patterns lead to increased droughts in some regions and severe flooding in others, affecting water resources.</p></div></div></div></div></div></div></div></div></div></div></div>
Output:
const ImageSchema = z.object({
    __image_url__: z.url().meta({
        description: "URL to image",
    }),
    __image_prompt__: z.string().meta({
        description: "Prompt used to generate the image. Max 30 words",
    }).min(10).max(50),
})

const IconSchema = z.object({
    __icon_url__: z.string().meta({
        description: "URL to icon",
    }),
    __icon_query__: z.string().meta({
        description: "Query used to search the icon. Max 3 words",
    }).min(5).max(20),
})
const layoutId = "bullet-with-icons-slide"
const layoutName = "Bullet with Icons"
const layoutDescription = "A bullets style slide with main content, supporting image, and bullet points with icons and descriptions."

const Schema = z.object({
    title: z.string().min(3).max(40).default("Problem").meta({
        description: "Main title of the slide. Max 5 words",
    }),
    description: z.string().max(150).default("Businesses face challenges with outdated technology and rising costs, limiting efficiency and growth in competitive markets.").meta({
        description: "Main description text explaining the problem or topic. Max 30 words",
    }), 
    image: ImageSchema.default({
        __image_url__: 'https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80',
        __image_prompt__: "Business people analyzing documents and charts in office"
    }).meta({
        description: "Supporting image for the slide. Max 30 words",
    }),
    bulletPoints: z.array(z.object({
        title: z.string().min(2).max(80).meta({
            description: "Bullet point title. Max 4 words",
        }),
        description: z.string().min(10).max(150).meta({
            description: "Bullet point description. Max 15 words",
        }),
        icon: IconSchema,
    })).min(1).max(3).default([
        {
            title: "Inefficiency",
            description: "Businesses struggle to find digital tools that meet their needs, causing operational slowdowns.",
            icon: {
                __icon_url__: "/static/icons/placeholder.png",
                __icon_query__: "warning alert inefficiency"
            }
        },
        {
            title: "High Costs",
            description: "Outdated systems increase expenses, while small businesses struggle to expand their market reach.",
            icon: {
                __icon_url__: "/static/icons/placeholder.png",
                __icon_query__: "trending up costs chart"
            }
        }
    ]).meta({
        description: "List of bullet points with icons and descriptions. Max 3 points",
    })
})

type BulletWithIconsSlideData = z.infer<typeof Schema>

interface BulletWithIconsSlideLayoutProps {
    data?: Partial<BulletWithIconsSlideData>
}

const dynamicSlideLayout: React.FC<BulletWithIconsSlideLayoutProps> = ({ data: slideData }) => {
    const bulletPoints = slideData?.bulletPoints || []

    return (
        <>
            <div 
                className="w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video bg-gradient-to-br from-gray-50 to-white relative z-20 mx-auto overflow-hidden"
                style={{
                    fontFamily: "Poppins, sans-serif"
                }}
            >


                {/* Main Content */}
                <div className="flex flex-col h-full px-8 sm:px-12 lg:px-20 pt-8 pb-8">
                    {/* Title Section - Full Width */}
                    <div className="mb-8">
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900">
                            {slideData?.title || "Problem"}
                        </h1>
                    </div>

                    {/* Content Container */}
                    <div className="flex flex-1">
                        {/* Left Section - Image with Grid Pattern */}
                        <div className="flex-1 relative">
                        {/* Grid Pattern Background */}
                        <div className="absolute top-0 left-0 w-full h-full">
                            <svg className="w-full h-full opacity-30" viewBox="0 0 200 200">
                                <defs>
                                    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                                        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#8b5cf6" strokeWidth="0.5"/>
                                    </pattern>
                                </defs>
                                <rect width="100%" height="100%" fill="url(#grid)" />
                            </svg>
                        </div>
                        
                        {/* Image Container */}
                        <div className="relative z-10 h-full flex items-center justify-center p-4">
                            <div className="w-full max-w-md h-80 rounded-2xl overflow-hidden shadow-lg">
                                <img
                                    src={slideData?.image?.__image_url__ || ""}
                                    alt={slideData?.image?.__image_prompt__ || slideData?.title || ""}
                                    className="w-full h-full object-cover"
                                />
                            </div>
                        </div>

                        {/* Decorative Sparkle */}
                        <div className="absolute top-20 right-8 text-purple-600">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 0l3.09 6.26L22 9l-6.91 2.74L12 18l-3.09-6.26L2 9l6.91-2.74L12 0z"/>
                            </svg>
                        </div>
                    </div>

                        {/* Right Section - Content */}
                        <div className="flex-1 flex flex-col justify-center pl-8 lg:pl-16">
                            {/* Description */}
                            <p className="text-lg text-gray-700 leading-relaxed mb-8">
                                {slideData?.description || "Businesses face challenges with outdated technology and rising costs, limiting efficiency and growth in competitive markets."}
                            </p>

                        {/* Bullet Points */}
                        <div className="space-y-6">
                            {bulletPoints.map((bullet, index) => (
                                <div key={index} className="flex items-start space-x-4">
                                    {/* Icon */}
                                    <div className="flex-shrink-0 w-12 h-12 bg-white rounded-lg shadow-md flex items-center justify-center">
                                        <img 
                                            src={bullet.icon.__icon_url__} 
                                            alt={bullet.icon.__icon_query__}
                                            className="w-6 h-6 object-contain text-gray-700"
                                        />
                                    </div>
                                    
                                    {/* Content */}
                                    <div className="flex-1">
                                        <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                            {bullet.title}
                                        </h3>   
                                        <div className="w-12 h-0.5 bg-purple-600 mb-3"></div>
                                        <p className="text-base text-gray-700 leading-relaxed">
                                            {bullet.description}
                                        </p>
                                    </div>
                                </div>
                            ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}

- 输出仅限代码且别无其它内容。（不要 json、不要 markdown、不要文本、不要解释）
"""


HTML_EDIT_SYSTEM_PROMPT = """
你需要根据给定的指示说明和草图，对提供的 HTML 进行编辑。你将获得当前界面的代码（其尺寸为演示文稿大小），以及该界面的可视化图像。此外，你还会获得另一张带有 UI 变化指示的草图图像。你需要根据图像中的修改标记和文本提示，返回修改后的 HTML（包含 Tailwind 样式）。

在进行修改前，请认真思考设计，确保：
- 仅修改被标注为需要更改的部分；
- 未被标注的部分保持不变；
- 生成的新内容应保持与当前设计风格一致；
- 如果未提供草图图像，则仅根据文本提示进行编辑；
- 无论如何都要确保演示文稿的尺寸不发生变化；
- 最终只输出修改后的 HTML 与 Tailwind 代码，不要包含任何额外文字或说明。
"""
