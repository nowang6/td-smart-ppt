import React, { useState, useEffect } from 'react';


const LoadingState = () => {
    const [currentTipIndex, setCurrentTipIndex] = useState(0);
    const tips = [
        "用AI制作演示文稿 ✨",
        "分析内容以制作完美的幻灯片 📊",
        "整理信息以获得最大影响力 🎯",
        "添加视觉元素 🎨",
        "快完成了！正在进行最后的润色 ⚡️"
    ];

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentTipIndex((prev) => (prev + 1) % tips.length);
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 mx-auto w-[500px] flex flex-col items-center justify-center p-8">
            <div className="w-full bg-white rounded-xl p-[2px] ">
                <div className="bg-white rounded-xl p-6 w-full">
                    <div className="flex items-center justify-center space-x-4 ">

                        <h2 className="text-2xl font-semibold text-gray-800">正在生成演示文稿</h2>
                    </div>
                    <div className="w-full max-w-md bg-white/80 backdrop-blur-sm rounded-xl shadow-sm p-6 mb-4">
                        <div className="min-h-[120px] flex items-center justify-center">
                            <p className="text-gray-700 text-lg text-center">
                                {tips[currentTipIndex]}
                            </p>
                        </div>
                    </div>

                    <div className="w-full max-w-md">
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div className="h-full bg-[#5141e5] rounded-full animate-progress" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoadingState; 