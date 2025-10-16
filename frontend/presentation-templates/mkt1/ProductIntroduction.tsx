import React from 'react'
import * as z from "zod";

export const layoutId = "mkt1-product-introduction"
export const layoutName = "Market1 Product Introduction"
export const layoutDescription = "一个包含背景图像、logo、标题、副标题、功能亮点、产品图像和定制卡片的幻灯片布局。"


const ImageSchema = z.object({ __image_url__: z.string().url(), __image_prompt__: z.string().min(10).max(50) })
const IconSchema = z.object({ __icon_url__: z.string(), __icon_query__: z.string().min(5).max(20) })

export const Schema = z.object({
  backgroundImage: ImageSchema.default({ __image_url__: "https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg", __image_prompt__: "Modern smartphone product showcase background" }),
  mainTitle: z.string().min(10).max(100).default("基于HUAWEI\nMate 70 Pro定制的行业终端"),
  subtitle: z.string().min(5).max(50).default("移动安全 鼎力相助"),
  features: z.string().min(10).max(100).default("北斗卫星消息 | 红枫原色影像 | 超可靠玄武架构"),
  phoneImages: z.array(ImageSchema).min(2).max(2).default([
    { __image_url__: "https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg", __image_prompt__: "Smartphone back view" },
    { __image_url__: "https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg", __image_prompt__: "Smartphone front view" }
  ]),
  customizationTitle: z.string().min(2).max(20).default("定制能力"),
  customizationCards: z.array(z.object({ title: z.string().min(2).max(20), description: z.string().min(10).max(100), icon: IconSchema })).min(1).max(6).default([
    { title: "行业鸿蒙", description: "国产操作系统行业定制\n分布式可信互联，应用跨设备流转", icon: { __icon_url__: "/static/icons/clock.svg", __icon_query__: "clock time" }},
    { title: "安全架构", description: "系统级防root防刷机，安全启动\n系统加密，应用安全隔离", icon: { __icon_url__: "/static/icons/lock.svg", __icon_query__: "lock security" }},
    { title: "设备管控", description: "适配行业MDM管控平台\n外设接口管控，一键清除设备数据", icon: { __icon_url__: "/static/icons/settings.svg", __icon_query__: "settings control" }},
    { title: "内容定制", description: "应用预置/保活/自启动/防卸载\n开机动画定制，产品包装定制", icon: { __icon_url__: "/static/icons/file.svg", __icon_query__: "file document" }},
    { title: "定位增强", description: "单北斗定位\n模糊定位", icon: { __icon_url__: "/static/icons/location.svg", __icon_query__: "location pin" }},
    { title: "场景化方案", description: "全局水印，企业黄页\n物理按键定制", icon: { __icon_url__: "/static/icons/layout.svg", __icon_query__: "layout grid" }}
  ]),
})

type HeroProductShowcaseSlideData = z.infer<typeof Schema>

interface HeroProductShowcaseSlideLayoutProps { data?: Partial<HeroProductShowcaseSlideData> }

const dynamicSlideLayout: React.FC<HeroProductShowcaseSlideLayoutProps> = ({ data: slideData }) => {
  const data = {
    backgroundImage: slideData?.backgroundImage || { __image_url__: "https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg", __image_prompt__: "Background" },
    logo: "/Logo.png", // DO NOT CHANGE: This logo path is fixed and must remain unchanged
    mainTitle: slideData?.mainTitle || "基于HUAWEI\nMate 70 Pro定制的行业终端",
    subtitle: slideData?.subtitle || "移动安全 鼎力相助",
    features: slideData?.features || "北斗卫星消息 | 红枫原色影像 | 超可靠玄武架构",
    phoneImages: slideData?.phoneImages || [],
    customizationTitle: slideData?.customizationTitle || "定制能力",
    customizationCards: slideData?.customizationCards || []
  }

  return (
    <div className="relative w-full rounded-sm max-w-[720px] shadow-lg max-h-[960px] aspect-[3/4] bg-white z-20 mx-auto overflow-hidden flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0 pt-4 pb-2 px-4"><img src={data.logo} alt="Logo" className="h-10 w-auto" /></div>
      
      {/* Title */}
      <div className="flex-shrink-0 px-4 py-3 text-center">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-800 leading-tight" style={{fontFamily: "微软雅黑"}}>{data.mainTitle}</h1>
      </div>
      
      {/* Subtitle */}
      <div className="flex-shrink-0 px-4 py-2 text-center">
        <div className="inline-block bg-white bg-opacity-90 px-6 py-2 rounded-full border border-gray-300 text-gray-700 font-medium text-lg" style={{fontFamily: "微软雅黑"}}>{data.subtitle}</div>
      </div>
      
      {/* Features */}
      <div className="flex-shrink-0 px-4 py-2 text-center text-gray-600 text-xs" style={{fontFamily: "微软雅黑"}}>{data.features}</div>
      
      {/* Product Images */}
      <div className="flex-shrink-0 px-4 py-4 flex justify-center space-x-3">
        {data.phoneImages.map((img, idx) => <img key={idx} src={img.__image_url__} alt={img.__image_prompt__} className="w-24 h-48 object-contain" />)}
      </div>
      
      {/* Customization Title */}
      <div className="flex-shrink-0 px-4 py-3 text-center">
        <div className="flex items-center justify-center space-x-2">
          <div className="w-1 h-6 bg-red-500"></div>
          <h2 className="text-xl font-bold text-gray-800" style={{fontFamily: "微软雅黑"}}>{data.customizationTitle}</h2>
          <div className="w-1 h-6 bg-red-500"></div>
        </div>
      </div>
      
      {/* Customization Cards */}
      <div className="flex-1 px-4 pb-4">
        <div className="grid grid-cols-2 gap-3 w-full max-w-sm mx-auto">
          {data.customizationCards.map((card, idx) => (
            <div key={idx} className="flex flex-col items-start space-y-2">
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-white border border-gray-300 rounded flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"></circle><path d="M12 8v4l2 2"></path>
                  </svg>
                </div>
                <div className="text-sm font-semibold text-gray-700" style={{fontFamily: "微软雅黑"}}>{card.title}</div>
              </div>
              <div className="text-xs text-gray-600 leading-tight" style={{fontFamily: "微软雅黑"}}>
                {card.description.split('\n').map((line, i) => <span key={i}>{line}{i < card.description.split('\n').length - 1 && <br />}</span>)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default dynamicSlideLayout