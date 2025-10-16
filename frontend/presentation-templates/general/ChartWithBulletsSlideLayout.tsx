import React from 'react'
import * as z from "zod";
import { IconSchema } from '@/presentation-templates/defaultSchemes';
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from "@/components/ui/chart";
import { BarChart, Bar, LineChart, Line, PieChart, Pie, AreaChart, Area, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Cell, ResponsiveContainer } from "recharts";

export const layoutId = 'chart-with-bullets-slide'
export const layoutName = '图表与要点'
export const layoutDescription = '一个包含标题、描述、左侧图表和右侧彩色要点框的幻灯片布局。仅在有数据时选择。'

const barPieLineAreaChartDataSchema = z.object({
    type: z.union([z.literal('bar'), z.literal('pie'), z.literal('line'), z.literal('area')]),
    data: z.array(z.object({
        name: z.string().meta({ description: "数据点名称" }),
        value: z.number().meta({ description: "数据点值" }),
    })).min(2).max(5)
})

const scatterChartDataSchema = z.object({
    type: z.literal('scatter'),
    data: z.array(z.object({
        x: z.number().meta({ description: "X坐标" }),
        y: z.number().meta({ description: "Y坐标" }),
    })).min(2).max(20)
})

const chartWithBulletsSlideSchema = z.object({
    title: z.string().min(3).max(40).default('市场规模').meta({
        description: "幻灯片主标题",
    }),
    description: z.string().min(10).max(150).default('企业面临过时技术和成本上升的挑战，限制了在竞争市场中的效率和增长。').meta({
        description: "标题下方的描述文本",
    }),
    chartData: z.union([barPieLineAreaChartDataSchema, scatterChartDataSchema]).default({
        type: 'scatter',
        data: [
            { x: 5, y: 5 },
            { x: 10, y: 12 },
            { x: 15, y: 18 },
            { x: 20, y: 23 },
            { x: 25, y: 26 },
        ]
    }
    ),
    color: z.string().default('#3b82f6').meta({
        description: "图表元素的主色",
    }),
    showLegend: z.boolean().default(false).meta({
        description: "是否显示图表图例",
    }),
    showTooltip: z.boolean().default(true).meta({
        description: "是否显示图表工具提示",
    }),
    bulletPoints: z.array(z.object({
        title: z.string().min(2).max(80).meta({
            description: "要点标题",
        }),
        description: z.string().min(10).max(150).meta({
            description: "要点描述",
        }),
        icon: IconSchema,
    })).min(1).max(3).default([
        {
            title: '总可寻址市场',
            description: '公司可以使用TAM来规划未来的扩张和投资。',
            icon: {
                __icon_url__: '/static/icons/placeholder.png',
                __icon_query__: 'target market scope'
            }
        },
        {
            title: '可服务可用市场',
            description: '表示更可衡量的市场细分，用于销售努力。',
            icon: {
                __icon_url__: '/static/icons/placeholder.png',
                __icon_query__: 'pie chart analysis'
            }
        },
        {
            title: '可服务可获得市场',
            description: '帮助公司根据市场规划发展战略。',
            icon: {
                __icon_url__: '/static/icons/placeholder.png',
                __icon_query__: 'trending up growth'
            }
        }
    ]).meta({
        description: "带彩色框和图标的要点列表",
    })
})

export const Schema = chartWithBulletsSlideSchema


export type ChartWithBulletsSlideData = z.infer<typeof chartWithBulletsSlideSchema>

interface ChartWithBulletsSlideLayoutProps {
    data?: Partial<ChartWithBulletsSlideData>
}

const chartConfig = {
    value: {
        label: "值",
    },
    name: {
        label: "名称",
    },
};

const CHART_COLORS = [
    '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
    '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
];

const BULLET_COLORS = [
    '#7F31E9', '#2C78DA', '#F58AAB', '#10b981', '#f59e0b',
    '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
];

const ChartWithBulletsSlideLayout: React.FC<ChartWithBulletsSlideLayoutProps> = ({ data: slideData }) => {
    const chartData = slideData?.chartData?.data || [];
    const chartType = slideData?.chartData?.type;
    const color = slideData?.color || '#3b82f6';
    const xAxis = chartType === 'scatter' ? 'x' : 'name';
    const yAxis = chartType === 'scatter' ? 'y' : 'value';
    const showLegend = slideData?.showLegend || false;
    const showTooltip = slideData?.showTooltip || true;
    const bulletPoints = slideData?.bulletPoints || []

    const renderChart = () => {
        const commonProps = {
            data: chartData,
            margin: { top: 20, right: 30, left: 40, bottom: 60 },
        };

        switch (chartType) {
            case 'bar':
                return (
                    <BarChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey={xAxis} />
                        <YAxis />
                        {showTooltip && <ChartTooltip content={<ChartTooltipContent />} />}
                        {showLegend && <ChartLegend content={<ChartLegendContent />} />}
                        <Bar dataKey={yAxis} fill={color} radius={[4, 4, 0, 0]} />
                    </BarChart>
                );

            case 'line':
                return (
                    <LineChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey={xAxis} />
                        <YAxis />
                        {showTooltip && <ChartTooltip content={<ChartTooltipContent />} />}
                        {showLegend && <ChartLegend content={<ChartLegendContent />} />}
                        <Line
                            type="monotone"
                            dataKey={yAxis}
                            stroke={color}
                            strokeWidth={3}
                            dot={{ fill: color, strokeWidth: 2, r: 4 }}
                        />
                    </LineChart>
                );

            case 'area':
                return (
                    <AreaChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey={xAxis} />
                        <YAxis />
                        {showTooltip && <ChartTooltip content={<ChartTooltipContent />} />}
                        {showLegend && <ChartLegend content={<ChartLegendContent />} />}
                        <Area
                            type="monotone"
                            dataKey={yAxis}
                            stroke={color}
                            fill={color}
                            fillOpacity={0.6}
                        />
                    </AreaChart>
                );

            case 'pie':
                return (
                    <PieChart margin={{ top: 20, right: 30, left: 40, bottom: 60 }}>
                        {showTooltip && <ChartTooltip content={<ChartTooltipContent />} />}
                        {showLegend && <ChartLegend content={<ChartLegendContent />} />}
                        <Pie
                            data={chartData}
                            cx="50%"
                            cy="40%"
                            outerRadius={70}
                            fill={color}
                            dataKey={yAxis}
                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        >
                            {chartData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                            ))}
                        </Pie>
                    </PieChart>
                );

            case 'scatter':
                return (
                    <ScatterChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey={xAxis} type="number" />
                        <YAxis dataKey={yAxis} type="number" />
                        {showTooltip && <ChartTooltip content={<ChartTooltipContent />} />}
                        {showLegend && <ChartLegend content={<ChartLegendContent />} />}
                        <Scatter dataKey="value" fill={color} />
                    </ScatterChart>
                );

            default:
                return <div>不支持的图表类型</div>;
        }
    };

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
                <div className="flex h-full px-8 sm:px-12 lg:px-20 pt-8 pb-8">
                    {/* Left Section - Title, Description, Chart */}
                    <div className="flex-1 flex flex-col pr-8">
                        {/* Title */}
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-4">
                            {slideData?.title || '市场规模'}
                        </h1>

                        {/* Description */}
                        <p className="text-base text-gray-700 leading-relaxed mb-8">
                            {slideData?.description || '企业面临过时技术和成本上升的挑战，限制了在竞争市场中的效率和增长。'}
                        </p>

                        {/* Chart Container */}
                        <div className="flex-1 bg-white rounded-lg shadow-sm border border-gray-100 p-4">
                            <ChartContainer config={chartConfig} className="h-full w-full">
                                {renderChart()}
                            </ChartContainer>
                        </div>
                    </div>

                    {/* Right Section - Bullet Point Boxes */}
                    <div className="flex-shrink-0 w-80 flex flex-col justify-center space-y-4">
                        {bulletPoints.map((bullet, index) => (
                            <div
                                key={index}
                                className="rounded-2xl p-6 text-white"
                                style={{
                                    backgroundColor: BULLET_COLORS[index % BULLET_COLORS.length]
                                }}
                            >
                                {/* Icon and Title */}
                                <div className="flex items-center space-x-3 mb-3">
                                    <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                                        <img
                                            src={bullet.icon.__icon_url__}
                                            alt={bullet.icon.__icon_query__}
                                            className="w-5 h-5 object-contain brightness-0 invert"
                                        />
                                    </div>
                                    <h3 className="text-lg font-semibold">
                                        {bullet.title}
                                    </h3>
                                </div>

                                {/* Description */}
                                <p className="text-sm leading-relaxed opacity-90">
                                    {bullet.description}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </>
    )
}

export default ChartWithBulletsSlideLayout 