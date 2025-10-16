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

const layoutId = "feature-description-slide"
const layoutName = "FeatureDescriptionSlide"
const layoutDescription = "A slide with a title, description, bullet points, and footer."

const Schema = z.object({
    title: z.string().min(1).max(100).default("特性描述").meta({
        description: "Title of the slide. Max 20 characters",
    }),
    subtitle: z.string().min(0).max(200).default("本页由 FO 填写").meta({
        description: "Subtitle of the slide. Max 40 characters",
    }),
    descriptionText: z.string().min(10).max(500).default("描述该特性 UI 变更情况 (UCD 是否已给出)、参数配置是否需要刷新").meta({
        description: "Main description text of the slide. Max 100 characters",
    }),
    uiChange: z.string().min(0).max(100).default("UI 变更").meta({
        description: "UI change description. Max 20 characters",
    }),
    configChange: z.string().min(0).max(100).default("参数配置").meta({
        description: "Config change description. Max 20 characters",
    }),
    image: ImageSchema.default({
        __image_url__: 'https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80',
        __image_prompt__: '会议室中的商业团队正在讨论产品功能和解决方案'
    }).meta({
        description: "幻灯片的支持图片",
    }),
    date: z.string().min(0).max(20).default("09/12/2025").meta({
        description: "Footer date of the slide. Max 10 characters",
    }),
    number: z.string().min(0).max(10).default("6").meta({
        description: "Footer number of the slide. Max 5 characters",
    })
})

type FeatureDescriptionSlideData = z.infer<typeof Schema>

interface FeatureDescriptionSlideLayoutProps {
    data?: Partial<FeatureDescriptionSlideData>
}

const dynamicSlideLayout: React.FC<FeatureDescriptionSlideLayoutProps> = ({ data: slideData }) => {
    const today = new Date().toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).replace(/\//g, '/')
    
    return (
        <div className="relative w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video bg-white relative z-20 mx-auto overflow-hidden">
            <div className="bg-blue-800 text-white p-4 font-bold text-4xl font-微软雅黑 relative">
                {slideData?.title || "特性描述"}
                <img src="/td-tech.png" alt="TD Tech Logo" className="absolute top-4 right-4 h-16 w-auto" />
            </div>
            <div className="flex justify-end p-4">
                <div className="bg-blue-200 text-blue-800 p-2 rounded">
                    {slideData?.subtitle || "本页由 FO 填写"}
                </div>
            </div>
            <div className="p-4 flex h-full">
                {/* Left Section - Content */}
                <div className="flex-1 pr-8">
                    <div className="text-lg font-微软雅黑">
                        {slideData?.descriptionText || "描述该特性 UI 变更情况 (UCD 是否已给出)、参数配置是否需要刷新"}
                    </div>
                    <ul className="list-disc list-inside mt-4 text-lg font-微软雅黑">
                        <li>{slideData?.uiChange || "UI 变更"}</li>
                    </ul>
                    <ul className="list-disc list-inside mt-2 text-lg font-微软雅黑">
                        <li>{slideData?.configChange || "参数配置"}</li>
                    </ul>
                </div>
                
                {/* Right Section - Image */}
                <div className="flex-1 flex items-center justify-center pl-8">
                    <div className="w-full max-w-md h-64 rounded-2xl overflow-hidden shadow-lg">
                        <img
                            src={slideData?.image?.__image_url__ || ''}
                            alt={slideData?.image?.__image_prompt__ || slideData?.title || ''}
                            className="w-full h-full object-cover"
                        />
                    </div>
                </div>
            </div>
            <div className="absolute bottom-0 p-4 text-gray-600 text-sm font-微软雅黑">
                {slideData?.date || today}
            </div>
            <div className="absolute bottom-0 right-0 p-4 text-gray-600 text-sm font-微软雅黑">
                {slideData?.number || "6"}
            </div>
        </div>
    )
}

export default dynamicSlideLayout
export { layoutId, layoutName, layoutDescription, Schema }
