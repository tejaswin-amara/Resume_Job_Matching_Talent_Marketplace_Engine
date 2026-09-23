import { ResumeDropzone } from '@/components/feedback/resume-dropzone';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

describe('ResumeDropzone Component', () => {
  it('triggers onFileAccepted when a valid PDF file is selected', async () => {
    const handleFileAccepted = vi.fn();
    render(<ResumeDropzone onFileAccepted={handleFileAccepted} />);

    const input = screen.getByTestId('dropzone-input');
    const validFile = new File(['%PDF-1.4 sample content'], 'resume_jane_doe.pdf', {
      type: 'application/pdf',
    });

    fireEvent.change(input, {
      target: { files: [validFile] },
    });

    await waitFor(() => {
      expect(handleFileAccepted).toHaveBeenCalledTimes(1);
      expect(handleFileAccepted).toHaveBeenCalledWith(validFile);
    });

    expect(screen.queryByTestId('dropzone-error')).not.toBeInTheDocument();
  });

  it('rejects invalid MIME types and displays an error message', async () => {
    const handleFileAccepted = vi.fn();
    render(<ResumeDropzone onFileAccepted={handleFileAccepted} />);

    const input = screen.getByTestId('dropzone-input');
    const invalidFile = new File(['invalid binary image'], 'avatar.png', {
      type: 'image/png',
    });

    fireEvent.change(input, {
      target: { files: [invalidFile] },
    });

    await waitFor(() => {
      expect(handleFileAccepted).not.toHaveBeenCalled();
      const errorElem = screen.getByTestId('dropzone-error');
      expect(errorElem).toBeInTheDocument();
      expect(errorElem).toHaveTextContent(/Invalid file format/i);
    });
  });

  it('rejects files exceeding 10MB limit', async () => {
    const handleFileAccepted = vi.fn();
    render(<ResumeDropzone onFileAccepted={handleFileAccepted} />);

    const input = screen.getByTestId('dropzone-input');
    // Create oversized file: 11MB
    const oversizedFile = new File([new ArrayBuffer(11 * 1024 * 1024)], 'giant_portfolio.pdf', {
      type: 'application/pdf',
    });

    fireEvent.change(input, {
      target: { files: [oversizedFile] },
    });

    await waitFor(() => {
      expect(handleFileAccepted).not.toHaveBeenCalled();
      const errorElem = screen.getByTestId('dropzone-error');
      expect(errorElem).toBeInTheDocument();
      expect(errorElem).toHaveTextContent(/exceeds the 10MB limit/i);
    });
  });

  it('renders step-by-step progress indicators when isLoading is true', () => {
    const handleFileAccepted = vi.fn();
    render(<ResumeDropzone onFileAccepted={handleFileAccepted} isLoading={true} currentStep={2} />);

    expect(screen.getByTestId('dropzone-loading')).toBeInTheDocument();
    expect(screen.getByText(/Deep Semantic Analysis in Progress/i)).toBeInTheDocument();
    expect(screen.getByText(/Step 2 of 3/i)).toBeInTheDocument();
    expect(screen.getByText(/Computing vector embeddings/i)).toBeInTheDocument();
  });
});
