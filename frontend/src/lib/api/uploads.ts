import * as tus from "tus-js-client";

export interface UploadProgress {
  bytesUploaded: number;
  bytesTotal: number;
}

export function uploadFile(
  file: File,
  onProgress: (p: UploadProgress) => void,
): Promise<{ uploadUrl: string }> {
  return new Promise((resolve, reject) => {
    const upload = new tus.Upload(file, {
      endpoint: "/uploads/",
      retryDelays: [0, 1000, 3000, 5000],
      metadata: { filename: file.name, filetype: file.type || "application/octet-stream" },
      onError: reject,
      onProgress: (uploaded, total) => onProgress({ bytesUploaded: uploaded, bytesTotal: total }),
      onSuccess: () => resolve({ uploadUrl: upload.url! }),
    });
    upload.start();
  });
}
