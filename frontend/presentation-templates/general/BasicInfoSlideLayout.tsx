import React from 'react'
import * as z from "zod";
import { ImageSchema } from '@/presentation-templates/defaultSchemes';

export const layoutId = 'basic-info-slide'
export const layoutName = '基本信息'
export const layoutDescription = '一个简洁的幻灯片布局，包含标题、描述文本和支持图片。'

const basicInfoSlideSchema = z.object({
    title: z.string().min(3).max(40).default('产品概览').meta({
        description: "幻灯片的主标题",
    }),
    description: z.string().min(10).max(150).default('我们的产品提供了可定制的仪表盘，用于实时报告和数据驱动决策。它与第三方工具集成，以增强运营并随着业务增长而扩大规模，从而提高效率。').meta({
        description: "主要内容描述文本",
    }),
    image: ImageSchema.default({
        __image_url__: 'https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80',
        __image_prompt__: '会议室中的商业团队正在讨论产品功能和解决方案'
    }).meta({
        description: "幻灯片的支持图片",
    })
})

export const Schema = basicInfoSlideSchema

export type BasicInfoSlideData = z.infer<typeof basicInfoSlideSchema>

interface BasicInfoSlideLayoutProps {
    data?: Partial<BasicInfoSlideData>
}

const BasicInfoSlideLayout: React.FC<BasicInfoSlideLayoutProps> = ({ data: slideData }) => {


    return (
        <>
            {/* Import Google Fonts */}
            <link
                href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"
                rel="stylesheet"
            />

            <div
                className="w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video bg-white relative z-20 mx-auto overflow-hidden"
                style={{
                    fontFamily: 'Poppins, sans-serif'
                }}
            >


                {/* Main Content */}
                <div className="relative z-10 flex h-full px-8 sm:px-12 lg:px-20 pb-8">
                    {/* Left Section - Image */}
                    <div className="flex-1 flex items-center justify-center pr-8">
                        <div className="w-full max-w-lg h-80 rounded-2xl overflow-hidden shadow-lg">
                            <img
                                src={slideData?.image?.__image_url__ || ''}
                                alt={slideData?.image?.__image_prompt__ || slideData?.title || ''}
                                className="w-full h-full object-cover"
                            />
                        </div>
                    </div>

                    {/* Right Section - Content */}
                    <div className="flex-1 flex flex-col justify-center pl-8 space-y-6">
                        {/* Title */}
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
                            {slideData?.title || '产品介绍'}
                        </h1>

                        {/* Purple accent line */}
                        <div className="w-20 h-1 bg-purple-600"></div>

                        {/* Description */}
                        <p className="text-base sm:text-lg text-gray-700 leading-relaxed">
                            {slideData?.description || '我们的产品提供了可定制的仪表盘，用于实时报告和数据驱动决策。它与第三方工具集成，以增强运营并随着业务增长而扩大规模，从而提高效率。'}
                        </p>


                    </div>
                </div>
            </div>
        </>
    )
}

export default BasicInfoSlideLayout 