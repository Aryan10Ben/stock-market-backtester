"use client";

import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => (
    <div className="animate-pulse bg-gray-800 rounded-lg w-full h-full min-h-[300px]"></div>
  ),
});

export default Plot;
