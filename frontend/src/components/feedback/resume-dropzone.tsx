'use client';

import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import {
  AlertTriangle,
  CheckCircle2,
  FileCheck,
  FileText,
  Loader2,
  UploadCloud,
} from 'lucide-react';
import * as React from 'react';
import { type FileRejection, useDropzone } from 'react-dropzone';

export interface ResumeDropzoneProps {
  onFileAccepted: (file: File) => void;
  isLoading?: boolean;
  currentStep?: 1 | 2 | 3;
  disabled?: boolean;
  className?: string;
}

export const PROCESSING_STEPS = [
  { id: 1, label: 'Extracting text & formatting structures' },
  { id: 2, label: 'Computing vector embeddings (Sentence-BERT)' },
  { id: 3, label: 'Aligning taxonomy & skill ontology' },
] as const;

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export const ACCEPTED_MIME_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/msword': ['.doc'],
};

export function ResumeDropzone({
  onFileAccepted,
  isLoading = false,
  currentStep = 1,
  disabled = false,
  className,
}: ResumeDropzoneProps) {
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [selectedFileName, setSelectedFileName] = React.useState<string | null>(null);

  const onDrop = React.useCallback(
    (acceptedFiles: File[], fileRejections: FileRejection[]) => {
      setErrorMessage(null);

      if (fileRejections.length > 0) {
        const rejection = fileRejections[0];
        const error = rejection.errors[0];
        if (error.code === 'file-invalid-type') {
          setErrorMessage('Invalid file format. Please upload a PDF or DOCX file.');
        } else if (error.code === 'file-too-large') {
          setErrorMessage('File size exceeds the 10MB limit. Please upload a smaller file.');
        } else {
          setErrorMessage(error.message || 'Error processing file. Please try again.');
        }
        return;
      }

      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        setSelectedFileName(file.name);
        onFileAccepted(file);
      }
    },
    [onFileAccepted],
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: ACCEPTED_MIME_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: false,
    disabled: disabled || isLoading,
  });

  const progressPercent = Math.round((currentStep / 3) * 100);

  return (
    <div className={cn('w-full space-y-3', className)}>
      <div
        {...getRootProps()}
        data-testid="resume-dropzone"
        className={cn(
          'relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 text-center transition-all duration-200 cursor-pointer select-none',
          isDragActive && !isDragReject
            ? 'border-blue-500 bg-blue-950/30 ring-4 ring-blue-500/10'
            : isDragReject
              ? 'border-rose-500 bg-rose-950/30'
              : 'border-slate-700 bg-slate-900/40 hover:border-slate-500 hover:bg-slate-900/70',
          (disabled || isLoading) && 'pointer-events-none opacity-80 cursor-not-allowed',
        )}
      >
        <input {...getInputProps()} data-testid="dropzone-input" />

        {isLoading ? (
          <div
            className="flex flex-col items-center justify-center space-y-4 w-full max-w-sm py-4"
            data-testid="dropzone-loading"
          >
            <div className="relative flex items-center justify-center">
              <Loader2 className="h-10 w-10 animate-spin text-blue-500" />
              <FileCheck className="absolute h-5 w-5 text-blue-400" />
            </div>

            <div className="space-y-1 text-center">
              <h4 className="text-sm font-semibold text-white">
                Deep Semantic Analysis in Progress
              </h4>
              <p className="text-xs text-slate-400">
                Parsing <span className="font-mono text-slate-300">{selectedFileName}</span>
              </p>
            </div>

            <div className="w-full space-y-2">
              <Progress value={progressPercent} className="h-1.5" />
              <div className="flex justify-between text-[11px] text-slate-400">
                <span>Step {currentStep} of 3</span>
                <span>{progressPercent}%</span>
              </div>
            </div>

            {/* Step-by-step indicators */}
            <div className="w-full space-y-2 text-left pt-2">
              {PROCESSING_STEPS.map((step) => {
                const isComplete = currentStep > step.id;
                const isCurrent = currentStep === step.id;

                return (
                  <div
                    key={step.id}
                    className={cn(
                      'flex items-center gap-2 text-xs transition-colors',
                      isComplete
                        ? 'text-emerald-400'
                        : isCurrent
                          ? 'text-blue-400 font-medium'
                          : 'text-slate-600',
                    )}
                  >
                    {isComplete ? (
                      <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
                    ) : isCurrent ? (
                      <Loader2 className="h-3.5 w-3.5 shrink-0 animate-spin" />
                    ) : (
                      <div className="h-3.5 w-3.5 rounded-full border border-slate-700 shrink-0" />
                    )}
                    <span className="truncate">{step.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center space-y-3">
            <div
              className={cn(
                'rounded-full p-4 transition-colors',
                isDragActive ? 'bg-blue-600/20 text-blue-400' : 'bg-slate-800/80 text-slate-400',
              )}
            >
              <UploadCloud className="h-8 w-8" />
            </div>

            <div className="space-y-1">
              <p className="text-sm font-medium text-slate-200">
                <span className="text-blue-400 underline decoration-blue-500/40 underline-offset-4 hover:text-blue-300">
                  Click to upload
                </span>{' '}
                or drag and drop candidate resume
              </p>
              <p className="text-xs text-slate-400">
                Supported formats: PDF, DOCX (Max size: 10MB)
              </p>
            </div>

            {selectedFileName && (
              <div className="flex items-center gap-2 rounded-md bg-slate-800/80 px-3 py-1 text-xs text-slate-300 border border-slate-700">
                <FileText className="h-3.5 w-3.5 text-blue-400" />
                <span className="max-w-[220px] truncate">{selectedFileName}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {errorMessage && (
        <div
          data-testid="dropzone-error"
          className="flex items-center gap-2 rounded-lg border border-rose-900/60 bg-rose-950/40 p-3 text-xs text-rose-300 animate-in fade-in"
        >
          <AlertTriangle className="h-4 w-4 shrink-0 text-rose-400" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}
