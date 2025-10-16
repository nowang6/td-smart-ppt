import React from 'react'
import { z } from 'zod'

const ImageSchema = z.object({
  __image_url__: z.url().meta({
    description: "URL to image",
  }),
  __image_prompt__: z.string().meta({
    description: "Prompt used to generate the image. Max 30 words",
  }).min(10).max(50),
})

const layoutId = "验收标准描述"
const layoutName = "验收标准描述"
const layoutDescription = "一个用于描述验收标准的简洁幻灯片布局。"

const Schema = z.object({
    title: z.string().min(1).max(10).default("验收标准").meta({
        description: "幻灯片标题。",
    }),
    subtitle: z.string().min(1).max(50).default("本页由特性 BBT 负责人填写").meta({
        description: "副标题，通常用于显示填写人信息。",
    }),
    description: z.string().min(1).max(200).default("描述验收标准").meta({
        description: "主要描述内容，解释验收标准。",
    }),
    image: ImageSchema.default({
        __image_url__: 'https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80',
        __image_prompt__: '会议室中的商业团队正在讨论产品功能和解决方案'
    }).meta({
        description: "幻灯片的支持图片",
    }),
    date: z.string().min(1).max(20).default("09/12/2025").meta({
        description: "幻灯片底部左侧的日期。",
    }),
    number: z.string().min(1).max(10).default("11").meta({
        description: "幻灯片底部右侧的页码。",
    })
})

type AcceptanceCriteriaSlideData = z.infer<typeof Schema>

export const dynamicSlideLayout: React.FC<{ data?: Partial<AcceptanceCriteriaSlideData> }> = ({ data }) => {
    const today = new Date().toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).replace(/\//g, '/')
    
    return (
        <div className="relative w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video bg-white relative z-20 mx-auto overflow-hidden">
            <div className="bg-blue-900 text-white p-4 font-['Microsoft YaHei'] text-4xl relative">
                {data?.title || "验收标准"}
                <img src="/td-tech.png" alt="TD Tech Logo" className="absolute top-4 right-4 h-16 w-auto" />
            </div>
            <div className="absolute top-4 right-4 bg-blue-200 p-2 rounded font-['Microsoft YaHei'] text-lg">
                {data?.subtitle || "本页由特性 BBT 负责人填写"}
            </div>
            <div className="m-8 flex h-full">
                {/* Left Section - Content */}
                <div className="flex-1 pr-8">
                    <div className="font-['Microsoft YaHei'] text-2xl">
                        {data?.description || "描述验收标准"}
                    </div>
                </div>
                
                {/* Right Section - Image */}
                <div className="flex-1 flex items-center justify-center pl-8">
                    <div className="w-full max-w-md h-64 rounded-2xl overflow-hidden shadow-lg">
                        <img
                            src={data?.image?.__image_url__ || ''}
                            alt={data?.image?.__image_prompt__ || data?.title || ''}
                            className="w-full h-full object-cover"
                        />
                    </div>
                </div>
            </div>
            <div className="absolute bottom-4 left-4 font-['Microsoft YaHei'] text-lg">
                {data?.date || today}
            </div>
            <div className="absolute bottom-4 right-4 font-['Microsoft YaHei'] text-lg">
                {data?.number || "11"}
            </div>
        </div>
    )
}

export default dynamicSlideLayout
export { layoutId, layoutName, layoutDescription, Schema }
