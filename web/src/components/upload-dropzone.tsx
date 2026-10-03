"use client";
import React, { useCallback, useState } from "react";
import { UploadCloud } from "lucide-react";

export function UploadDropzone({ onUpload }: { onUpload: (file: File) => void }) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      const validTypes = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"];
      if (validTypes.includes(file.type) || file.name.endsWith(".pdf") || file.name.endsWith(".docx") || file.name.endsWith(".txt")) {
        onUpload(file);
      } else {
        alert("Invalid file type. Please upload PDF, DOCX, or TXT.");
      }
    }
  }, [onUpload]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
        isDragging ? "border-blue-500 bg-blue-500/10" : "border-gray-700 hover:border-gray-500"
      }`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <UploadCloud className="mx-auto h-12 w-12 text-gray-400 mb-4" />
      <h3 className="text-lg font-semibold text-gray-200 mb-2">Drag and drop your resume</h3>
      <p className="text-sm text-gray-400 mb-4">Supported formats: PDF, DOCX, TXT</p>
      <label className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md text-sm font-medium transition-colors">
        Browse Files
        <input type="file" className="hidden" accept=".pdf,.docx,.txt" onChange={handleChange} />
      </label>
    </div>
  );
}
