import React from "react";

import UploadPage from "./components/UploadPage";
import Header from "@/app/(presentation-generator)/dashboard/components/Header";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "td-smart-pp",
  description:
    "td-smart-pp",
  alternates: {
    canonical: "https://my.com",
  },
  keywords: [
    "presentation generator",
    "AI presentations"
  ],
};

const page = () => {
  return (
    <div className="relative">
      <div className="flex flex-col items-center justify-center  py-8">
        <h1 className="text-3xl font-semibold font-instrument_sans">
          创建幻灯片{" "}
        </h1>
        {/* <p className='text-sm text-gray-500'>We will generate a presentation for you</p> */}
      </div>

      <UploadPage />
    </div>
  );
};

export default page;

