// Fetch the thought-and-word rules index for the coach's prompt. The site keeps
// no copy of its own: the true copy is in faadiallop/foundations, and each build
// and test run takes it from there. A build without the rules stops here.
// measure/coverage.py reads the same address for the conversation tests.

import { mkdir, writeFile } from "node:fs/promises";

const URL_ =
  "https://raw.githubusercontent.com/faadiallop/foundations/main/plugins/thought-and-word/skills/thought-and-word-rules/SKILL.md";
const OUT = new URL("../fetched/thought-and-word-rules.md", import.meta.url);

const res = await fetch(URL_);
if (!res.ok) throw new Error(`could not fetch the rules index: ${res.status} from ${URL_}`);
const text = await res.text();
if (!text.includes("# Thought-and-Word Rules")) throw new Error(`what came from ${URL_} is not the rules index`);
await mkdir(new URL("./", OUT), { recursive: true });
await writeFile(OUT, text);
