import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { sanitizeFilename } from "@/app/(presentation-generator)/utils/others";

export async function GET(
  request: NextRequest,
  { params }: { params: { filename: string[] } }
) {
  try {
    // Join the filename array to get the full filename
    const filename = params.filename.join('/');
    const sanitizedFilename = sanitizeFilename(filename);
    
    // Construct the file path
    const filePath = path.join(process.cwd(), "app_data", "exports", sanitizedFilename);
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      return new NextResponse("File not found", { status: 404 });
    }
    
    // Read the file
    const fileBuffer = fs.readFileSync(filePath);
    
    // Determine content type based on file extension
    const ext = path.extname(sanitizedFilename).toLowerCase();
    let contentType = "application/octet-stream";
    
    switch (ext) {
      case ".pptx":
        contentType = "application/vnd.openxmlformats-officedocument.presentationml.presentation";
        break;
      case ".pdf":
        contentType = "application/pdf";
        break;
      case ".jpg":
      case ".jpeg":
        contentType = "image/jpeg";
        break;
      case ".png":
        contentType = "image/png";
        break;
      case ".gif":
        contentType = "image/gif";
        break;
      case ".txt":
        contentType = "text/plain";
        break;
    }
    
    // Return the file with appropriate headers
    return new NextResponse(fileBuffer, {
      status: 200,
      headers: {
        "Content-Type": contentType,
        "Content-Disposition": `attachment; filename="${path.basename(sanitizedFilename)}"`,
        "Cache-Control": "public, max-age=3600", // Cache for 1 hour
      },
    });
  } catch (error) {
    console.error("Error serving file:", error);
    return new NextResponse("Internal Server Error", { status: 500 });
  }
}
