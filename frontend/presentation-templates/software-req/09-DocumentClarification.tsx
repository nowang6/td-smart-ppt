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

const layoutId = "document-clarification-slide"
const layoutName = "DocumentClarificationSlide"
const layoutDescription = "A slide layout for displaying document clarification details."

const Schema = z.object({
    title: z.string().min(1).max(50).default("文档澄清").meta({
        description: "Title of the slide"
    }),
    subheading: z.string().min(1).max(50).default("本页由 FO 填写").meta({
        description: "Subheading of the slide"
    }),
    description: z.string().min(1).max(200).default("和 Story 相关的文档、资料的准备情况：").meta({
        description: "Description for the slide"
    }),
    documents: z.array(z.object({
        number: z.string().min(1).max(10).default("1").meta({
            description: "Document number"
        }),
        name: z.string().min(1).max(100).default("").meta({
            description: "Document name"
        }),
        path: z.string().min(1).max(200).default("").meta({
            description: "Document path"
        })
    })).min(1).max(10).default([
        { number: "1", name: "", path: "" },
        { number: "2", name: "", path: "" },
        { number: "3", name: "", path: "" }
    ]).meta({
        description: "List of documents"
    }),
    image: ImageSchema.default({
        __image_url__: 'https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80',
        __image_prompt__: '会议室中的商业团队正在讨论产品功能和解决方案'
    }).meta({
        description: "幻灯片的支持图片",
    }),
    dateString: z.string().min(1).max(20).default("09/12/2025").meta({
        description: "Date displayed on the slide"
    }),
    slideNumber: z.string().min(1).max(10).default("9").meta({
        description: "Slide number"
    })
})

type DocumentClarificationSlideData = z.infer<typeof Schema>

interface DocumentClarificationSlideLayoutProps {
    data?: Partial<DocumentClarificationSlideData>
}

const dynamicSlideLayout: React.FC<DocumentClarificationSlideLayoutProps> = ({ data: slideData }) => {
    const today = new Date().toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).replace(/\//g, '/')
    
    return (
        <div className="relative w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video bg-white relative z-20 mx-auto overflow-hidden">
            <div className="bg-blue-800 text-white text-[56px] font-[微软雅黑] leading-[64px] p-4 relative">
                {slideData?.title || "文档澄清"}
                <img src="/td-tech.png" alt="TD Tech Logo" className="absolute top-4 right-4 h-16 w-auto" />
            </div>
            <div className="bg-blue-200 text-blue-800 text-[16px] font-[微软雅黑] leading-[24px] p-2 m-2 rounded">
                {slideData?.subheading || "本页由 FO 填写"}
            </div>
            <div className="flex h-full mt-4 ml-10 mr-10">
                {/* Left Section - Content */}
                <div className="flex-1 pr-8">
                    <div className="text-[24px] font-[微软雅黑] leading-[32px] mt-6">
                        {slideData?.description || "和 Story 相关的文档、资料的准备情况："}
                    </div>
                    <div className="bg-gray-200 rounded overflow-hidden mt-4">
                        <table className="w-full bg-white">
                            <thead>
                                <tr className="text-[16px] font-[微软雅黑] leading-[24px] text-left text-gray-800">
                                    <th className="px-4 py-2 w-1/6">序号</th>
                                    <th className="px-4 py-2 w-2/6">文档 / 资料名称</th>
                                    <th className="px-4 py-2 w-3/6">归档路径</th>
                                </tr>
                            </thead>
                            <tbody>
                                {slideData?.documents?.map((doc: any, index: number) => (
                                    <tr key={index} className="text-[16px] font-[微软雅黑] leading-[24px] text-left text-gray-800">
                                        <td className="px-4 py-2 w-1/6">{doc?.number || (index + 1).toString()}</td>
                                        <td className="px-4 py-2 w-2/6">{doc?.name || ""}</td>
                                        <td className="px-4 py-2 w-3/6">{doc?.path || ""}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
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
            <div className="text-gray-600 text-[14px] font-[微软雅黑] leading-[20px] absolute bottom-10 left-10">
                {slideData?.dateString || today}
            </div>
            <div className="text-gray-600 text-[14px] font-[微软雅黑] leading-[20px] absolute bottom-10 right-10">
                {slideData?.slideNumber || "9"}
            </div>
        </div>
    )
}


export default dynamicSlideLayout
export { layoutId, layoutName, layoutDescription, Schema }