import React from 'react'
import * as z from "zod";

const ImageSchema = z.object({
    __image_url__: z.string().url().meta({ description: "URL to image" }),
    __image_prompt__: z.string().meta({ description: "Prompt used to generate the image. Max 30 words" }).min(10).max(50),
})

export const layoutId = "mkt1-product-detail"
export const layoutName = "Market1 Product Detail"
export const layoutDescription = "一个包含标题、解决方案卡片、产品标题、规格表和二维码及联系方式的幻灯片布局。"

const DEFAULT_IMAGE = "https://images.pexels.com/photos/31527637/pexels-photo-31527637.jpeg"
const defaultSolutions = [
    { image: { __image_url__: DEFAULT_IMAGE, __image_prompt__: "Mine communication equipment in underground setting" }, title: "矿务通", description: ["防爆电池改造、电池防伪、电池保护", "适配矿山井下专网，支持高清音视频通话", "支持矿鸿软总线，多设备协同管理、卡片化呈现"] },
    { image: { __image_url__: DEFAULT_IMAGE, __image_prompt__: "Quantum encryption communication device" }, title: "量子密话", description: ["量子加密，一话一密，端到端加密", "原生拨号盘定制，一键拨打VoLTE高清通话", "来电明密识别，显性状态提示"] },
    { image: { __image_url__: DEFAULT_IMAGE, __image_prompt__: "Professional walkie talkie communication system" }, title: "和对讲", description: ["专业对讲，音量键长按发起频道沟通", "调度平台适配，保持终端数据长连接", "应用预置，和对讲APP预置/保活/卸载"] },
    { image: { __image_url__: DEFAULT_IMAGE, __image_prompt__: "Government security communication device" }, title: "政企通", description: ["应用安全隔离", "国密算法，端到端加密", "MDM设备安全管控", "防信息海外泄露"] }
]

const defaultSpecs = [
    { label: "操作系统", value: "HarmonyOS 4.3" },
    { label: "双卡", value: "双卡双待双通" },
    { label: "屏幕", value: "屏幕尺寸: 6.9英寸 分辨率: FHD+ 2832×1316像素 屏幕像素密度: 454 PPI\nOLED; 支持1-120Hz LTPO自适应刷新率, 1440Hz高帧PWM调光, 300Hz触控采样率 第二代昆仑玻璃" },
    { label: "传感器", value: "3D人脸识别, 环境光传感器, 红外传感器, 指纹传感器, 霍尔传感器, 陀螺仪, 指南针, NFC, 气压计, 接近光传感器\n重力传感器, 姿态感应器, Camera激光对焦传感器, 色温传感器" },
    { label: "存储", value: "运行内存 (RAM): 12GB RAM, 机身内存 (ROM): 256GB / 512GB" },
    { label: "WLAN", value: "2.4GHz和5GHz, 802.11 a/b/g/n/ac/ax, 2x2 MIMO, HE160, 1024 QAM, 8 Spatial-stream Sounding MU-MIMO" },
    { label: "蓝牙", value: "Bluetooth 5.2, 支持低功耗蓝牙, 支持SBC、AAC, 支持LDAC和L2HC高清音频" },
    { label: "定位", value: "支持GPS (L1+L5双频) /AGPS/GLONASS/北斗 (B1I+B1C+B2a+B2b四频) /GALILEO (E1+E5a+E5b三频)\nQZSS (L1+L5双频) /NavIC" },
    { label: "电池容量", value: "5500mAh (典型值)" },
    { label: "机身尺寸", value: "164.6mm (长) ×79.5mm (宽) ×8.2mm (厚)" },
    { label: "机身重量", value: "约221克 (含电池)" },
    { label: "防尘抗水", value: "IP68级6米抗水, IP69级抗高温高压喷水" }
]


export const Schema = z.object({
    solutions: z.array(z.object({
        image: ImageSchema,
        title: z.string().min(2).max(10).meta({ description: "Solution card title. Max 3 words" }),
        description: z.array(z.string().min(5).max(50)).min(1).max(4).meta({ description: "Solution card description lines. Max 8 words per line" }),
    })).min(1).max(4).default(defaultSolutions).meta({ description: "List of solution cards with images and descriptions. Max 4 cards" }),
    productTitle: z.string().min(5).max(30).default("HUAWEI Mate 70 Pro").meta({ description: "Product title. Max 5 words" }),
    specifications: z.array(z.object({
        label: z.string().min(2).max(20).meta({ description: "Specification label. Max 3 words" }),
        value: z.string().min(5).max(200).meta({ description: "Specification value. Max 30 words" }),
    })).min(1).max(15).default(defaultSpecs).meta({ description: "Product specifications table. Max 15 rows" }),
})

type SolutionCardsSpecsSlideData = z.infer<typeof Schema>
interface SolutionCardsSpecsSlideLayoutProps { data?: Partial<SolutionCardsSpecsSlideData> }

const FONT_STYLE = { fontFamily: "微软雅黑" }

const SolutionCard = ({ solution }: { solution: any }) => (
    <div className="flex items-center space-x-3">
        <img src={solution.image.__image_url__} alt={solution.image.__image_prompt__} className="w-12 h-12 object-cover rounded-md flex-shrink-0" />
        <div className="flex flex-col flex-1">
            <h3 className="font-bold text-sm text-gray-800" style={FONT_STYLE}>{solution.title}</h3>
            <div className="mt-1 text-xs text-gray-600" style={FONT_STYLE}>
                {solution.description.map((line: string, i: number) => <p key={i}>{line}</p>)}
            </div>
        </div>
    </div>
)

const SpecTable = ({ specifications }: { specifications: any[] }) => (
    <div className="overflow-x-auto mb-4">
        <table className="w-full border-collapse">
            <thead>
                <tr className="bg-gray-200">
                    <th className="border px-2 py-1 text-left text-xs font-medium text-gray-700" style={FONT_STYLE}>产品规格</th>
                    <th className="border px-2 py-1 text-left text-xs font-medium text-gray-700" style={FONT_STYLE}></th>
                </tr>
            </thead>
            <tbody>
                {specifications.map((spec, i) => (
                    <tr key={i} className="border-t">
                        <td className="px-2 py-1 text-xs font-medium text-gray-700" style={FONT_STYLE}>{spec.label}</td>
                        <td className="px-2 py-1 text-xs text-gray-600" style={FONT_STYLE}>{spec.value}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
)

const dynamicSlideLayout: React.FC<SolutionCardsSpecsSlideLayoutProps> = ({ data: slideData }) => {
    const solutions = slideData?.solutions || []
    const specifications = slideData?.specifications || []

    return (
        <div className="relative w-full rounded-sm max-w-[720px] shadow-lg max-h-[960px] aspect-[3/4] bg-white z-20 mx-auto overflow-hidden">
            <div className="flex flex-col h-full p-4">
                <div className="grid grid-cols-2 gap-4 mb-6">
                    {solutions.map((solution, index) => <SolutionCard key={index} solution={solution} />)}
                </div>
                <div className="text-xl font-bold mb-4 text-gray-800" style={FONT_STYLE}>{slideData?.productTitle || "HUAWEI Mate 70 Pro"}</div>
                <SpecTable specifications={specifications} />
                <div className="flex justify-center">
                    <img src="/contact_detail.png" alt="Contact Details" className="max-w-full h-auto object-contain" />
                </div>
            </div>
        </div>
    )
}

export default dynamicSlideLayout