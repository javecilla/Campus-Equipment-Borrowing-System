import { copyFile, mkdir } from "node:fs/promises";

await mkdir("assets/build", { recursive: true });
await copyFile("node_modules/axios/LICENSE", "assets/build/axios-LICENSE.txt");
