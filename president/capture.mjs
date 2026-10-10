// Frame-accurate capture of animated HTML segments with headless Chromium.
// Usage: node capture.mjs jobs.json WORKERS
// jobs.json: [{html, out, frames, fps, artOffset}]  (artOffset in seconds)
// Every CSS animation is paused and seeked per frame; animations inside #art
// (and the #cam move) use the art clock, the rest use the scene clock.
import { readFileSync, existsSync, statSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_CORE || 'playwright-core');
const jobs = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const workers = Number(process.argv[3] || 4);
const exe = process.env.CHROMIUM || '/opt/pw-browsers/chromium';

let next = 0, done = 0;
const todo = jobs.filter(j => !(existsSync(j.out) && statSync(j.out).size > 1000 && existsSync(j.out + '.ok')));

async function worker(id) {
  const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox', '--disable-gpu', '--font-render-hinting=none'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  while (next < todo.length) {
    const job = todo[next++];
    await page.goto('file://' + job.html);
    await page.evaluate(() => document.fonts.ready);
    await page.evaluate(() => {
      window.__anims = document.getAnimations().map(a => {
        a.pause();
        const t = a.effect && a.effect.target;
        const art = !!(t && (t.id === 'cam' || (t.closest && t.closest('#art'))));
        return { a, art };
      });
    });
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(job.fps), '-c:v', 'mjpeg',
      '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', String(job.fps), job.out]);
    const closed = new Promise(r => ff.on('close', r));
    for (let i = 0; i < job.frames; i++) {
      const t = (i / job.fps) * 1000;
      await page.evaluate(([t, off]) => { for (const { a, art } of window.__anims) a.currentTime = art ? t + off : t; }, [t, job.artOffset * 1000]);
      const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
    await closed;
    (await import('node:fs')).writeFileSync(job.out + '.ok', '');
    done++;
    process.stdout.write(`[w${id}] ${done}/${todo.length} ${job.out.split('/').pop()}\n`);
  }
  await browser.close();
}

await Promise.all(Array.from({ length: workers }, (_, i) => worker(i)));
