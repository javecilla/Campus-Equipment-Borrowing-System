import { copyFile, mkdir } from "node:fs/promises";

await mkdir("static/build", { recursive: true });
await copyFile("node_modules/axios/LICENSE", "static/build/axios-LICENSE.txt");
