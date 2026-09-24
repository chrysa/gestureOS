#!/usr/bin/env node
// Blocks Write/Edit/MultiEdit under core/ that import gestureos (D-0002, DECISIONS.md).
"use strict";

const fs = require("node:fs");

function readStdin() {
  try {
    return fs.readFileSync(0, "utf8");
  } catch {
    return "";
  }
}

function main() {
  let payload;
  try {
    payload = JSON.parse(readStdin());
  } catch {
    return;
  }

  const input = payload.tool_input || {};
  const filePath = input.file_path || "";
  if (!filePath.includes("/core/") && !filePath.startsWith("core/")) {
    return;
  }

  const candidates = [input.content, input.new_string]
    .concat((input.edits || []).map((edit) => edit.new_string))
    .filter(Boolean);

  const violatesBoundary = candidates.some((text) =>
    /(^|\n)\s*(from gestureos|import gestureos)\b/.test(text),
  );

  if (violatesBoundary) {
    console.log(
      JSON.stringify({
        decision: "block",
        reason:
          "core/ must not import gestureos (D-0002, DECISIONS.md): core is modality-agnostic.",
      }),
    );
  }
}

main();
