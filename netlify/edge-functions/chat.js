import OpenAI from "openai";

const encoder = new TextEncoder();

/** @param {Request} request */
export default async (request) => {
  const openai = new OpenAI({ apiKey: request.headers.get("Authorization")?.replace("Bearer ", "") ?? Netlify.env.get("OPENAI_API_KEY") ?? "", baseURL: Netlify.env.get("OPENAI_API_BASE") });

  /** @type {import("openai/resources/chat/completions").ChatCompletionCreateParamsNonStreaming} */
  const params = await request.json();

  console.log(params);

  const res = await openai.chat.completions.create({
    ...params,
    model: Netlify.env.get("OPENAI_CHAT_MODEL") ?? "gpt-3.5-turbo",
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


  const headers = new Headers(res.response.headers)
  headers.set("content-type", "text/plain")

  return new Response(stream, { headers });
};


/** @type {import("@netlify/edge-functions").Config} */
export const config = { method: "POST" };
