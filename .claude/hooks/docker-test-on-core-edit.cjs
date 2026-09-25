#!/usr/bin/env node
// After edits under core/ or gestureos/, remind to run the canonical Docker test
// command (project rule: tests run in Docker, never on host).
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

  const filePath = (payload.tool_input || {}).file_path || "";
  const touchesGuardedPath = /(^|\/)(core|gestureos)\//.test(filePath);
  if (!touchesGuardedPath) {
    return;
  }

  console.log(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PostToolUse",
        additionalContext:
          "This edit touches core/ or gestureos/. Run `make docker-test` " +
          "(Docker-only test rule) before considering the change done.",
      },
    }),
  );
}

main();
