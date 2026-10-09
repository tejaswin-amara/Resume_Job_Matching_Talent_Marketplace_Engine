"use client";
import React from 'react';

export const UploadDropzone = ({ onUpload, className }: any) => {
  return (
    <div className={`border-2 border-dashed border-gray-600 rounded p-6 text-center text-gray-400 ${className || ''}`}
      onDragOver={(event) => event.preventDefault()}
      onDrop={(event) => {
        event.preventDefault();
        const file = event.dataTransfer.files[0];
        if (file) onUpload(file);
      }}
    >
      <input type="file" onChange={(e) => {
        if (e.target.files && e.target.files.length > 0) {
          onUpload(e.target.files[0]);
        }
      }} />
      <p>Drag &amp; drop resume, or click to browse</p>
    </div>
  );
};
