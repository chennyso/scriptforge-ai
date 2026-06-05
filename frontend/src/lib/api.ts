export type Settings = {
  script_type: "screenplay" | "short_drama" | "stage_play" | "audio_drama";
  style: "faithful" | "conflict_plus" | "compressed" | "dialogue_plus";
  target_scene_count: number;
  narration_level: "none" | "light" | "balanced";
  dialogue_density: "low" | "medium" | "high";
};

export async function postJson<T>(url: string, body: unknown): Promise<T> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

