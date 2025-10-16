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

const layoutId = "specific-implementation-plan-slide"
const layoutName = "Specific Implementation Plan"
const layoutDescription = "A slide with a title, footer note, and main content area for descriptions and diagrams."

const Schema = z.object({
    title: z.string().min(2).max(20).default("具体实现方案").meta({
        description: "Title of the slide. Max 3 words"
    }),
    note: z.string().min(10).max(30).default("本页由对应模块开发人员填写").meta({
        description: "Footer note. Max 5 words"
    }),
    description: z.string().min(10).max(300).default("描述该特性的具体实现方案，流程图、框图、架构图等，由对应模块开发分别完成").meta({
        description: "Main description text explaining the implementation plan. Max 50 words"
    }),
    image: ImageSchema.default({
        __image_url__: 'https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80',
        __image_prompt__: '会议室中的商业团队正在讨论产品功能和解决方案'
    }).meta({
        description: "幻灯片的支持图片",
    }),
    date: z.string().min(8).max(11).default("09/12/2025").meta({
        description: "Date in the format MM/DD/YYYY. Max 11 characters"
    }),
    slideNumber: z.string().min(1).max(2).default("8").meta({
        description: "Slide number. Max 2 characters"
    })
})

type DynamicSlideLayoutData = z.infer<typeof Schema>

const dynamicSlideLayout: React.FC<{ data?: Partial<DynamicSlideLayoutData> }> = ({ data: slideData }) => {
    const today = new Date().toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).replace(/\//g, '/')
    return (
        <div className="relative w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video bg-white relative z-20 mx-auto overflow-hidden">
            <div className="bg-blue-800 text-white p-4 text-4xl font-semibold font-['Microsoft YaHei'] relative">
                {slideData?.title || "具体实现方案"}
                <img src="/td-tech.png" alt="TD Tech Logo" className="absolute top-4 right-4 h-16 w-auto" />
            </div>
            <div className="flex justify-end p-4">
                <div className="bg-blue-200 text-blue-800 p-2 rounded">{slideData?.note || "本页由对应模块开发人员填写"}</div>
            </div>
            <div className="p-8 flex h-full">
                {/* Left Section - Content */}
                <div className="flex-1 pr-8">
                    <div className="text-xl font-['Microsoft YaHei']">{slideData?.description || "描述该特性的具体实现方案，流程图、框图、架构图等，由对应模块开发分别完成"}</div>
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
            <div className="absolute bottom-0 left-0 text-gray-500 p-4">{slideData?.date || today}</div>
            <div className="absolute bottom-0 right-0 text-gray-500 p-4">{slideData?.slideNumber || "8"}</div>
        </div>
    )
}

export default dynamicSlideLayout
export { layoutId, layoutName, layoutDescription, Schema }
