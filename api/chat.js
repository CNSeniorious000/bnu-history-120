import OpenAI from "openai";

const encoder = new TextEncoder();

/** @param {string} key */
const getEnv = (key) => typeof Netlify !== "undefined" ? Netlify.env.get(key) : process.env[key]

/** @param {Request} request */
export default async (request) => {
  const openai = new OpenAI({ apiKey: request.headers.get("Authorization")?.replace("Bearer ", "") ?? getEnv("OPENAI_API_KEY") ?? "", baseURL: getEnv("OPENAI_API_BASE") });

  /** @type {import("openai/resources/chat/completions").ChatCompletionCreateParamsNonStreaming} */
  const params = await request.json();

  console.log(params);

  const res = await openai.chat.completions.create({
    ...params,
    model: getEnv("OPENAI_CHAT_MODEL") ?? "gpt-3.5-turbo",
    stream: true,
  });

  const stream = new ReadableStream({
    async start(controller) {
      for await (const chunk of res) {
        const delta = chunk.choices[0].delta.content ?? "";
        delta && controller.enqueue(encoder.encode(delta));
      }
      controller.close()
    },
  });


  const headers = new Headers(res?.response?.headers ?? {})  // can't access headers in newer version
  headers.set("content-type", "text/plain")

  return new Response(stream, { headers });
};


/** @type {import("@netlify/edge-functions").Config} */
export const config = { method: "POST", runtime: "edge", path: "/api/chat" };
