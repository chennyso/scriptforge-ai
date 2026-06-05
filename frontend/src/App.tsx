import { useMemo, useState } from "react";
import { Download, FileCheck2, Loader2, PenLine, RefreshCw, Sparkles, Upload } from "lucide-react";
import { postJson, Settings } from "./lib/api";

const sampleText = `第1章 雨夜来信
雨从傍晚下到深夜，林知远回到旧书房时，窗台上多了一封没有署名的信。沈清站在灯下，像是已经等了很久。她说这封信不能打开，可林知远还是看见了信角露出的旧印章。

第2章 长街追问
第二天清晨，长街被雾气遮住。周启拦住林知远，告诉他那枚印章属于十年前失踪的档案室。沈清追来时，三个人都明白，过去并没有结束。

第3章 庭院摊牌
雨夜的庭院里，沈清终于承认自己保管过那份档案。周启逼她说出名单的下落，林知远却发现名单上第一个名字正是自己的父亲。`;

type GenerateResult = {
  chapters: Array<{ index: number; title: string; word_count: number; content: string }>;
  blueprint: Record<string, any>;
  yaml_text: string;
  script: any;
  validation: { valid: boolean; issues: Array<{ path: string; message: string }> };
  provider: string;
};

const defaultSettings: Settings = {
  script_type: "screenplay",
  style: "conflict_plus",
  target_scene_count: 6,
  narration_level: "light",
  dialogue_density: "medium"
};

export function App() {
  const [text, setText] = useState(sampleText);
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [yamlText, setYamlText] = useState("");
  const [selectedScene, setSelectedScene] = useState("SC001");
  const [loading, setLoading] = useState(false);
  const [notice, setNotice] = useState("");

  const stats = useMemo(() => {
    const chars = text.trim().length;
    const chapters = (text.match(/^\s*(第[一二三四五六七八九十百千万\d]+[章节回幕]|Chapter\s+\d+)/gim) || []).length;
    return { chars, chapters };
  }, [text]);

  async function generate() {
    setLoading(true);
    setNotice("");
    try {
      const data = await postJson<GenerateResult>("/api/generate", { text, settings });
      setResult(data);
      setYamlText(data.yaml_text);
      setSelectedScene(data.script?.episodes?.[0]?.scenes?.[0]?.id || "SC001");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "生成失败");
    } finally {
      setLoading(false);
    }
  }

  async function validate() {
    try {
      const validation = await postJson<GenerateResult["validation"]>("/api/validate", { yaml_text: yamlText });
      setResult((current) => (current ? { ...current, validation } : current));
      setNotice(validation.valid ? "Schema 校验通过。" : "发现结构问题，请查看右侧问题列表。");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "校验失败");
    }
  }

  async function rewrite(instruction: string) {
    if (!yamlText) return;
    setLoading(true);
    try {
      const data = await postJson<Pick<GenerateResult, "yaml_text" | "script" | "validation" | "provider">>("/api/rewrite", {
        yaml_text: yamlText,
        scene_id: selectedScene,
        instruction
      });
      setYamlText(data.yaml_text);
      setResult((current) => current ? { ...current, ...data } : null);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "重写失败");
    } finally {
      setLoading(false);
    }
  }

  function onFile(file?: File) {
    if (!file) return;
    file.text().then(setText);
  }

  function downloadYaml() {
    const blob = new Blob([yamlText], { type: "text/yaml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "scriptforge-output.yaml";
    link.click();
    URL.revokeObjectURL(url);
  }

  const scenes = result?.script?.episodes?.flatMap((episode: any) => episode.scenes) || [];

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Novel2Script Studio</p>
          <h1>ScriptForge AI</h1>
        </div>
        <div className="status-strip">
          <span>{stats.chars} 字符</span>
          <span className={stats.chapters >= 3 ? "ok" : "warn"}>{stats.chapters || "自动"} 章节</span>
          <span>{result?.provider || "待生成"}</span>
        </div>
      </header>

      <section className="workspace">
        <aside className="panel input-panel">
          <div className="panel-head">
            <h2>小说输入</h2>
            <label className="icon-button">
              <Upload size={18} />
              <input type="file" accept=".txt,.md" onChange={(event) => onFile(event.target.files?.[0])} />
            </label>
          </div>
          <textarea value={text} onChange={(event) => setText(event.target.value)} />

          <div className="settings">
            <Select label="剧本类型" value={settings.script_type} onChange={(value) => setSettings({ ...settings, script_type: value as Settings["script_type"] })} options={[["screenplay", "影视剧"], ["short_drama", "短剧"], ["stage_play", "舞台剧"], ["audio_drama", "广播剧"]]} />
            <Select label="改编风格" value={settings.style} onChange={(value) => setSettings({ ...settings, style: value as Settings["style"] })} options={[["conflict_plus", "强化冲突"], ["faithful", "忠实原文"], ["compressed", "压缩节奏"], ["dialogue_plus", "增强对白"]]} />
            <label className="range-row">场景数 <input type="range" min="3" max="12" value={settings.target_scene_count} onChange={(event) => setSettings({ ...settings, target_scene_count: Number(event.target.value) })} /> <b>{settings.target_scene_count}</b></label>
            <button className="primary" onClick={generate} disabled={loading}>
              {loading ? <Loader2 className="spin" size={18} /> : <Sparkles size={18} />}
              生成结构化剧本
            </button>
          </div>
        </aside>

        <section className="panel preview-panel">
          <div className="panel-head">
            <h2>剧本预览</h2>
            <div className="toolbar">
              <button onClick={validate}><FileCheck2 size={17} />校验</button>
              <button onClick={downloadYaml} disabled={!yamlText}><Download size={17} />导出</button>
            </div>
          </div>
          {result ? (
            <div className="preview-scroll">
              <div className={result.validation.valid ? "validation valid" : "validation invalid"}>
                {result.validation.valid ? "Schema 校验通过" : `${result.validation.issues.length} 个结构问题`}
              </div>
              <div className="blueprint">
                <h3>故事蓝图</h3>
                <p>{result.blueprint.theme}</p>
                <div>{result.blueprint.chapter_summaries?.map((item: any) => <span key={item.chapter}>第{item.chapter}章：{item.turning_point}</span>)}</div>
              </div>
              <div className="scene-list">
                {scenes.map((scene: any) => (
                  <article className={selectedScene === scene.id ? "scene selected" : "scene"} key={scene.id} onClick={() => setSelectedScene(scene.id)}>
                    <div><strong>{scene.id}</strong><span>{scene.heading}</span></div>
                    <p>{scene.objective}</p>
                    {scene.beats.slice(0, 4).map((beat: any, idx: number) => <small key={idx}>{beat.speaker ? `${beat.speaker}: ` : ""}{beat.content}</small>)}
                  </article>
                ))}
              </div>
            </div>
          ) : (
            <div className="empty-state"><PenLine size={42} /><p>输入三章以上小说后生成剧本初稿。</p></div>
          )}
        </section>

        <aside className="panel yaml-panel">
          <div className="panel-head">
            <h2>YAML 编辑</h2>
            <button onClick={() => rewrite("more_cinematic")} disabled={!yamlText || loading}><RefreshCw size={17} />影视化</button>
          </div>
          <select className="scene-select" value={selectedScene} onChange={(event) => setSelectedScene(event.target.value)}>
            {scenes.map((scene: any) => <option key={scene.id}>{scene.id}</option>)}
          </select>
          <div className="rewrite-grid">
            <button onClick={() => rewrite("intensify_conflict")}>强化冲突</button>
            <button onClick={() => rewrite("add_dialogue")}>增加对白</button>
            <button onClick={() => rewrite("compress_pace")}>压缩节奏</button>
          </div>
          <textarea className="yaml-editor" value={yamlText} onChange={(event) => setYamlText(event.target.value)} placeholder="生成后的 YAML 会显示在这里" />
          <div className="issues">
            {notice && <p>{notice}</p>}
            {result?.validation.issues.map((issue) => <p key={`${issue.path}-${issue.message}`}>{issue.path}: {issue.message}</p>)}
          </div>
        </aside>
      </section>
    </main>
  );
}

function Select(props: { label: string; value: string; options: string[][]; onChange: (value: string) => void }) {
  return (
    <label>
      {props.label}
      <select value={props.value} onChange={(event) => props.onChange(event.target.value)}>
        {props.options.map(([value, label]) => <option value={value} key={value}>{label}</option>)}
      </select>
    </label>
  );
}
