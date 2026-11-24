import argparse
import base64
import io
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import torch
from PIL import Image

from scripts.predict import (
    build_model,
    load_checkpoint,
    load_class_to_idx,
    resolve_device,
    strip_module_prefix,
)
from src.data.transforms import build_transforms

STATE = {
    "model": None,
    "transform": None,
    "device": None,
    "idx_to_class": None,
    "num_classes": None,
    "model_name": None,
    "zh": None,
    "lock": threading.Lock(),
}

INDEX_HTML = """<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>LeafGuard 叶片病害识别 Demo</title>
<style>
  :root { --bg:#0f172a; --card:#1e293b; --accent:#22c55e; --text:#e2e8f0; --muted:#94a3b8; }
  * { box-sizing: border-box; }
  body { margin:0; font-family: "Microsoft YaHei", system-ui, sans-serif; background:var(--bg); color:var(--text); }
  .wrap { max-width: 720px; margin: 0 auto; padding: 32px 20px 64px; }
  h1 { font-size: 22px; margin: 0 0 4px; }
  .sub { color: var(--muted); font-size: 13px; margin-bottom: 24px; }
  .card { background: var(--card); border-radius: 14px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,.3); }
  .drop { border: 2px dashed #334155; border-radius: 12px; padding: 28px; text-align: center; cursor: pointer; transition: .15s; }
  .drop:hover { border-color: var(--accent); }
  .drop.drag { border-color: var(--accent); background: rgba(34,197,94,.08); }
  input[type=file] { display:none; }
  #preview { max-width: 100%; max-height: 260px; border-radius: 10px; margin-top: 16px; display:none; }
  .result { margin-top: 22px; display:none; }
  .pred { font-size: 20px; font-weight: 700; }
  .pred .tag { color: var(--accent); }
  .pred .en { color: var(--muted); font-size: 13px; font-weight: 400; }
  .bar-row { margin: 10px 0; }
  .bar-label { display:flex; justify-content:space-between; font-size: 13px; margin-bottom: 4px; }
  .bar-track { background:#0b1220; border-radius: 8px; height: 14px; overflow:hidden; }
  .bar-fill { height:100%; background: linear-gradient(90deg,#16a34a,#22c55e); width:0; transition: width .5s ease; }
  .note { color: var(--muted); font-size: 12px; margin-top: 18px; }
  .status { color: var(--muted); font-size: 13px; margin-top: 12px; min-height: 18px; }
</style>
</head>
<body>
<div class="wrap">
  <h1>🌿 LeafGuard · 叶片病害识别</h1>
  <div class="sub">上传一张植物叶片照片，识别它是否患病及可能的病害类别（本页为本地演示，结果仅供参考）。</div>
  <div class="card">
    <label class="drop" id="drop">
      <div>点击选择，或把图片拖到这里</div>
      <div class="sub" style="margin:8px 0 0">支持 JPG / PNG</div>
      <input type="file" id="file" accept="image/*" />
      <img id="preview" alt="preview" />
    </label>
    <div class="status" id="status"></div>
    <div class="result" id="result">
      <div class="pred">预测：<span class="tag" id="predName">-</span> <span class="en" id="predEn"></span></div>
      <div id="bars"></div>
      <div class="note">分数为 softmax 置信度，不代表校准后的诊断概率；本项目为课程/研究演示，不能作为真实农业诊断依据。</div>
    </div>
  </div>
</div>
<script>
const fileInput = document.getElementById('file');
const drop = document.getElementById('drop');
const preview = document.getElementById('preview');
const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');
const predName = document.getElementById('predName');
const bars = document.getElementById('bars');

function handleFile(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    preview.src = reader.result;
    preview.style.display = 'block';
    statusEl.textContent = '正在识别…';
    resultEl.style.display = 'none';
    fetch('/api/predict', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({image_b64: reader.result})
    }).then(r => r.json()).then(data => {
      if (data.error) { statusEl.textContent = '出错：' + data.error; return; }
      statusEl.textContent = '';
      render(data);
      resultEl.style.display = 'block';
    }).catch(e => { statusEl.textContent = '请求失败：' + e; });
  };
  reader.readAsDataURL(file);
}

function render(data) {
  predName.textContent = data.prediction;
  var predEn = document.getElementById('predEn');
  predEn.textContent = data.prediction_en ? '(' + data.prediction_en + ')' : '';
  bars.innerHTML = '';
  data.top_k.forEach(item => {
    const pct = (item.score * 100);
    var label = item.class_name_zh || item.class_name;
    const row = document.createElement('div');
    row.className = 'bar-row';
    row.innerHTML = '<div class="bar-label"><span>' + label +
      '</span><span>' + pct.toFixed(1) + '%</span></div>' +
      '<div class="bar-track"><div class="bar-fill"></div></div>';
    bars.appendChild(row);
    requestAnimationFrame(() => { row.querySelector('.bar-fill').style.width = pct + '%'; });
  });
}

fileInput.addEventListener('change', e => handleFile(e.target.files[0]));
['dragover','dragenter'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add('drag'); }));
['dragleave','drop'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove('drag'); }));
drop.addEventListener('drop', e => { if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); });
</script>
</body>
</html>
"""


def setup(checkpoint, classes, device_arg, zh_map_path="splits/class_to_zh.json"):
    device = resolve_device(device_arg)
    ckpt = load_checkpoint(checkpoint, device)
    if "model_name" not in ckpt:
        raise SystemExit("checkpoint missing required field: model_name")
    class_to_idx, _ = load_class_to_idx(ckpt, classes)
    num_classes = int(ckpt.get("num_classes", len(class_to_idx)))
    model = build_model(ckpt["model_name"], num_classes)
    state_dict = ckpt.get("model_state_dict") or ckpt.get("state_dict")
    if state_dict is None:
        raise SystemExit("checkpoint missing required field: model_state_dict")
    model.load_state_dict(strip_module_prefix(state_dict))
    model.to(device).eval()

    zh = {}
    zh_path = Path(zh_map_path)
    if zh_path.is_file():
        with open(zh_path, encoding="utf-8") as f:
            zh = json.load(f)

    STATE.update(
        model=model,
        transform=build_transforms(int(ckpt.get("input_size", 224)), train=False, augment=False),
        device=device,
        idx_to_class={int(v): k for k, v in class_to_idx.items()},
        num_classes=num_classes,
        model_name=ckpt["model_name"],
        zh=zh,
    )


def predict_pil(image):
    with STATE["lock"]:
        tensor = STATE["transform"](image).unsqueeze(0).to(STATE["device"])
        with torch.no_grad():
            logits = STATE["model"](tensor)
            probs = torch.softmax(logits, dim=1)[0]
        k = min(5, STATE["num_classes"])
        scores, indices = probs.topk(k)
    zh = STATE.get("zh") or {}
    top = []
    for s, i in zip(scores.tolist(), indices.tolist()):
        en = STATE["idx_to_class"][int(i)]
        top.append({
            "class_name": en,
            "class_name_zh": zh.get(en, en),
            "label": int(i),
            "score": float(s),
        })
    return {
        "prediction": top[0]["class_name_zh"],
        "prediction_en": top[0]["class_name"],
        "model_name": STATE["model_name"],
        "top_k": top,
        "note": "scores are softmax, not calibrated diagnostic probabilities",
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, INDEX_HTML, "text/html")
        elif self.path == "/health":
            self._send(200, "ok", "text/plain")
        else:
            self._send(404, "not found", "text/plain")

    def do_POST(self):
        if self.path != "/api/predict":
            self._send(404, "not found", "text/plain")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > 25_000_000:
            self._send(400, json.dumps({"error": "invalid content length"}, ensure_ascii=False))
            return
        try:
            payload = json.loads(self.rfile.read(length))
            b64 = payload["image_b64"]
            if b64.strip().startswith("data:"):
                b64 = b64.split(",", 1)[1]
            image = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
            self._send(200, json.dumps(predict_pil(image), ensure_ascii=False))
        except Exception as exc:  # noqa: BLE001
            self._send(400, json.dumps({"error": str(exc)}, ensure_ascii=False))

    def log_message(self, *args):  # quiet
        pass


def main():
    parser = argparse.ArgumentParser(description="LeafGuard local web demo (zero dependency)")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--classes", default="splits/class_to_idx.json")
    parser.add_argument("--zh-map", default="splits/class_to_zh.json")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    checkpoint = Path(args.checkpoint)
    if not checkpoint.is_file():
        raise SystemExit(f"checkpoint not found: {checkpoint}")
    setup(checkpoint, args.classes, args.device, args.zh_map)

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"LeafGuard demo running: http://{args.host}:{args.port}")
    print(f"model: {STATE['model_name']}  device: {STATE['device']}  classes: {STATE['num_classes']}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
