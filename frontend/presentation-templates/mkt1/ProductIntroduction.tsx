import React from 'react'
import * as z from "zod";
import { ImageSchema } from '@/presentation-templates/defaultSchemes';

export const layoutId = 'mkt1-product-introduction'
export const layoutName = 'Product Introduction'
export const layoutDescription = 'Marketing slide with hero image, product title, tagline, and description.'

const productIntroductionSchema = z.object({
    title: z.string().min(3).max(40).default('产品介绍').meta({
        description: "Main title of the slide",
    }),
    tagline: z.string().min(5).max(80).default('赋能增长的现代化数字化解决方案').meta({
        description: "Short tagline or positioning statement",
    }),
    description: z.string().min(10).max(180).default('我们的产品帮助企业实现数据驱动与自动化，通过模块化能力快速集成现有系统，提升效率与协作体验，适用于从初创到大型组织的不同阶段。').meta({
        description: "Main description text content",
    }),
    image: ImageSchema.default({
        __image_url__: 'https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80',
        __image_prompt__: 'Marketing product introduction hero image with team collaboration'
    }).meta({
        description: "Hero/supporting image for the slide",
    })
})

export const Schema = productIntroductionSchema

export type ProductIntroductionData = z.infer<typeof productIntroductionSchema>

interface ProductIntroductionProps {
    data?: Partial<ProductIntroductionData>
}

const ProductIntroduction: React.FC<ProductIntroductionProps> = ({ data: slideData }) => {


    return (
        <>
            {/* Import Google Fonts */}
            <link
                href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"
                rel="stylesheet"
            />

            <div
                className="w-full rounded-sm max-w-[720px] shadow-lg max-h-[1280px] aspect-[9/16] bg-white relative z-20 mx-auto overflow-hidden"
                style={{
                    fontFamily: 'Poppins, sans-serif'
                }}
            >


                {/* Main Content */}
                <div className="relative z-10 flex flex-col h-full px-6 sm:px-8 lg:px-12 py-6">
                    {/* Top Section - Image */}
                    <div className="flex-1 flex items-center justify-center pb-6">
                        <div className="w-full max-w-sm h-64 rounded-2xl overflow-hidden shadow-lg">
                            <img
                                src={slideData?.image?.__image_url__ || ''}
                                alt={slideData?.image?.__image_prompt__ || slideData?.title || ''}
                                className="w-full h-full object-cover"
                            />
                        </div>
                    </div>

                    {/* Bottom Section - Content */}
                    <div className="flex-1 flex flex-col justify-center space-y-4">
                        {/* Title */}
                        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 leading-tight text-center">
                            {slideData?.title || '产品介绍'}
                        </h1>

                        {/* Tagline */}
                        <p className="text-sm sm:text-base text-purple-700 font-medium text-center">
                            {slideData?.tagline || '赋能增长的现代化数字化解决方案'}
                        </p>

                        {/* Purple accent line */}
                        <div className="w-16 h-1 bg-purple-600 mx-auto"></div>

                        {/* Description */}
                        <p className="text-xs sm:text-sm text-gray-700 leading-relaxed text-center">
                            {slideData?.description || '我们的产品帮助企业实现数据驱动与自动化，通过模块化能力快速集成现有系统，提升效率与协作体验，适用于从初创到大型组织的不同阶段。'}
                        </p>


                    </div>
                </div>
            </div>
        </>
    )
}

export default ProductIntroduction 

