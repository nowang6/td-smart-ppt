import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { sanitizeFilename } from "@/app/(presentation-generator)/utils/others";

export async function POST(request: Request) {
  try {
    const { filePath } = await request.json();

    const sanitizedFilePath = sanitizeFilename(filePath);
    const normalizedPath = path.normalize(sanitizedFilePath);
    const resolvedPath = fs.realpathSync(path.resolve(normalizedPath));
  
    
    console.log("Reading file (dev mode - no path restrictions):", resolvedPath);
    const content = fs.readFileSync(resolvedPath, "utf-8");

    return NextResponse.json({ content });
  } catch (error) {
    console.error("Error reading file:", error);
    return NextResponse.json({ error: "Failed to read file" }, { status: 500 });
  }
}

