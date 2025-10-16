import React from 'react'
import * as z from "zod";
import { ImageSchema } from '@/presentation-templates/defaultSchemes';

export const layoutId = 'general-intro-slide'
export const layoutName = '简介幻灯片'
export const layoutDescription = '一个简洁的幻灯片布局，包含标题、描述文本、演讲者信息和支持图像。'

const introSlideSchema = z.object({
    title: z.string().min(3).max(40).default('产品概览').meta({
        description: "幻灯片主标题",
    }),
    description: z.string().min(10).max(150).default('我们的产品提供了可定制的仪表盘，用于实时报告和数据驱动决策。它与第三方工具集成，以增强运营并随着业务增长而扩大规模，从而提高效率。').meta({
        description: "主要描述文本内容",
    }),
    presenterName: z.string().min(2).max(50).default('张三').meta({
        description: "演讲者姓名",
    }),
    presentationDate: z.string().min(2).max(50).default('2024年12月').meta({
        description: "演讲日期",
    }),
    image: ImageSchema.default({
        __image_url__: 'https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80',
        __image_prompt__: '会议室中的商务团队讨论产品功能和解决方案'
    }).meta({
        description: "幻灯片的支持图像",
    })
})

export const Schema = introSlideSchema

export type IntroSlideData = z.infer<typeof introSlideSchema>

interface IntroSlideLayoutProps {
    data?: Partial<IntroSlideData>
}

const IntroSlideLayout: React.FC<IntroSlideLayoutProps> = ({ data: slideData }) => {
    // Generate initials from presenter name
    const getInitials = (name: string) => {
        return name.split(' ').map(word => word.charAt(0).toUpperCase()).join('');
    };

    const presenterInitials = getInitials(slideData?.presenterName || '张三');
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
                            {slideData?.title || '产品概览'}
                        </h1>

                        {/* Purple accent line */}
                        <div className="w-20 h-1 bg-purple-600"></div>

                        {/* Description */}
                        <p className="text-base sm:text-lg text-gray-700 leading-relaxed">
                            {slideData?.description || '我们的产品提供了可定制的仪表盘，用于实时报告和数据驱动决策。它与第三方工具集成，以增强运营并随着业务增长而扩大规模，从而提高效率。'}
                        </p>

                        {/* Presenter Section */}
                        <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4 lg:p-6 border border-gray-200 shadow-sm">
                            <div className="flex items-center gap-4">
                                {/* Custom Initials Icon */}
                                <div className="w-10 h-10 lg:w-12 lg:h-12 bg-purple-600 rounded-full flex items-center justify-center">
                                    <span className="text-white font-bold text-sm lg:text-base">
                                        {presenterInitials}
                                    </span>
                                </div>
                                
                                {/* Presenter Info */}
                                <div className="flex flex-col">
                                    <span className="text-lg lg:text-xl font-bold text-gray-900">
                                        {slideData?.presenterName || '张三'}
                                    </span>
                                    <span className="text-sm lg:text-base text-gray-600 font-medium">
                                        {slideData?.presentationDate || '2024年12月'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}

export default IntroSlideLayout 