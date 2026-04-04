import { useEffect, useRef, useState } from "react";

export default function LiveView() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    let stream: MediaStream | null = null;

    async function startCamera() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user" },
          audio: false,
        });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }
      } catch (e) {
        const msg =
          e instanceof Error ? e.message : "Camera permission or device error.";
        setError(msg);
      }
    }

    startCamera();

    return () => {
      // Stop camera when component unmounts
      if (stream) {
        stream.getTracks().forEach((t) => t.stop());
      }
    };
  }, []);

  return (
    <div style={{ padding: 16 }}>
      <h2>Live Mode (Camera Preview)</h2>
      {error && (
        <p style={{ color: "crimson" }}>
          Camera error: {error}
        </p>
      )}
      <video
        ref={videoRef}
        playsInline
        muted
        style={{
          width: "100%",
          maxWidth: 720,
          borderRadius: 12,
          border: "1px solid #ccc",
        }}
      />
      <p style={{ marginTop: 8, opacity: 0.8 }}>
        If you can see yourself here, Step 1 is done.
      </p>
    </div>
  );
}
