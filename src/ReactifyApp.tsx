import React, { useEffect, useMemo, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Camera, Play, Upload, Link2, Trash2, Video, Hand, Smile } from "lucide-react";

const DEFAULT_GESTURES = [
  { id: 1, name: "Thumbs Up", type: "hand" },
  { id: 2, name: "Peace Sign", type: "hand" },
  { id: 3, name: "Surprised", type: "face" },
  { id: 4, name: "Happy", type: "face" },
  { id: 5, name: "Angry", type: "face" },
];

const STORAGE_KEY = "reactify_app_state_v1";

function readSavedState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return {
        clips: [],
        mappings: {},
        live: false,
      };
    }
    return JSON.parse(raw);
  } catch (error) {
    return {
      clips: [],
      mappings: {},
      live: false,
    };
  }
}

function makeId() {
  return `${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export default function ReactifyApp() {
  const saved = useMemo(() => readSavedState(), []);

  const [clips, setClips] = useState(saved.clips || []);
  const [mappings, setMappings] = useState(saved.mappings || {});
  const [live, setLive] = useState(saved.live || false);
  const [activeTab, setActiveTab] = useState("home");
  const [selectedGestureId, setSelectedGestureId] = useState("");
  const [selectedClipId, setSelectedClipId] = useState("");
  const [clipName, setClipName] = useState("");
  const [detectedGesture, setDetectedGesture] = useState("None");
  const [cameraStatus, setCameraStatus] = useState("Idle");
  const [message, setMessage] = useState("Welcome to Reactify");
  const [autoPlay, setAutoPlay] = useState(true);

  const videoPreviewRef = useRef(null);
  const liveVideoRef = useRef(null);
  const playbackRef = useRef(null);
  const mediaStreamRef = useRef(null);

  useEffect(() => {
    const state = { clips, mappings, live };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [clips, mappings, live]);

  useEffect(() => {
    return () => {
      stopCamera();
      clips.forEach((clip) => {
        if (clip.objectUrl) {
          URL.revokeObjectURL(clip.objectUrl);
        }
      });
    };
  }, []);

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });

      mediaStreamRef.current = stream;

      if (liveVideoRef.current) {
        liveVideoRef.current.srcObject = stream;
      }

      setCameraStatus("Camera active");
      setMessage("Live mode is on. Waiting for a gesture.");
      return true;
    } catch (error) {
      setCameraStatus("Camera blocked");
      setMessage("Camera access was denied.");
      return false;
    }
  }

  function stopCamera() {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    if (liveVideoRef.current) {
      liveVideoRef.current.srcObject = null;
    }
    setCameraStatus("Idle");
  }

  async function handleStartLiveMode() {
    const ok = await startCamera();
    if (!ok) {
      setLive(false);
      return;
    }
    setLive(true);
    setActiveTab("live");
  }

  function handleStopLiveMode() {
    setLive(false);
    stopCamera();
    setDetectedGesture("None");
    setMessage("Live mode stopped.");
  }

  function handleUploadClip(event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith("video/")) {
      setMessage("Only video files are supported.");
      return;
    }

    const name = clipName.trim() || file.name;
    const objectUrl = URL.createObjectURL(file);

    const newClip = {
      id: makeId(),
      name,
      fileName: file.name,
      type: file.type,
      objectUrl,
    };

    setClips((prev) => [...prev, newClip]);
    setClipName("");
    setMessage(`Uploaded clip: ${name}`);

    if (videoPreviewRef.current) {
      videoPreviewRef.current.src = objectUrl;
    }
  }

  function handleCreateMapping() {
    if (!selectedGestureId || !selectedClipId) {
      setMessage("Select both a gesture and a clip first.");
      return;
    }

    setMappings((prev) => ({
      ...prev,
      [selectedGestureId]: selectedClipId,
    }));

    const gesture = DEFAULT_GESTURES.find((g) => String(g.id) === String(selectedGestureId));
    const clip = clips.find((c) => c.id === selectedClipId);
    setMessage(`Mapped ${gesture?.name || "gesture"} to ${clip?.name || "clip"}`);
  }

  function playMappedClipByGestureName(gestureName) {
    const gesture = DEFAULT_GESTURES.find((g) => g.name === gestureName);
    if (!gesture) {
      setMessage("Gesture not recognized.");
      return;
    }

    const clipId = mappings[String(gesture.id)];
    if (!clipId) {
      setMessage(`No clip mapped for ${gesture.name}.`);
      return;
    }

    const clip = clips.find((c) => c.id === clipId);
    if (!clip) {
      setMessage("Mapped clip could not be found.");
      return;
    }

    setDetectedGesture(gesture.name);
    setMessage(`Detected ${gesture.name}. Playing ${clip.name}.`);

    if (playbackRef.current) {
      playbackRef.current.src = clip.objectUrl;
      if (autoPlay) {
        playbackRef.current.play().catch(() => {
          setMessage("Clip is ready. Press play if autoplay is blocked.");
        });
      }
    }
  }

  function handleDeleteClip(clipId) {
    const clip = clips.find((item) => item.id === clipId);
    if (clip?.objectUrl) {
      URL.revokeObjectURL(clip.objectUrl);
    }

    setClips((prev) => prev.filter((clipItem) => clipItem.id !== clipId));

    setMappings((prev) => {
      const next = { ...prev };
      Object.keys(next).forEach((gestureId) => {
        if (next[gestureId] === clipId) {
          delete next[gestureId];
        }
      });
      return next;
    });

    setMessage("Clip deleted.");
  }

  function mappedClipName(gestureId) {
    const clipId = mappings[String(gestureId)];
    const clip = clips.find((item) => item.id === clipId);
    return clip ? clip.name : "Not mapped";
  }

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Reactify</h1>
            <p className="text-sm text-slate-600">
              Real-time meme triggering with face and hand gestures
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant={activeTab === "home" ? "default" : "outline"} onClick={() => setActiveTab("home")}>Home</Button>
            <Button variant={activeTab === "upload" ? "default" : "outline"} onClick={() => setActiveTab("upload")}>Upload Clip</Button>
            <Button variant={activeTab === "map" ? "default" : "outline"} onClick={() => setActiveTab("map")}>Map Gestures</Button>
            <Button variant={activeTab === "live" ? "default" : "outline"} onClick={() => setActiveTab("live")}>Live Mode</Button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-2 rounded-2xl shadow-sm">
            <CardHeader>
              <CardTitle>
                {activeTab === "home" && "Home"}
                {activeTab === "upload" && "Upload Clip"}
                {activeTab === "map" && "Map Gestures"}
                {activeTab === "live" && "Live Mode"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {activeTab === "home" && (
                <div className="grid gap-4 md:grid-cols-3">
                  <Card className="rounded-2xl">
                    <CardContent className="flex flex-col gap-3 p-5">
                      <Camera className="h-8 w-8" />
                      <div>
                        <h3 className="font-semibold">Start Live Mode</h3>
                        <p className="text-sm text-slate-600">Turn on the camera and wait for gestures.</p>
                      </div>
                      <Button onClick={handleStartLiveMode}>Start</Button>
                    </CardContent>
                  </Card>

                  <Card className="rounded-2xl">
                    <CardContent className="flex flex-col gap-3 p-5">
                      <Upload className="h-8 w-8" />
                      <div>
                        <h3 className="font-semibold">Upload Clip</h3>
                        <p className="text-sm text-slate-600">Add meme clips to local app state.</p>
                      </div>
                      <Button variant="outline" onClick={() => setActiveTab("upload")}>Open</Button>
                    </CardContent>
                  </Card>

                  <Card className="rounded-2xl">
                    <CardContent className="flex flex-col gap-3 p-5">
                      <Link2 className="h-8 w-8" />
                      <div>
                        <h3 className="font-semibold">Map Gestures</h3>
                        <p className="text-sm text-slate-600">Link gestures to clips for playback.</p>
                      </div>
                      <Button variant="outline" onClick={() => setActiveTab("map")}>Open</Button>
                    </CardContent>
                  </Card>
                </div>
              )}

              {activeTab === "upload" && (
                <div className="space-y-5">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label htmlFor="clipName">Clip Name</Label>
                      <Input
                        id="clipName"
                        value={clipName}
                        onChange={(e) => setClipName(e.target.value)}
                        placeholder="Enter a clip name"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="clipFile">Video File</Label>
                      <Input id="clipFile" type="file" accept="video/*" onChange={handleUploadClip} />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Preview</Label>
                    <video
                      ref={videoPreviewRef}
                      controls
                      className="w-full rounded-2xl border bg-black"
                    />
                  </div>

                  <div className="grid gap-3">
                    {clips.length === 0 && <p className="text-sm text-slate-600">No clips uploaded yet.</p>}
                    {clips.map((clip) => (
                      <div key={clip.id} className="flex items-center justify-between rounded-2xl border p-4">
                        <div>
                          <p className="font-medium">{clip.name}</p>
                          <p className="text-sm text-slate-500">{clip.fileName}</p>
                        </div>
                        <Button variant="outline" onClick={() => handleDeleteClip(clip.id)}>
                          <Trash2 className="mr-2 h-4 w-4" /> Delete
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === "map" && (
                <div className="space-y-5">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label>Select Gesture</Label>
                      <Select value={selectedGestureId} onValueChange={setSelectedGestureId}>
                        <SelectTrigger>
                          <SelectValue placeholder="Choose a gesture" />
                        </SelectTrigger>
                        <SelectContent>
                          {DEFAULT_GESTURES.map((gesture) => (
                            <SelectItem key={gesture.id} value={String(gesture.id)}>
                              {gesture.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Select Clip</Label>
                      <Select value={selectedClipId} onValueChange={setSelectedClipId}>
                        <SelectTrigger>
                          <SelectValue placeholder="Choose a clip" />
                        </SelectTrigger>
                        <SelectContent>
                          {clips.map((clip) => (
                            <SelectItem key={clip.id} value={clip.id}>
                              {clip.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <Button onClick={handleCreateMapping}>Save Mapping</Button>

                  <div className="grid gap-3 md:grid-cols-2">
                    {DEFAULT_GESTURES.map((gesture) => (
                      <Card key={gesture.id} className="rounded-2xl">
                        <CardContent className="flex items-center justify-between p-4">
                          <div className="flex items-center gap-3">
                            {gesture.type === "hand" ? <Hand className="h-5 w-5" /> : <Smile className="h-5 w-5" />}
                            <div>
                              <p className="font-medium">{gesture.name}</p>
                              <p className="text-sm text-slate-500">{mappedClipName(gesture.id)}</p>
                            </div>
                          </div>
                          <Badge variant="secondary">{gesture.type}</Badge>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === "live" && (
                <div className="space-y-5">
                  <div className="flex flex-wrap items-center gap-3">
                    {!live ? (
                      <Button onClick={handleStartLiveMode}>
                        <Play className="mr-2 h-4 w-4" /> Start Live Mode
                      </Button>
                    ) : (
                      <Button variant="outline" onClick={handleStopLiveMode}>Stop Live Mode</Button>
                    )}

                    <div className="flex items-center gap-2 rounded-full border px-3 py-2">
                      <Switch checked={autoPlay} onCheckedChange={setAutoPlay} />
                      <span className="text-sm">Autoplay clip</span>
                    </div>
                  </div>

                  <div className="grid gap-4 lg:grid-cols-2">
                    <div className="space-y-2">
                      <Label>Camera View</Label>
                      <video
                        ref={liveVideoRef}
                        autoPlay
                        muted
                        playsInline
                        className="aspect-video w-full rounded-2xl border bg-black object-cover"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Clip Playback</Label>
                      <video
                        ref={playbackRef}
                        controls
                        className="aspect-video w-full rounded-2xl border bg-black"
                      />
                    </div>
                  </div>

                  <div className="grid gap-3 md:grid-cols-3">
                    <Card className="rounded-2xl">
                      <CardContent className="p-4">
                        <p className="text-sm text-slate-500">Status</p>
                        <p className="font-semibold">{live ? "Live" : "Stopped"}</p>
                      </CardContent>
                    </Card>
                    <Card className="rounded-2xl">
                      <CardContent className="p-4">
                        <p className="text-sm text-slate-500">Camera</p>
                        <p className="font-semibold">{cameraStatus}</p>
                      </CardContent>
                    </Card>
                    <Card className="rounded-2xl">
                      <CardContent className="p-4">
                        <p className="text-sm text-slate-500">Detected Gesture</p>
                        <p className="font-semibold">{detectedGesture}</p>
                      </CardContent>
                    </Card>
                  </div>

                  <div className="space-y-3">
                    <Label>Demo Gesture Triggers</Label>
                    <div className="flex flex-wrap gap-2">
                      {DEFAULT_GESTURES.map((gesture) => (
                        <Button
                          key={gesture.id}
                          variant="outline"
                          onClick={() => playMappedClipByGestureName(gesture.name)}
                        >
                          Trigger {gesture.name}
                        </Button>
                      ))}
                    </div>
                    <p className="text-sm text-slate-500">
                      These buttons simulate gesture detection for now. Replace this with MediaPipe output next.
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card className="rounded-2xl shadow-sm">
              <CardHeader>
                <CardTitle>System State</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex items-center justify-between">
                  <span>Clips</span>
                  <Badge>{clips.length}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Gestures</span>
                  <Badge>{DEFAULT_GESTURES.length}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Mapped</span>
                  <Badge>{Object.keys(mappings).length}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Live Mode</span>
                  <Badge>{live ? "On" : "Off"}</Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="rounded-2xl shadow-sm">
              <CardHeader>
                <CardTitle>Message Center</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-700">{message}</p>
              </CardContent>
            </Card>

            <Card className="rounded-2xl shadow-sm">
              <CardHeader>
                <CardTitle>Next Step</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-slate-700">
                <p>Connect MediaPipe gesture results to the live mode trigger function.</p>
                <p>Store uploaded files in a backend or indexed storage if you need persistence beyond the current browser session.</p>
                <p>Expand gestures, add validation, and add error states for unsupported uploads.</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
